from confluent_kafka import Producer
import json
import time
import pandas as pd

# Inisialisasi Kafka producer
producer = Producer({'bootstrap.servers': 'localhost:9092'})

def delivery_callback(err, msg):
    if err:
        print(f"[ERROR] Failed to send message: {err}")
    else:
        print(f"[PRODUCER] Message sent to: {msg.topic()} [partition {msg.partition()}] offset {msg.offset()}")

# Membaca data dari file CSV
csv_file_path = './Dataset/testingSingapore.csv'  # Ganti dengan path file CSV kamu
df = pd.read_csv(csv_file_path)

# Fungsi untuk mengirim data dari baris CSV ke Kafka
def send_data_from_csv(row):
    # Mengonversi baris ke dictionary
    data = {
        "TransactionID": row["TransactionID"],
        "AccountID": row["AccountID"],
        "TransactionAmount": row["TransactionAmount"],
        "TransactionDate": row["TransactionDate"],
        "TransactionType": row["TransactionType"],
        "Location": row["Location"],
        "Latitude": row["Latitude"],
        "Longitude": row["Longitude"],
        "DeviceID": row["DeviceID"],
        "IP Address": row["IP Address"],
        "MerchantID": row["MerchantID"],
        "Channel": row["Channel"],
        "CustomerAge": row["CustomerAge"],
        "CustomerOccupation": row["CustomerOccupation"],
        "TransactionDuration": row["TransactionDuration"],
        "LoginAttempts": row["LoginAttempts"],
        "AccountBalance": row["AccountBalance"],
        "PreviousTransactionDate": row["PreviousTransactionDate"]
    }
    
    return data

try:
    # Iterasi setiap baris data dalam CSV
    for _, row in df.iterrows():
        data = send_data_from_csv(row)  # Mengambil data dari baris CSV
        value_json = json.dumps(data)  # Mengonversi data ke format JSON
        producer.produce(
            topic="fraud-transactions",
            key=str(data["TransactionID"]),  # Menggunakan TransactionID sebagai key
            value=value_json,
            callback=delivery_callback
        )
        producer.poll(0)  # Memanggil producer untuk mengecek event
        print(f"[PRODUCER] Sending data: {value_json} \n")
        time.sleep(1)  # Memberikan jeda 1 detik antar pengiriman pesan

except KeyboardInterrupt:
    producer.flush()  # Memastikan semua pesan terkirim sebelum berhenti
print("Producer stopped by user")

