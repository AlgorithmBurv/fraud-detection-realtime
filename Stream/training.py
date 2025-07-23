import mlflow
from mlflow.sklearn import log_model
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np

# Membuat eksperimen baru (jika belum ada) dan set eksperimen
experiment_name = "FraudDetectionExperiment"
mlflow.set_experiment(experiment_name)

# Data contoh untuk training (dengan lebih banyak data)
data = pd.DataFrame({
    'user_id': np.arange(10000),  # ID pengguna
    'amount': np.random.uniform(100.0, 5000.0, 10000),  # Random amount antara 100 dan 5000
    'is_fraud': np.random.choice([0, 1], size=10000)  # Label fraud secara acak (0 atau 1)
})

# Tampilkan sebagian dari data untuk memastikan
print(data.head())

# Pisahkan data dan label
X = data[['amount']]
y = data['is_fraud']

# Train model
model = LogisticRegression()
model.fit(X, y)

# Mulai MLflow run dan simpan model ke registry
with mlflow.start_run():
    log_model(model, artifact_path="model", registered_model_name="FraudDetectionModel")
    mlflow.log_param("model_type", "LogisticRegression")
    print("Model sudah disimpan dan didaftarkan ke MLflow")
