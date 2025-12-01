import json
import os
import logging
import configparser
import pathlib
import re

import google.cloud.logging
from google.cloud import secretmanager
from google.cloud import resourcemanager_v3
from google.cloud.logging_v2.handlers import CloudLoggingHandler

import requests
import http.client as http_client
from requests.auth import HTTPBasicAuth

# ----------------------- CONFIGURATION SETUP -----------------------
# Allow use of config file for any values not defined within env. variables.
config = configparser.ConfigParser()
config.read(pathlib.Path(__file__).parent.parent/"notifications.cfg")

# -------------------- DEFINE CENTRALIZED LOGGING --------------------
# Logs messages to Google Cloud Logging with configurable level.
def log(message, type="INFO"):
    """
    Args:
        message (str): The message to log.
        type (str, optional): Log level ('INFO', 'DEBUG', 'WARN', 'ERROR'). 
                              Defaults to 'INFO'.
    """
    #Initialize logging client
    client = google.cloud.logging.Client()
    handler = CloudLoggingHandler(client)
    cloud_logger = logging.getLogger('cloudLogger')

    # Configure log level based on env variable
    log_level_str = os.getenv('LOG_LEVEL', 'INFO')
    log_level = getattr(logging, log_level_str.upper(), logging.INFO) 
    cloud_logger.setLevel(log_level)

    cloud_logger.addHandler(handler)
    cloud_logger.log(log_level, message)  # Use the configured log level

# --------------- SECRET MANAGER RETRIEVAL ---------------
# Retreive any secret values from gcp secret manager
def get_sa_key(secret_name, project_id):
    """
    This function gets service account key stored in Cloud Secret Manager and stores it in JSON.
    The JSON key is stored under the /tmp folder.
    """

    log("Logged: Parameters provided for function get_sa_key are secret_name=" + secret_name + ", project_id=" + project_id, 'info')
    secret_manager_client = secretmanager.SecretManagerServiceClient()

    request = {
        "name": "projects/" + project_id + "/secrets/" + secret_name + "/versions/latest"
    }

    response = secret_manager_client.access_secret_version(request)
    return response.payload.data

