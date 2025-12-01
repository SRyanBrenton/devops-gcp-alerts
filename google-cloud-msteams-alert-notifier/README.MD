# google-cloud-msteams-alert-notifier ☁️ 🚀

![Python](https://img.shields.io/badge/Python-3.9-blue?style=for-the-badge&logo=python&logoColor=white)
![GCP](https://img.shields.io/badge/Google_Cloud-Platform-red?style=for-the-badge&logo=google-cloud&logoColor=white)
![Teams](https://img.shields.io/badge/Microsoft_Teams-ChatOps-purple?style=for-the-badge&logo=microsoft-teams&logoColor=white)

## 📖 Overview
This project is a **Serverless Cloud Function** designed to improve incident response times by bridging Google Cloud Platform (GCP) monitoring with Microsoft Teams. 
It consumes alert payloads from **GCP Pub/Sub**, parses the JSON data, and formats it into a high-visibility **Adaptive Card** sent directly to an MS Teams channel. This enables "ChatOps" workflows where engineering teams can view incident details, severity, and runbooks without leaving their communication platform.

Once this script is live via either a Cloud Run Function 2nd Gen, or Cloud Function 1st Gen you will create a new notification channel within GCP under Ops Observability Monitoring. Be sure to create a new Pub/Sub notification. Any alerts you want to notify to your MS Teams channel you will add this channel to your alert notification rules.

## 🏗 Architecture
The data flow represents an event-driven architecture:

`GCP Monitoring Alert` ➔ `Pub/Sub Topic` ➔ `Cloud Function (Python)` ➔ `MS Teams Webhook`

## ✨ Key Features
* **Adaptive Cards:** Converts raw JSON alerts into rich, interactive UI cards (not just plain text).
* **Conditional Logic:** Only forwards "Open" incidents; automatically filters out closed/resolved states to reduce noise.
* **Structured Logging:** Implements Google Cloud Logging with configurable log levels for deep observability.
* **Secret Management:** Includes helper functions for integrating with GCP Secret Manager for secure credential retrieval.

## 🛠️ Prerequisites
* Google Cloud Platform project with billing enabled.
* **Cloud Functions API** and **Pub/Sub API** enabled.
* A Microsoft Teams channel with an **Incoming Webhook** configured.

## ⚙️ Configuration & Environment Variables
The function relies on environment variables to keep sensitive URLs out of the source code. Ensure the following are set in your Cloud Function runtime environment:

| Variable | Description | Example Value |
| :--- | :--- | :--- |
| `MS_TEAMS_URL` | **(Required)** The webhook URL for the destination Teams channel. | `https://outlook.office.com/webhook/...` |
| `RUNBOOK_URL` | **(Required)** Link to your internal wiki/Confluence for SOPs. | `https://wiki.company.com/ops/runbook` |
| `PROJECT_ID` | **(Required)** The GCP Project ID where the function resides. | `my-prod-project-123` |
| `LOG_LEVEL` | (Optional) Sets the verbosity of the logs. Default: `INFO`. | `DEBUG`, `INFO`, `WARN` |

## 🚀 Deployment Guide

### 1. Install Dependencies
Ensure you have the required libraries locally for testing:
```bash
pip install -r requirements.txt
```

### 2. Deploy via gcloud CLI
You can deploy this function directly from the command line. Make sure to replace `[YOUR_TOPIC_NAME]` with your actual Pub/Sub trigger topic.

```bash
gcloud functions deploy gcp-teams-notifier \
--runtime python39 \
--trigger-topic [YOUR_TOPIC_NAME] \
--entry-point alert_notification_handler \
--set-env-vars MS_TEAMS_URL="[YOUR_URL]",RUNBOOK_URL="[YOUR_LINK]",PROJECT_ID="[YOUR_ID]" \
--region us-central1
```

## 🧪 JSON Payload & Adaptive Cards
This script specifically handles the **Adaptive Card v1.5** schema. It dynamically formats the following alert data:
* **Policy Name:** The specific alert definition (e.g., "High CPU Usage").
* **Condition:** What triggered the alert.
* **Threshold vs. Observed:** e.g., "Threshold: 80% | Observed: 92%".
* **Links:** Direct buttons to the GCP Console Incident and the Operations Runbook.

## 🤝 Contributing
1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/new-card-layout`).
3.  Commit your changes.
4.  Push to the branch and open a Pull Request.

---
*Created and maintained by Shaun Brenton*
