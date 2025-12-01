# apigee-msteams-alert-notifier

# Apigee Edge: MS Teams Alert Transformation Proxy ⚡

![Apigee](https://img.shields.io/badge/Apigee-Edge-red?style=for-the-badge&logo=google-cloud&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow?style=for-the-badge&logo=javascript&logoColor=white)
![XML](https://img.shields.io/badge/Config-XML-orange?style=for-the-badge)

## 📖 Overview
This project contains the logic and configuration for an **Apigee Edge API Proxy** that acts as a middleware transformation layer. 

It intercepts raw JSON alert payloads from upstream monitoring systems, parses critical threshold violations, and reconstructs the payload into a **Microsoft Teams MessageCard** format. This ensures that operational alerts sent to Teams are readable, actionable, and formatted correctly before they reach the webhook.

## 🏗 Architecture & Request Flow
The proxy logic utilizes Apigee's **PreFlow** and **TargetEndpoint** hooks to manipulate the payload before it is sent to the backend target.

`Monitoring Tool` ➔ `Proxy Endpoint` ➔ **[ JS Transformation ]** ➔ **[ Header Assignment ]** ➔ `Target Endpoint` ➔ `MS Teams`



## 📂 Repository Contents
* `msteams-alert-integration.js` - The core logic that parses the incoming JSON and generates the Adaptive Card HTML.

## ⚙️ Implementation Guide
Since Apigee relies on XML configuration to trigger JavaScript resources, the following setup demonstrates how this script is orchestrated within the API Proxy flows.

### 1. Policy Definitions
Define the policies to execute the script and assign the resulting payload.

**JavaScript Policy (`msteams-alert-integration.xml`)**
Executes the JS file located in the resource repository.
```xml
<Javascript async="false" continueOnError="false" enabled="true" timeLimit="200" name="msteams-alert-integration">
    <DisplayName>msteams-alert-integration</DisplayName>
    <ResourceURL>jsc://msteams-alert-integration.js</ResourceURL>
</Javascript>
