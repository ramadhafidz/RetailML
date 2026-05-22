#!/bin/bash
set -e

# Pastikan Anda sudah login ke gcloud: `gcloud auth login`
# dan sudah set project: `gcloud config set project datawarehouse-493606`

echo "🚀 Mendeploy ML Engine ke Google Cloud Functions..."

gcloud functions deploy proses-file-otomatis \
  --gen2 \
  --runtime=python310 \
  --region=asia-southeast2 \
  --source=. \
  --entry-point=process_new_csv \
  --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
  --trigger-event-filters="bucket=retail-data-raw-izz" \
  --memory=512MB \
  --timeout=120s

echo "✅ Deploy selesai!"
