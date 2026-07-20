import time
import random
import uuid
import json
import logging
import os
import psutil
import socket
from datetime import datetime
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

# ==========================================
# ESTADO GLOBAL PARA EL DASHBOARD
# ==========================================
class SimulatorState:
    def __init__(self):
        self.start_time = datetime.utcnow()
        self.total_tx = 0
        self.success_tx = 0
        self.biz_fail_tx = 0
        self.tech_fail_tx = 0
        self.last_latency = 0.0
        self.total_latency = 0.0
        self.metrics_sent = 0
        self.last_cw_status = "OK"

state = SimulatorState()

# ==========================================
# CONFIGURACIÓN DE LOGS ESTRUCTURADOS (JSON)
# ==========================================
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage()
        }
        if hasattr(record, 'extra_data'):
            log_record.update(record.extra_data)
        return json.dumps(log_record)

logger = logging.getLogger("SRE_Lab_Logger")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("sre_transactions.log")
file_handler.setFormatter(JSONFormatter())
logger.addHandler(file_handler)

# ==========================================
# INICIALIZACIÓN DE CLIENTE CLOUDWATCH
# ==========================================
session = boto3.Session()
region = session.region_name if session.region_name else "us-east-1"
cw_client = boto3.client("cloudwatch", region_name=region)
CW_NAMESPACE = "SRELab/BusinessAPI"

# ==========================================
# CONFIGURACIÓN DE RUBROS Y PAYLOADS (NEGOCIO)
# ==========================================
def get_banco_payload():
    monto = random.randint(5000, 1500000)
    return {
        "data": {"monto_clp": monto, "cta_destino": f"CTA-{random.randint(1000, 9999)}"},
        "metrics": [
            {"MetricName": "TransferAmountCLP", "Value": monto, "Unit": "None"},
            {"MetricName": "FraudScore", "Value": random.randint(0, 100), "Unit": "None"}
        ]
    }

def get_clinica_payload():
    wait_time_minutes = random.randint(5, 45)
    return {
        "data": {"especialidad": random.choice(["Cardiologia", "Pediatria", "Medicina General"]), "medico_id": f"MED-{random.randint(10, 99)}"},
        "metrics": [
            {"MetricName": "AppointmentsCreated", "Value": 1, "Unit": "Count"},
            {"MetricName": "PatientWaitTime", "Value": wait_time_minutes * 60, "Unit": "Seconds"}, # Corregido a "Seconds" para AWS
            {"MetricName": "DoctorsAvailable", "Value": random.randint(2, 10), "Unit": "Count"}
        ]
    }

def get_fintech_payload():
    vol = round(random.uniform(0.1, 5.0), 4)
    return {
        "data": {"ticker": random.choice(["BTC", "ETH", "AAPL", "TSLA"]), "operacion": random.choice(["BUY", "SELL"]), "cantidad": vol},
        "metrics": [
            {"MetricName": "TradeVolume", "Value": vol, "Unit": "None"},
            {"MetricName": "SettlementTime", "Value": random.randint(100, 500), "Unit": "Milliseconds"}
        ]
    }

def get_ecommerce_payload():
    cart_val = random.randint(15000, 800000)
    items = random.randint(1, 12)
    return {
        "data": {"total_carrito": cart_val, "items_count": items},
        "metrics": [
            {"MetricName": "CartValue", "Value": cart_val, "Unit": "None"},
            {"MetricName": "ItemsPerOrder", "Value": items, "Unit": "Count"}
        ]
    }

def get_contabilidad_payload():
    tax = random.randint(1000, 50000)
    return {
        "data": {"factura_id": f"DTE-{random.randint(10000, 99999)}", "monto_iva": tax},
        "metrics": [
            {"MetricName": "InvoicesProcessed", "Value": 1, "Unit": "Count"},
            {"MetricName": "TaxAmount", "Value": tax, "Unit": "None"}
        ]
    }

