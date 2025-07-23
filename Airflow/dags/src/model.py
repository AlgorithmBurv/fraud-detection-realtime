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



mlflow.set_registry_uri("sqlite:///mlflow_registry.db")
# Set MLflow Tracking URI
# mlflow.set_tracking_uri("sqlite:////opt/airflow/mlruns/mlflow.db")
# mlflow.set_tracking_uri("http://mlflow:5000")
# Fungsi untuk training model RandomForest
def train_random_forest(**kwargs):
    df = kwargs['ti'].xcom_pull(task_ids='transform_data')
    df = pd.DataFrame(df) if isinstance(df, list) else df  # Convert list to DataFrame if needed

    X = df.drop(columns=['Prediction'])   # Fitur
    y = df['Prediction']  # Target

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    kwargs['ti'].xcom_push(key='accuracy', value=accuracy)

    if accuracy > 0.8:
        log_model_to_mlflow(model, accuracy)
    
    return accuracy

# Fungsi untuk menyimpan model ke MLflow
def log_model_to_mlflow(model, accuracy):
    experiment_name = "FraudDetectionExperiment"
    mlflow.set_experiment(experiment_name)
    mlflow.start_run(run_name="RandomForest")
    mlflow.sklearn.log_model(model, artifact_path="model", registered_model_name="FraudDetectionModel")
    mlflow.log_metric("accuracy", accuracy)
    mlflow.end_run()

# Fungsi untuk memilih model terbaik berdasarkan akurasi
def choose_best_model(ti):
    accuracy = ti.xcom_pull(task_ids='training_model_A', key='accuracy')
    return 'accurate' if accuracy > 0.8 else 'inaccurate'