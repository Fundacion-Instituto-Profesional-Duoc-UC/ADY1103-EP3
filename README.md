# 🚀 Evaluación Parcial 3 (EP3)

## Observabilidad y Trazabilidad en la Nube

---

## 📖 Descripción

En esta tercera evaluación asumirás nuevamente el rol de **Consultor SRE (Site Reliability Engineer)** para dar continuidad a la estrategia de observabilidad de la empresa ficticia desarrollada durante el semestre.

En esta oportunidad, la observabilidad migrará hacia un entorno **Cloud Native en AWS**, utilizando servicios administrados para el monitoreo, almacenamiento de métricas y análisis de registros.

Se proporcionará una aplicación desarrollada en Python que simulará un proceso crítico del negocio y realizará dos funciones principales:

* Generar métricas personalizadas hacia AWS CloudWatch.
* Generar registros operacionales (*logs*) para su posterior análisis.

Tu objetivo será implementar una solución de observabilidad que permita centralizar métricas y registros, construir dashboards operativos y asegurar la trazabilidad de los eventos más relevantes del sistema.

---

## 🎯 Objetivos de la Evaluación

Al finalizar esta actividad serás capaz de:

* Utilizar AWS CloudWatch como plataforma de monitoreo.
* Analizar métricas personalizadas generadas por aplicaciones.
* Gestionar y consultar registros operacionales.
* Construir dashboards de observabilidad en AWS.
* Correlacionar eventos técnicos con indicadores de negocio.
* Implementar mecanismos básicos de trazabilidad operacional.

---

## 📑 Contenido

