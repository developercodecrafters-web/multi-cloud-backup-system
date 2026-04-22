# Multi-Cloud Hybrid Backup Strategy for Supply Chain

## Project Description
This project simulates a hybrid, multi-cloud backup system used by supply chain companies to protect critical logistics files such as inventory reports, shipment data, supplier records, and warehouse documents.

The system demonstrates:
- Redundancy
- Failover
- Hybrid cloud storage
- Multi-cloud backup strategy (local + selectable cloud provider)

## Architecture Diagram
```
+-----------------------+         +----------------------+
|   Dataset (Local)     |  ---->  |   Local Backup Store |
|  inventory.csv, etc.  |         |  backup/local_backup |
+-----------------------+         +----------------------+
            |                                |
            | (if local fails)               | (redundancy)
            v                                v
+-----------------------+         +------------------------------+
|   AWS S3 / GDrive     |  <----  |  Cloud Backup Module         |
|  bucket or folder     |         |  boto3 + Google Drive API    |
+-----------------------+         +------------------------------+
```

## How to Run
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure cloud provider credentials.

### Option A: AWS S3
Set AWS credentials:
```bash
setx AWS_ACCESS_KEY_ID "your_key"
setx AWS_SECRET_ACCESS_KEY "your_secret"
setx AWS_DEFAULT_REGION "us-east-1"
```
Then, in the dashboard, choose `AWS S3` and enter:
- Bucket name
- Optional S3 prefix

### Option B: Google Drive
You can now choose either `OAuth Client` or `Service Account` in the dashboard.

OAuth Client setup:
1. In Google Cloud Console, create/select a project and enable **Google Drive API**.
2. Configure OAuth consent screen.
3. Create OAuth client credentials:
- Recommended: `Desktop app`
- Or `Web application` with redirect URI `http://localhost:8080/`
4. Download the OAuth client JSON file.
5. Set env vars:
```bash
setx GOOGLE_DRIVE_OAUTH_CLIENT_SECRET_FILE "C:\path\to\oauth-client.json"
setx GOOGLE_DRIVE_OAUTH_TOKEN_FILE "C:\path\to\google_drive_token.json"
setx GOOGLE_DRIVE_OAUTH_LOCAL_SERVER_PORT "8080"
```
You can also put these same values in a project `.env` file. The app now auto-loads `.env` during backup execution.
6. In dashboard, choose:
- Cloud Provider: `Google Drive`
- Google Drive Auth: `OAuth Client`
- Enter folder ID from `https://drive.google.com/drive/folders/<FOLDER_ID>`
7. On first backup run, a browser auth flow opens; after consent, token is saved and reused.

Service Account setup (alternative):
1. Create Service Account and download JSON key.
2. Share target Drive folder with service account email (Editor).
3. Set env var:
```bash
setx GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE "C:\path\to\service-account.json"
```
4. In dashboard, choose `Google Drive` + `Service Account` and enter folder ID.

3. Run the Streamlit dashboard:
```bash
streamlit run frontend/dashboard.py
```

4. Open in browser:
```text
http://localhost:8501
```

## Notes on Sample Dataset
- `dataset/warehouse_stock.xlsx` is a lightweight CSV-formatted placeholder with an `.xlsx` extension for demo portability.
- If you need a strict Excel `.xlsx`, replace it with a true Excel file or generate one using pandas with `openpyxl` installed.

## Project Structure
```
multi-cloud-backup
+-- frontend
|   +-- dashboard.py
+-- backend
|   +-- backup_manager.py
|   +-- local_backup.py
|   +-- cloud_backup.py
|   +-- failover_handler.py
|   +-- logger.py
|   +-- performance_monitor.py
+-- dataset
|   +-- sample supply chain files
+-- backup
|   +-- local_backup
+-- logs
|   +-- backup_logs.txt
+-- requirements.txt
+-- README.md
```
