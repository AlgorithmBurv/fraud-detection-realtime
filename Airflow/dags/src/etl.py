from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import ipaddress
from sklearn.preprocessing import LabelEncoder


def serialize_xcom_value(value):
    """
    Fungsi untuk mengonversi objek Timestamp menjadi string
    agar dapat diserialisasi oleh JSON.
    """
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')  # Mengonversi Timestamp ke string
    return value

def extract_data():
    # Path ke file kredensial JSON
    credentials_path = '/opt/airflow/dags/bigquery-33633-a1f67260d745.json'  # Ganti dengan path file kredensial Anda

    # Ganti dengan ID proyek Google Cloud Anda
    project_id = "bigquery-33633"    

    # Kueri SQL untuk mengambil data dari BigQuery
    query = """
        SELECT *
        FROM `bigquery-33633.fraudDataset.fraudTransaction`
        LIMIT 1000
    """

    # Muat kredensial dengan google-auth
    credentials = service_account.Credentials.from_service_account_file(credentials_path)

    # Mengambil data dari BigQuery dan mengonversinya menjadi DataFrame
    df = pd.read_gbq(query, project_id=project_id, credentials=credentials)

    # Mengonversi setiap nilai dalam DataFrame yang bertipe Timestamp menjadi string
    df = df.applymap(serialize_xcom_value)

    # Mengubah DataFrame menjadi dictionary
    return df.to_dict(orient='records')


def ip_to_float(ip):
    """
    Fungsi untuk mengonversi IP Address ke dalam format float.
    """
    return float(int(ipaddress.IPv4Address(ip)))

def transform_data(**kwargs):
    # Mengambil data dari XCom
    df = kwargs['ti'].xcom_pull(task_ids='extract_data')
    
    # Mengonversi list ke DataFrame jika perlu
    df = pd.DataFrame(df) if isinstance(df, list) else df  

    # Menghapus kolom yang tidak diperlukan
    df.drop(columns=['TransactionID', 'AccountID', 'DeviceID', 'MerchantID'], inplace=True)

    # Mengonversi kolom tanggal ke datetime dan kemudian ke integer (epoch time)
    df['TransactionDate'] = pd.to_datetime(df['TransactionDate'])
    df['PreviousTransactionDate'] = pd.to_datetime(df['PreviousTransactionDate'])
    
    # Mengonversi tanggal ke format timestamp dalam detik (epoch)
    df['TransactionDate'] = df['TransactionDate'].astype('int64') // 10**9
    df['PreviousTransactionDate'] = df['PreviousTransactionDate'].astype('int64') // 10**9

    # Mengonversi IP Address ke float
    df['IP Address'] = df['IP Address'].apply(ip_to_float)
    
    # Melakukan Label Encoding untuk beberapa kolom
    label_encoder = LabelEncoder()

    # Label Encoding untuk kolom-kolom kategori
    df['TransactionType'] = label_encoder.fit_transform(df['TransactionType'])
    df['Location'] = label_encoder.fit_transform(df['Location'])
    df['Channel'] = label_encoder.fit_transform(df['Channel'])
    df['CustomerOccupation'] = label_encoder.fit_transform(df['CustomerOccupation'])

    # Menghapus missing values
    df.dropna(inplace=True)

    # Memilih kolom yang diperlukan (TransactionAmount dan IsFraud)
    # df = df[['TransactionAmount', 'IsFraud']]

    # Mengembalikan data dalam format list of dictionaries
    return df.to_dict(orient='records')


# Fungsi untuk load data (debugging purposes)
def load_data(**kwargs):
    transformed_data = kwargs['ti'].xcom_pull(task_ids='transform_data')
    print(f"Data yang diterima untuk load: {transformed_data}")
    return "Data Loaded Successfully"