SECTORS = {
    "1": {"rubro": "Banco", "endpoints": ["/api/login", "/api/transfer"], "payload_gen": get_banco_payload},
    "2": {"rubro": "Clinica", "endpoints": ["/api/auth", "/api/triage"], "payload_gen": get_clinica_payload},
    "3": {"rubro": "Fintech", "endpoints": ["/api/trade", "/api/settle"], "payload_gen": get_fintech_payload},
    "4": {"rubro": "Ecommerce", "endpoints": ["/api/checkout", "/api/invoice"], "payload_gen": get_ecommerce_payload},
    "5": {"rubro": "Contabilidad", "endpoints": ["/api/ledger", "/api/audit"], "payload_gen": get_contabilidad_payload}
}

# ==========================================
# ENVÍO DE MÉTRICAS A CLOUDWATCH
# ==========================================
def send_to_cloudwatch(metric_data):
    try:
        cw_client.put_metric_data(Namespace=CW_NAMESPACE, MetricData=metric_data)
        state.metrics_sent += len(metric_data)
        state.last_cw_status = "OK"
    except Exception as e:
        state.last_cw_status = "ERROR"
        logger.error(f"Error AWS CloudWatch: {str(e)}")

# ==========================================
# DASHBOARD EN CONSOLA
# ==========================================
def print_dashboard(sector_data):
    os.system('cls' if os.name == 'nt' else 'clear')
    
    uptime = datetime.utcnow() - state.start_time
    minutes = uptime.total_seconds() / 60.0
    req_per_min = int(state.total_tx / minutes) if minutes > 0 else 0
    avg_latency = int(state.total_latency / state.total_tx) if state.total_tx > 0 else 0

    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent

    print("============================================================")
    print("SRE LAB 3.0 - OBSERVABILIDAD EN AWS")
    print(f"Rubro: {sector_data['rubro']}")
    print(f"Tiempo ejecución: {str(uptime).split('.')[0]}")
    print("\nTRANSACCIONES")
    print("------------------------------------------------------------")
    print(f"Total               : {state.total_tx:,}")
    print(f"Exitosas            : {state.success_tx:,}")
    print(f"Business Failures   : {state.biz_fail_tx:,}")
    print(f"Technical Failures  : {state.tech_fail_tx:,}")
    print("\nAPI")
    print("------------------------------------------------------------")
    print(f"Última Latencia     : {int(state.last_latency)} ms")
    print(f"Latencia Promedio   : {avg_latency} ms")
    print(f"Requests/min        : {req_per_min}")
    print("\nINFRAESTRUCTURA")
    print("------------------------------------------------------------")
    print(f"CPU                 : {cpu} %")
    print(f"Memoria             : {memory} %")
    print(f"Disco               : {disk} %")
    print("\nAWS")
    print("------------------------------------------------------------")
    print(f"Métricas enviadas   : {state.metrics_sent:,}")
    print(f"Último envío        : {state.last_cw_status}")
    print("============================================================")

