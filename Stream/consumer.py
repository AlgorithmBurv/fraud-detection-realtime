import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType
import mlflow.sklearn
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from pandas_gbq import to_gbq
import ipaddress
from sklearn.preprocessing import LabelEncoder

# Path ke file kredensial JSON
credentials_path = "bigquery-33633-a1f67260d745.json"

# Muat kredensial dengan google-auth
credentials = service_account.Credentials.from_service_account_file(credentials_path)

# Inisialisasi Spark session
spark = SparkSession.builder.appName("KafkaSparkMLflowStreaming").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# Schema data JSON Kafka
schema = StructType([
    StructField("TransactionID", StringType(), True),
    StructField("AccountID", StringType(), True),
    StructField("TransactionAmount", IntegerType(), True),
    StructField("TransactionDate", StringType(), True),
    StructField("TransactionType", StringType(), True),
    StructField("Location", StringType(), True),
    StructField("Latitude", FloatType(), True),         
    StructField("Longitude", FloatType(), True),
    StructField("DeviceID", StringType(), True),
    StructField("IP Address", StringType(), True),       
    StructField("MerchantID", StringType(), True),
    StructField("Channel", StringType(), True),
    StructField("CustomerAge", IntegerType(), True),
    StructField("CustomerOccupation", StringType(), True),
    StructField("TransactionDuration", IntegerType(), True),
    StructField("LoginAttempts", IntegerType(), True),
    StructField("AccountBalance", IntegerType(), True),
    StructField("PreviousTransactionDate", StringType(), True)
])

# Baca streaming dari Kafka
df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "fraud-transactions") \
    .option("startingOffsets", "earliest") \
    .load()

# Extract value string dan parse JSON sesuai schema
json_df = df.selectExpr("CAST(value AS STRING) as json_str")
parsed_df = json_df.select(from_json(col("json_str"), schema).alias("data")).select("data.*")

# Buang baris yang ada null di kolom
clean_df = parsed_df.na.drop(subset=[
    "`TransactionID`", "`AccountID`", "`TransactionAmount`", "`TransactionDate`", 
    "`TransactionType`", "`Location`", "`Latitude`", "`Longitude`", 
    "`DeviceID`", "`IP Address`", "`MerchantID`", "`Channel`", 
    "`CustomerAge`", "`CustomerOccupation`", "`TransactionDuration`", 
    "`LoginAttempts`", "`AccountBalance`", "`PreviousTransactionDate`"
])

# Load model scikit-learn dari MLflow Model Registry
model_uri = "models:/FraudDetectionModel/Production"
model = mlflow.sklearn.load_model(model_uri)

