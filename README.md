# Multi-Cloud Hybrid Backup Strategy for Supply Chain

## Project Description
This project simulates a hybrid, multi-cloud backup system used by supply chain companies to protect critical logistics files such as inventory reports, shipment data, supplier records, and warehouse documents. The system demonstrates:
- Redundancy
- Failover
- Hybrid cloud storage
- Multi-cloud backup strategy (simulated with local + AWS S3)

## Architecture Diagram
```
+-----------------------+         +----------------------+
|   Dataset (Local)     |  ---->  |   Local Backup Store  |
|  inventory.csv, etc.  |         |  backup/local_backup  |
+-----------------------+         +----------------------+
            |                                |
            | (if local fails)               | (redundancy)
            v                                v
+-----------------------+         +----------------------+
|   AWS S3 Bucket       |  <----  |  Cloud Backup Module |
|  supply-chain-backups |         |  boto3 uploader      |
+-----------------------+         +----------------------+
```

## How to Run
1. Install dependencies:
```
pip install -r requirements.txt
```
2. Set AWS credentials (example):
```
setx AWS_ACCESS_KEY_ID "your_key"
setx AWS_SECRET_ACCESS_KEY "your_secret"
setx AWS_DEFAULT_REGION "us-east-1"
```
3. Run the Streamlit dashboard:
```
streamlit run frontend/dashboard.py
```
4. Open in browser:
```
http://localhost:8501
```

## Notes on Sample Dataset
- `dataset/warehouse_stock.xlsx` is a lightweight CSV-formatted placeholder with an `.xlsx` extension for demo portability.
- If you need a strict Excel `.xlsx`, replace it with a true Excel file or generate one using pandas with `openpyxl` installed.

## Git Setup Instructions
```
git init
git add .
git commit -m "Initial commit: multi-cloud backup demo"
```

## Project Structure
```
multi-cloud-backup
├── frontend
│   └── dashboard.py
├── backend
│   ├── backup_manager.py
│   ├── local_backup.py
│   ├── cloud_backup.py
│   ├── failover_handler.py
│   ├── logger.py
│   └── performance_monitor.py
├── dataset
│   └── sample supply chain files
├── backup
│   └── local_backup
├── logs
│   └── backup_logs.txt
├── requirements.txt
└── README.md
```