# ==========================================
# SIMULACIÓN DE TRANSACCIONES
# ==========================================
def simulate_transaction(sector_data):
    rubro = sector_data["rubro"]
    endpoint = random.choice(sector_data["endpoints"])
    trx_id = str(uuid.uuid4())
    client_id = f"USR-{random.randint(100000, 999999)}"

    # Latencia
    dice_roll = random.random()
    if dice_roll < 0.80: latency = random.uniform(0.05, 0.30)
    elif dice_roll < 0.95: latency = random.uniform(0.50, 1.50)
    else: latency = random.uniform(2.00, 5.00)

    # Status
    status_roll = random.random()
    if status_roll < 0.03:
        status = random.choice([500, 502, 503])
        log_level, msg, biz_status = "ERROR", "Error interno", "Failed_Technical"
        state.tech_fail_tx += 1
    elif status_roll < 0.15:
        status = random.choice([400, 401, 403, 404])
        log_level, msg, biz_status = "WARNING", "Rechazo de negocio", "Failed_Business_Rule"
        state.biz_fail_tx += 1
    else:
        status = random.choice([200, 201])
        log_level, msg, biz_status = "INFO", "Transaccion exitosa", "Success"
        state.success_tx += 1

    # Actualizar estado API
    state.total_tx += 1
    state.last_latency = latency * 1000
    state.total_latency += state.last_latency

    payload_obj = sector_data["payload_gen"]()
    biz_payload = payload_obj["data"]
    biz_metrics = payload_obj["metrics"]

    # Logs
    log_context = {
        "extra_data": {
            "trx_id": trx_id, "client_id": client_id, "rubro": rubro,
            "endpoint": endpoint, "status_code": status, "duration_ms": round(state.last_latency, 2),
            "business_data": biz_payload
        }
    }
    if log_level == "INFO": logger.info(msg, extra=log_context)
    elif log_level == "WARNING": logger.warning(msg, extra=log_context)
    else: logger.error(msg, extra=log_context)

    # ================= Métrica Base (API) =================
    base_dims = [{"Name": "Rubro", "Value": rubro}, {"Name": "Endpoint", "Value": endpoint}]
    
    # Arreglado: Set de dimensiones específico para contar requests mapeados por código HTTP status
    requests_dims = [
        {"Name": "Rubro", "Value": rubro},
        {"Name": "Endpoint", "Value": endpoint},
        {"Name": "StatusCode", "Value": str(status)}
    ]

    metric_data = [
        {"MetricName": "ApiLatency", "Dimensions": base_dims, "Value": state.last_latency, "Unit": "Milliseconds"},
        {"MetricName": "ApiRequests", "Dimensions": requests_dims, "Value": 1, "Unit": "Count"},
        {"MetricName": "ApiAvailability", "Dimensions": base_dims, "Value": 100 if status < 400 else 0, "Unit": "Percent"},
        {"MetricName": "ApiErrors", "Dimensions": base_dims, "Value": 1 if status >= 400 else 0, "Unit": "Count"},
        {"MetricName": "RequestSizeBytes", "Dimensions": base_dims, "Value": random.randint(512, 8192), "Unit": "Bytes"},
        {"MetricName": "ResponseSizeBytes", "Dimensions": base_dims, "Value": random.randint(1024, 16384), "Unit": "Bytes"}
    ]

    # ================= Métrica Infra =================
    server_name = socket.gethostname()
    process = psutil.Process()
    process_name = process.name()

    server_dimensions = [
        {"Name": "ServerName", "Value": server_name}
    ]
    
    process_dimensions = [
        {"Name": "ServerName", "Value": server_name},
        {"Name": "ProcessName", "Value": process_name}
    ]

    metric_data.extend([
        {"MetricName": "CPUUtilization", "Dimensions": server_dimensions, "Value": psutil.cpu_percent(), "Unit": "Percent"},
        {"MetricName": "MemoryUtilization", "Dimensions": server_dimensions, "Value": psutil.virtual_memory().percent, "Unit": "Percent"},
        {"MetricName": "DiskUtilization", "Dimensions": server_dimensions, "Value": psutil.disk_usage("/").percent, "Unit": "Percent"},
        {"MetricName": "ProcessMemoryMB", "Dimensions": process_dimensions, "Value": process.memory_info().rss / 1024 / 1024, "Unit": "Megabytes"}
    ])

    # ================= Métrica Negocio =================
    for bm in biz_metrics:
        bm["Dimensions"] = [{"Name": "Rubro", "Value": rubro}]
        metric_data.append(bm)

    send_to_cloudwatch(metric_data)
    print_dashboard(sector_data)

# ==========================================
# MAIN
# ==========================================
def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=== SRE LAB 3.0: AWS CLOUDWATCH & STRUCTURED LOGGING ===")
    
    for key, val in SECTORS.items():
        print(f"[{key}] {val['rubro']}")

    choice = input("\nSelecciona el rubro (1-5): ").strip()
    if choice not in SECTORS:
        print("Opción inválida.")
        return

    sector_data = SECTORS[choice]

    try:
        while True:
            simulate_transaction(sector_data)
            time.sleep(random.uniform(0.2, 0.5))

    except KeyboardInterrupt:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n[!] Simulador detenido por el usuario.")
        print(f"Total Transacciones: {state.total_tx} | Métricas Enviadas: {state.metrics_sent}\n")

if __name__ == "__main__":
    main()