# ---------- DEFINE MS TEAMS COMMUNICATION DATA AND PAYLOAD ----------
def post_data_to_teams(payload_data):

    # Initialize logging for debugging purposes
    http_client.HTTPConnection.debuglevel = 1
    logging.basicConfig()
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

    # Parse JSON data. Takes payload_data string and converts it to Py dict named payload_json
    payload_json = json.loads(payload_data)
	
    # Defines env variables from cloud function
    ms_teams_url = os.environ.get("MS_TEAMS_URL")
    runbook_url = os.environ.get("RUNBOOK_URL")

    # Set json boolean values to extract properly within my json payload.
    """ This is needed to properly pass boolean values as lower case string into json for ms teams to accept """
    wrap_true = payload_json.get("wrap", True)  # Use default True if not present for wrap
    sep_true = payload_json.get("separator", True)  # Use default True if not present for separator
    isvis_false = payload_json.get("isVisible", False)  # Use default False if not present for isVisible

    # ---------- BEGIN JSON ADAPTIVE CARD PAYLOAD SCHEMA AND TEMPLATING ----------
    adaptive_card = {
	"type": "message",
	"content": "Teams webhook adaptive card json",
	"attachments": [
		{
			"contentType": "application/vnd.microsoft.card.adaptive",
			"content": {
				"type": "AdaptiveCard",
				"$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
				"version": "1.5",
				"body": [
					{
						"type": "Container",
						"items": [
							{
								"type": "TextBlock",
								"text": "Google Cloud Alerts",
								"wrap": wrap_true,
								"size": "Medium",
								"weight": "Bolder",
								"spacing": "Large",
								"horizontalAlignment": "Center"
							}
						],
						"style": "emphasis",
						"separator": sep_true
					},
					{
						"type": "Container",
						"separator": sep_true,
						"items": [
							{
								"type": "TextBlock",
								"text": f"**{payload_json.get('incident', {}).get('policy_name', 'Unknown')}**",
								"wrap": wrap_true
							}
						]
					},
					{
						"type": "Container",
						"items": [
							{
								"type": "TextBlock",
								"text": f"_{payload_json.get('incident', {}).get('condition_name', 'Unknown')}_",
								"wrap": wrap_true
							},
							{
								"type": "TextBlock",
								"text": f"{payload_json.get('incident', {}).get('summary', 'Unknown')}",
								"wrap": wrap_true
							},
							{
								"type": "Container",
								"separator": sep_true,
								"items": [
									{
										"type": "FactSet",
										"facts": [
											{
												"title": "Threshold",
												"value": f"{payload_json.get('incident', {}).get('threshold_value', 'Unknown')}"
											},
											{
												"title": "Observed Value",
												"value": f"{payload_json.get('incident', {}).get('observed_value', 'Unknown')}"
											}
										]
									}
								]
							}
						]
					},
					{
						"type": "Container",
						"separator": sep_true,
						"items": [
							{
								"type": "ColumnSet",
								"columns": [
									{
										"type": "Column",
										"width": "stretch",
										"items": [
											{
												"type": "TextBlock",
												"text": "More Details",
												"wrap": wrap_true,
												"horizontalAlignment": "Center"
											}
										],
										"horizontalAlignment": "Right",
										"verticalContentAlignment": "Center"
									},
									{
										"type": "Column",
										"width": "stretch",
										"items": [
											{
												"type": "ActionSet",
												"actions": [
													{
														"type": "Action.ToggleVisibility",
														"iconUrl": "https://amdesigner.azurewebsites.net/samples/assets/Down.png",
														"targetElements": [
															"moreDetails",
															"moreDetailsWrapper",
															"chevronUp",
															"chevronDown"
														],
														"id": "expandDetails"
													}
												],
												"horizontalAlignment": "Right",
												"id": "chevronDown"
											}
										]
									},
									{
										"type": "Column",
										"width": "stretch",
										"items": [
											{
												"type": "ActionSet",
												"actions": [
													{
														"type": "Action.ToggleVisibility",
														"iconUrl": "https://amdesigner.azurewebsites.net/samples/assets/Up.png",
														"targetElements": [
															"moreDetails",
															"moreDetailsWrapper",
															"chevronDown",
															"chevronUp"
														],
														"id": "collapseDetails"
													}
												],
												"horizontalAlignment": "Left",
												"isVisible": isvis_false,
												"id": "chevronUp"
											}
										]
									}
								]
							}
						],
						"style": "default"
					},
					{
						"type": "Container",
						"items": [
							{
								"type": "FactSet",
								"facts": [
									{
										"title": "Project",
										"value": f"{payload_json.get('incident', {}).get('scoping_project_id', 'Unknown')}"
									},
                                   				 	{
										"title": "Project Num",
										"value": f"{payload_json.get('incident', {}).get('scoping_project_number', 'Unknown')}"
									},
                                    					{
										"title": "Incident Id",
										"value": f"{payload_json.get('incident', {}).get('incident_id', 'Unknown')}"
									},
                                    					{
										"title": "State",
										"value": f"{payload_json.get('incident', {}).get('state', 'Unknown')}"
									},
                                    					{
										"title": "Severity",
										"value": f"{payload_json.get('incident', {}).get('severity', 'Unknown')}"
									}

								],
								"id": "moreDetails",
								"isVisible": isvis_false
							}
						],
						"style": "emphasis",
						"id": "moreDetailsWrapper",
						"isVisible": isvis_false
					},
					{
						"type": "Container",
						"items": [
							{
								"type": "ActionSet",
								"actions": [
									{
										"type": "Action.OpenUrl",
										"title": "View Alert Incident",
										"tooltip": "Open the google alert incident page",
										"style": "positive",
										"url": f"{payload_json.get('incident', {}).get('url', 'Unknown')}"
									},
									{
										"type": "Action.OpenUrl",
										"title": "Read The Runbook",
										"tooltip": "Open the operations runbook page",
										"url": runbook_url,
										"style": "positive"
									}
								]
							}
						],
						"horizontalAlignment": "Center",
						"verticalContentAlignment": "Center",
						"spacing": "Large"
					}
				]
			}
		}
	]
}
    
    # Send the message to Microsoft Teams using requests.post
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(ms_teams_url, headers=headers, json=adaptive_card)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        logging.info("Message sent to Microsoft Teams successfully")
    except requests.exceptions.RequestException as e:
        logging.error("Failed to send message to Microsoft Teams: {}".format(str(e)))

# -------- BEGIN DECODE AND PARSING OF PUBSUB MESSAGE AND SET CUSTOM LOG --------
def alert_notification_handler(event, context):
    """Cloud Function to be triggered by PubSub subscription.
       This function receives messages containing Alerts data.
       It creates a log entry within the project allowing Cloud
       Monitoring to be used for alerting.

    Args:
        event (dict): The PubSub message payload.
        context (google.cloud.functions.Context): Metadata of triggering event.
    Returns:
        None; the output is written to Cloud Logging.
    """
    import base64
    # Set custom gcloud log name
    log("Entered the alert notification handler", 'INFO')

    CUSTOM_LOG_NAME = "alert_notifications_log"
    logging_client = google.cloud.logging.Client()
    logger = logging_client.logger(CUSTOM_LOG_NAME)
	
    # PubSub payloads come in encoded. Using base64 the message will be decoded for parsing.
    try:
        # PubSub messages come in encrypted
        dataString = base64.b64decode(event['data']).decode('utf-8')
    except Exception as e:
        dataString = "error decoding payload"

    data = dataString
    try:
        # Try to parse dataString as JSON
        data = json.loads(dataString)
    except Exception as e:
        log(f"Error processing Pub/Sub message: {e}", "ERROR")
        return
    # Print the payload in DEBUG mode
    if os.getenv('LOG_LEVEL') == 'DEBUG':
        log(f"Pub/Sub Alert Payload: {data}", "DEBUG")
	    
    # Log the payload to Cloud Logging	    
    logger.log_struct(
        {
            "event_id": context.event_id,
            "timestamp": context.timestamp,
            "data": data,
        }
    )

    # Read the project number from the payload
    skip_incident_creation = False

    project_id = os.getenv('PROJECT_ID')
	
    # Check if incident data exists and send to MS teams
    if (data["incident"] is not None):
        current_state = data['incident'].get('state') 

        if current_state and current_state.casefold() == 'open':  # Case-insensitive check
            post_data_to_teams(dataString) 
        else:
            log("Incident state is closed, no Teams notification sent", "INFO")
