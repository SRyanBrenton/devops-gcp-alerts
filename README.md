# DevOps Alerting & ChatOps Automation 🚨 ☁️

![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)
![Focus](https://img.shields.io/badge/Focus-Observability_%26_Incident_Response-blue?style=for-the-badge)

## 👋 Overview
Welcome to my alerting automation repository. This collection contains production-grade integrations that bridge **Google Cloud Platform (GCP)** and **Apigee Edge** monitoring systems with **Microsoft Teams**.

These tools enable "ChatOps" workflows, converting raw system metrics and infrastructure alerts into actionable, high-visibility notifications for Engineering and SRE teams.

## 📂 Project Index

| Application | Stack | Description |
| :--- | :--- | :--- |
| **[Google Cloud Teams Notifier](./google-cloud-msteams-alert-notifier)** | Python, Cloud Functions, Pub/Sub | A serverless function that ingests GCP Monitoring alerts via Pub/Sub and formats them into Adaptive Cards for MS Teams. |
| **[Apigee Edge Alert Notifier](./apigee-msteams-alert-notifier)** | JavaScript, Apigee Policies | A middleware proxy script that intercepts API Gateway alerts and transforms them into rich notifications with threshold details. |

## 💻 Technologies Used
* **Cloud Infrastructure:** Google Cloud Platform (Cloud Functions, Pub/Sub, Logging)
* **API Gateway:** Google Apigee Edge
* **Languages:** Python 3.9, JavaScript (ES6)
* **Collaboration:** Microsoft Teams Webhooks (Adaptive Cards 1.5)

## 🏗 Architecture Summary
This repository demonstrates an **Event-Driven Architecture**:
1.  **Ingestion:** Alerts are triggered by Infrastructure (GCP) or API Traffic (Apigee).
2.  **Transformation:** Scripts parse JSON payloads to extract severity, resource ID, and runbook links.
3.  **Notification:** Formatted cards are pushed to specific Teams Channels based on the alert context.

---
*Created and maintained by [SRyanBrenton](https://github.com/SRyanBrenton)*
