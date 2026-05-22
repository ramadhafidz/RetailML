# 🧠 Retail Dashboard - ML Engine

This is the Data Standardization & Machine Learning engine for the Retail Dashboard project. It is designed to be highly efficient, stateless, and deployed as a serverless Google Cloud Function.

It solves the problem of messy, unstructured retail data by mapping varying column names (like 'prc', 'harga', 'stk', 'inventory') into standardized data warehouse schemas.

## 🚀 Tech Stack
- **Environment**: Python 3.10
- **Core Libraries**: Pandas, Scikit-learn
- **Algorithm**: Hybrid (Regex Rule-based + TF-IDF Logistic Regression)
- **Deployment**: Google Cloud Functions (Gen 2) & Eventarc
- **CI/CD**: GitHub Actions

## ⚙️ Architecture Workflow
1. **Trigger (Eventarc)**: A new raw CSV file is uploaded to the GCS bucket (`retail-data-raw-493606`) by the Backend.
2. **Execution**: The Cloud Function (`main.py`) wakes up, downloads the CSV into memory, and runs the data through the core engine (`engine/column_mapper_core.py`).
3. **Storage**: The cleaned, standardized DataFrame is appended directly to the BigQuery table (`retail_warehouse.integrated_retail_data`).

## ☁️ Deployment

### Automated (GitHub Actions)
Pushing to the `main` branch will automatically trigger the GitHub Actions workflow (`.github/workflows/deploy.yml`) which deploys the updated code to Google Cloud Functions. 
*Note: Requires `GCP_CREDENTIALS` to be set in GitHub Repository Secrets.*

### Manual / Local Testing
You can deploy manually from your terminal using the provided shell script:
```bash
./deploy.sh
```
To test the pipeline locally without deploying, you can run the simulator scripts in the `scripts/` folder or run `column_mapper_lokal.py`.