# Fungsi untuk mengirimkan email
def send_email(subject, body, to_email):
    from_email = "alertalert948@gmail.com"
    from_password = "suvb daeo jrug kale"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))  # Menggunakan MIMEText dengan format HTML

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(from_email, from_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print(f"[NOTIFICATION] Email alert sent successfully to {to_email} \n")
    except Exception as e:
        print(f"[NOTIFICATION] Failed to send email to {to_email}. Error: {e} \n")

# Fungsi untuk menyimpan hasil ke BigQuery
def save_to_bigquery(df):
    project_id = "bigquery-33633"  
    dataset_table = "fraudDataset.fraudTransaction"  

    try:
        to_gbq(df, dataset_table, project_id=project_id, if_exists='append', credentials=credentials)
        print(f"Data successfully sent to BigQuery: {dataset_table}")
    except Exception as e:
        print(f"Failed to save to BigQuery: {e}")

# Fungsi untuk memproses setiap baris data
def process_row(row):
    # Convert tipe data dan lakukan transformasi untuk setiap row
    row_df = pd.DataFrame([row.asDict()])  # Convert row ke DataFrame Pandas untuk pemrosesan lebih lanjut

    # Convert dates to timestamp and apply encoding
    row_df['TransactionDate'] = pd.to_datetime(row_df['TransactionDate'])
    row_df['PreviousTransactionDate'] = pd.to_datetime(row_df['PreviousTransactionDate'])
    row_df['TransactionDate'] = row_df['TransactionDate'].astype('int64') // 10**9
    row_df['PreviousTransactionDate'] = row_df['PreviousTransactionDate'].astype('int64') // 10**9

    # IP address conversion
    def ip_to_float(ip):
        return float(int(ipaddress.IPv4Address(ip)))
    
    row_df['IP Address'] = row_df['IP Address'].apply(ip_to_float)

    # Label Encoding and prediction
    label_encoder = LabelEncoder()
    row_df['TransactionType'] = label_encoder.fit_transform(row_df['TransactionType'])
    row_df['Location'] = label_encoder.fit_transform(row_df['Location'])
    row_df['Channel'] = label_encoder.fit_transform(row_df['Channel'])
    row_df['CustomerOccupation'] = label_encoder.fit_transform(row_df['CustomerOccupation'])

    predictions = model.predict(row_df[[
        "TransactionAmount", "TransactionDate", "TransactionType", "Location", "Latitude", 
        "Longitude", "IP Address", "Channel", "CustomerAge", "CustomerOccupation", 
        "TransactionDuration", "LoginAttempts", "AccountBalance", "PreviousTransactionDate"
    ]])

    # Add predictions to dataframe
    row_df['Prediction'] = predictions

    # Convert dates back to datetime
    row_df['TransactionDate'] = pd.to_datetime(row_df['TransactionDate'], unit='s')
    row_df['PreviousTransactionDate'] = pd.to_datetime(row_df['PreviousTransactionDate'], unit='s')

    def float_to_ip(float_ip):
        return str(ipaddress.IPv4Address(int(float_ip)))
    
    row_df['IP Address'] = row_df['IP Address'].apply(float_to_ip)
        # Mengganti nilai pada kolom dengan menggunakan mapping
    transaction_type_mapping = {0: 'Cash-In', 1: 'Cash-Out'}
    channel_mapping = {0: 'ATM', 1: 'Branch', 2: 'Mobile'}
    location_mapping = {
        0: 'Central Singapore',
        1: 'East Singapore',
        2: 'North East Singapore',
        3: 'North West Singapore',
        4: 'West Singapore'
    }
    occupation_mapping = {
        0: 'Banker',
        1: 'Healthcare Worker',
        2: 'Retail Worker',
        3: 'Software Engineer',
        4: 'Teacher'
    }

    row_df['TransactionType'] = row_df['TransactionType'].map(transaction_type_mapping)
    row_df['Channel'] = row_df['Channel'].map(channel_mapping)
    row_df['Location'] = row_df['Location'].map(location_mapping)
    row_df['CustomerOccupation'] = row_df['CustomerOccupation'].map(occupation_mapping)

    # Check for fraud detection
    if row_df['Prediction'].iloc[0] == 1:  # Fraud detected
        print("[NOTIFICATION] Transaction Status: Fraud ")

        
        # Membuat body email yang lebih terstruktur dan rapi dalam HTML
        fraud_details_str = f"""
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr><td style="font-weight: bold;">Transaction ID:</td><td>{row_df['TransactionID'].iloc[0]}</td></tr>
            <tr><td style="font-weight: bold;">Account ID:</td><td>{row_df['AccountID'].iloc[0]}</td></tr>
            <tr><td style="font-weight: bold;">Amount:</td><td>${row_df['TransactionAmount'].iloc[0]}</td></tr>
            <tr><td style="font-weight: bold;">Date:</td><td>{row_df['TransactionDate'].iloc[0]}</td></tr>
            <tr><td style="font-weight: bold;">Type:</td><td>{row_df['TransactionType'].iloc[0]}</td></tr>
            <tr><td style="font-weight: bold;">Location:</td><td>{row_df['Location'].iloc[0]}</td></tr>
            <tr><td style="font-weight: bold;">Latitude:</td><td>{row_df['Latitude'].iloc[0]}</td></tr>
            <tr><td style="font-weight: bold;">Longitude:</td><td>{row_df['Longitude'].iloc[0]}</td></tr>
            <tr><td style="font-weight: bold;">Device ID:</td><td>{row_df['DeviceID'].iloc[0]}</td></tr>
            <tr><td style="font-weight: bold;">IP Address:</td><td>{row_df['IP Address'].iloc[0]}</td></tr>
            <tr><td style="font-weight: bold;">Merchant ID:</td><td>{row_df['MerchantID'].iloc[0]}</td></tr>
            <tr><td style="font-weight: bold;">Channel:</td><td>{row_df['Channel'].iloc[0]}</td></tr>
        </table>
        """


        subject = "⚠️ Suspicious Transaction Detected - Immediate Review Required"
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2 style="color: #d9534f;">⚠️ Suspicious Transaction Detected</h2>
                <p style="font-size: 16px;">Dear Team,</p>
                <p style="font-size: 16px;">A potentially fraudulent transaction has been identified. Kindly review the following details and take the appropriate action:</p>

                <hr style="border: 1px solid #d9534f;">

                <h3 style="color: #5bc0de;">Transaction Details:</h3>
                {fraud_details_str}

                <p style="font-size: 16px;">Please take immediate action to investigate this matter.</p>

                <p style="font-size: 14px; color: #777;">Best regards,</p>
                <p style="font-size: 14px; color: #777;">Your Fraud Detection System</p>
            </body>
        </html>
        """
        to_email = "groupberitaacara@gmail.com"
        send_email(subject, body, to_email)
    else:
        print("[NOTIFICATION] Transaction Status: Normal \n")

# Gantikan foreachBatch dengan foreach untuk memproses setiap row
query = clean_df.writeStream \
    .foreach(process_row) \
    .outputMode("append") \
    .start()

query.awaitTermination()
