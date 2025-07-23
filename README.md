# 🛡️ Real-Time Fraud Detection System

<img src="./Fraud Architecture.png" alt="Fraud Detection Architecture" width="800"/>

## 📖 Overview

This project is a **real-time fraud detection system** built using a modern data pipeline architecture. It integrates multiple tools for **data ingestion**, **processing**, **modeling**, and **analysis**, orchestrated with Docker and Apache Airflow.

---

## 🧱 System Components

### 🏦 System Fraud Layer
- **Bank System**: Simulated transaction data source.
- **Kafka**: Real-time streaming platform to capture and forward transaction data.
- **Apache Spark**: Performs real-time processing and scoring of streaming data.
- **Gmail API**: Sends alert notifications when fraudulent activity is detected.

---

### 🧠 Modeling Layer
- **MLflow**: Used for model tracking, versioning, and experiment logging.
- **Training Service**: Responsible for training fraud detection models.
- **MinIO**: Object storage to save trained models (S3 compatible).
- **PostgreSQL**: Stores structured training data and metadata.

---

### ⚙️ Orchestration Layer
- **Apache Airflow**: Manages DAGs for ETL, training, and monitoring pipelines.
- **PostgreSQL**: Backend metadata database for Airflow.
- **Celery + Redis**: Used for distributed task queuing and execution in Airflow.

---

### 📊 Analysis Layer
- **Google BigQuery**: Centralized data warehouse for transaction logs and model results.
- **Power BI**: Business Intelligence dashboard for fraud trend analysis and reporting.

---

## 🐳 Dockerized Services

All services are containerized with Docker for reproducibility and scalability:
- `airflow-webserver`, `airflow-scheduler`, `airflow-worker`
- `mlflow-server`
- `kafka`, `zookeeper`
- `postgres`, `redis`, `minio`
- `spark`, `bigquery-connector`

---

## 🔄 Data Flow Summary

1. Simulated transactions are sent to **Kafka**.
2. **Spark** consumes the stream, processes it, and applies the fraud detection model.
3. Detected frauds trigger email alerts and are logged into **BigQuery**.
4. **Airflow** orchestrates batch jobs like retraining models or data ingestion.
5. **MLflow** tracks experiment metadata and trained model performance.
6. **Power BI** visualizes fraud statistics via BigQuery integration.

---

## 🚀 Getting Started

```bash
# Clone repository
git clone https://github.com/your-username/fraud-detection-realtime.git
cd fraud-detection-realtime

# Start the system
docker-compose up --build
```

> Ensure `.env` and credential files are properly configured (see `.env.example`).

---

## ⚠️ Security Note

🚫 **Do not commit** cloud credentials (e.g. GCP, AWS, service account `.json`) to this repository.



