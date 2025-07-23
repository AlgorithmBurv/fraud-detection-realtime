import mlflow
import mlflow.sklearn
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import ipaddress
from sklearn.preprocessing import LabelEncoder

from src.etl import serialize_xcom_value
from src.etl import ip_to_float
from src.etl import extract_data
from src.etl import transform_data
from src.etl import load_data

from src.model import train_random_forest
from src.model import choose_best_model
from src.model import log_model_to_mlflow





# Definisikan DAG
with DAG("my_dag", start_date=datetime(2022, 11, 11),
         schedule_interval="@daily", catchup=False) as dag:

    # Task untuk ekstraksi data
    extract_task = PythonOperator(
        task_id="extract_data",
        python_callable=extract_data
    )

    # Task untuk transformasi data
    transform_task = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data
    )

    # Task untuk load data
    load_task = PythonOperator(
        task_id="load_data",
        python_callable=load_data
    )

    # Task untuk melatih model (Random Forest)
    training_model_A = PythonOperator(
        task_id="training_model_A",
        python_callable=train_random_forest
    )

    # Task untuk memilih model terbaik berdasarkan akurasi
    choose_best_model = BranchPythonOperator(
        task_id="choose_best_model",
        python_callable=choose_best_model
    )

    # Task jika model akurat
    accurate = BashOperator(
        task_id="accurate",
        bash_command="echo 'Model has been uploaded to MLflow'"
    )

    # Task jika model tidak akurat
    inaccurate = BashOperator(
        task_id="inaccurate",
        bash_command="echo 'Retraining is required'"
    )

    # Menentukan urutan tugas ETL dan model training
    extract_task >> transform_task >> load_task >> training_model_A >> choose_best_model >> [accurate, inaccurate]