* [Prerrequisitos](#-prerrequisitos)
* [Configuración del Entorno](#️-configuración-del-entorno)
* [Ejecución del Simulador](#-ejecución-del-simulador)
* [Arquitectura de Observabilidad](#-arquitectura-de-observabilidad)
* [Métricas y Logs Generados](#-métricas-y-logs-generados)
* [Limpieza del Entorno AWS](#-limpieza-del-entorno-aws)

---

# 📋 Prerrequisitos

Antes de comenzar, verifica que dispones de:

| Requisito                      | Versión                             |
| ------------------------------ | ----------------------------------- |
| Sistema Operativo              | Linux (Ubuntu o Debian recomendado) |
| Python                         | 3.10 o superior                     |
| AWS CLI                        | Última versión estable              |
| Git                            | Última versión estable              |
| Cuenta AWS Academy Learner Lab | Activa                              |


### ☁️ Requisitos AWS

Para que la aplicación pueda enviar métricas personalizadas a AWS CloudWatch, la instancia EC2 utilizada debe contar con un perfil de instancia (IAM Role) asociado.

> ⚠️ **Importante:** Si el rol no está configurado correctamente, las métricas no podrán ser publicadas en CloudWatch.

Verifica tu instalación:

```bash
python3 --version
aws --version
git --version
```

---

# ⚙️ Configuración del Entorno

## 1️⃣ Clonar el repositorio

```bash
git clone https://github.com/Fco-Quiroga/ADY1103-Monitoreo-Observabilidad.git

cd ADY1103-Monitoreo-Observabilidad/06_Ev_Parcial_3-Observabilidad_Nube
```

---

## 2️⃣ Crear y activar el entorno virtual

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 3️⃣ Instalar dependencias

```bash
pip install --upgrade pip

pip install -r requirements.txt
```

---

## 4️⃣ Configurar credenciales AWS

Verifica que tu entorno posea credenciales válidas para interactuar con AWS.

```bash
aws sts get-caller-identity
```

Si la configuración es correcta, AWS devolverá la información de la cuenta asociada al laboratorio.

---

## 5️⃣ Ejecutar el simulador

```bash
python3 app.py
```

---

# 🎮 Ejecución del Simulador

Al iniciar la aplicación:

1. Se comenzarán a generar eventos de negocio simulados.
2. Se enviarán métricas personalizadas a AWS CloudWatch.
3. Se generarán registros operacionales locales.
4. Los datos podrán ser posteriormente consultados desde la consola de AWS.

Mantén la aplicación ejecutándose durante toda la actividad para permitir la generación continua de telemetría.

---

## ⏳ Acumulación de Métricas para las Evidencias

> ⚠️ **Importante:** Una vez iniciado el simulador, debes dejarlo ejecutándose durante un período suficiente para que **AWS CloudWatch** pueda procesar los datos históricos y tus dashboards dispongan de información representativa para visualizar.

Antes de capturar las evidencias finales, asegúrate de contar con **al menos 30 minutos de métricas continuas** almacenadas y visibles en CloudWatch.

---

# ☁️ Arquitectura de Observabilidad

La arquitectura utilizada en esta evaluación contempla los siguientes componentes:

```text
Aplicación Python
        │
        ├── Métricas Personalizadas
        │
        ▼
 AWS CloudWatch Metrics
        │
        ▼
 CloudWatch Dashboard

        ───────────────────

 Aplicación Python
        │
        ├── Logs Operacionales
        │
        ▼
 CloudWatch Logs
        │
        ▼
 Log Insights
```

El objetivo es construir una visión integrada que permita analizar tanto el comportamiento técnico del sistema como el impacto sobre el negocio.

---

# 📊 Métricas y Logs Generados

La aplicación genera telemetría avanzada estructurada en tres capas de observabilidad. Todas las métricas son enviadas automáticamente a AWS CloudWatch bajo el Namespace **`SRELab/BusinessAPI`**.

## 📈 Métricas de CloudWatch

### 1. Capa de Infraestructura
Métricas asociadas a la salud del servidor y del proceso, etiquetadas con las dimensiones `ServerName` y `ProcessName`:
* **`CPUUtilization` (%)**: Porcentaje de uso de la CPU del servidor.
* **`MemoryUtilization` (%)**: Consumo de memoria RAM del servidor.
* **`DiskUtilization` (%)**: Espacio utilizado en el disco raíz.
* **`ProcessMemoryMB` (MB)**: Memoria específica consumida por el proceso de Python.

### 2. Capa de Aplicación (API)
Indicadores de rendimiento de los endpoints HTTP, etiquetados con las dimensiones `Rubro`, `Endpoint` y `StatusCode`:
* **`ApiLatency` (ms)**: Tiempo de respuesta del servidor simulado.
* **`ApiRequests` (Count)**: Volumen de peticiones entrantes (Throughput).
* **`ApiAvailability` (%)**: Disponibilidad del servicio (100% para 2xx, 0% para 4xx/5xx).
* **`ApiErrors` (Count)**: Tasa de errores HTTP (Status >= 400).
* **`RequestSizeBytes` / `ResponseSizeBytes` (Bytes)**: Tamaño de los payloads simulados.

### 3. Capa de Negocio (Por Rubro)
Métricas transaccionales específicas que reflejan el estado del negocio:
* **🏦 Banco:** `TransferAmountCLP` (Monto), `FraudScore` (0-100).
* **🏥 Clínica:** `AppointmentsCreated` (Citas), `PatientWaitTime` (Segundos), `DoctorsAvailable`.
* **💳 Fintech:** `TradeVolume` (Volumen de compra/venta), `SettlementTime` (ms).
* **🛒 Ecommerce:** `CartValue` (Valor de ventas), `ItemsPerOrder` (Artículos).
* **🧾 Contabilidad:** `InvoicesProcessed` (Facturas), `TaxAmount` (IVA retenido).

---

## 📝 Logs Operacionales (Estructurados)

La aplicación ya no genera logs de texto plano. Todos los eventos se escriben en el archivo `sre_transactions.log` utilizando formato **JSON Estructurado**, lo que permite:

* Ingesta nativa mediante el **Amazon CloudWatch Agent**.
* Consultas avanzadas usando **CloudWatch Logs Insights**.
* Correlación exacta mediante `trx_id` (ID de transacción) y `client_id`.

**Ejemplo de un Log Generado:**
```json
{
  "timestamp": "2023-10-25T14:32:01.123Z",
  "level": "INFO",
  "message": "Transaccion exitosa",
  "trx_id": "c8a4f6e1-9b2d...",
  "client_id": "USR-481516",
  "rubro": "Ecommerce",
  "endpoint": "/api/checkout",
  "status_code": 200,
  "duration_ms": 125.4,
  "business_data": {
    "total_carrito": 45000,
    "items_count": 3
  }
}

---

# 🧹 Limpieza del Entorno AWS

> ⚠️ Importante: Una vez obtenidas todas las evidencias, elimina los recursos utilizados para evitar el consumo innecesario de créditos en AWS Academy Learner Lab.

## Paso 1: Detener la aplicación

Finaliza la ejecución del simulador:

```bash
CTRL + C
```

---

## Paso 2: Verificar recursos utilizados

Revisa que no existan recursos adicionales ejecutándose en AWS que hayan sido creados durante la actividad.

Ejemplos:

* Instancias EC2.
* Dashboards temporales.
* Log Groups de prueba.
* Alarmas de prueba.

---

## Paso 3: Terminar la instancia EC2

1. Accede al servicio EC2.
2. Selecciona la instancia utilizada.
3. Haz clic en:

```text
Instance State → Terminate Instance
```

4. Confirma la acción.

---

## Paso 4: Finalizar el Learner Lab

1. Regresa a AWS Academy.
2. Haz clic en:

```text
End Lab
```

3. Espera la confirmación de cierre.

---

> ✅ Completar estos pasos garantiza que no continúe el consumo de créditos asociados al laboratorio.

---

## 👨‍💻 Autor

**ADY1103 - Monitoreo y Observabilidad**

Evaluación Parcial 3 — Observabilidad y Trazabilidad en la Nube.