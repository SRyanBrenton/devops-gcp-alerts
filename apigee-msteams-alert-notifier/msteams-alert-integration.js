if (context.flow == "PROXY_REQ_FLOW") {
    var alertData = JSON.parse(context.getVariable("request.content"));

    // Extract relevant data from the alert message
    var alertName = alertData.alertName;
    var org = alertData.org;
    var description = alertData.description;
    var alertTime = alertData.alertTime;
    var playbook = alertData.playbook;

    // Extract and format threshold violations with line breaks using HTML <br> tags
var formattedThresholdViolations = "";
if (alertData.thresholdViolationsFormatted && alertData.thresholdViolationsFormatted.length > 0) {
    for (var i = 0; i < alertData.thresholdViolationsFormatted.length; i++) {
        var violation = alertData.thresholdViolationsFormatted[i];
            formattedThresholdViolations += "**Proxy**: `" + violation.proxy + "`<br>";
            formattedThresholdViolations += "**Region**: `" + violation.region + "`<br>";
            formattedThresholdViolations += "**Status Code**: `" + violation.statusCode + "`<br>";
            formattedThresholdViolations += "**Trigger Value**: `" + violation.triggerValue + "`<br>";
            formattedThresholdViolations += "**Duration**: `" + violation.duration + "`<br>";
            formattedThresholdViolations += "**Threshold Value**: `" + violation.thresholdValue + "`<br>";
            formattedThresholdViolations += "**Violation**: `" + violation.violation + "`<br><br>";
    }
} else {
    formattedThresholdViolations = "No threshold violations found.";
}


    // Construct the payload for Microsoft Teams
    var teamsPayload = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "summary": "Alert: " + alertName,
        "themeColor": "FF4300",
        "sections": [
            {
                "activityTitle": "Alert: " + alertName,
                "activitySubtitle": "Organization: " + org,
                "markdown": true,
                "facts": [
                    {
                        "name": "Description",
                        "value": description
                    },
                    {
                        "name": "Alert Time",
                        "value": alertTime
                    },
                    // Add more facts as needed
                ],
                "text": formattedThresholdViolations + "<br>[Operations Runbook](" + encodeURI(playbook) + ")" // Encoding playbook URL as a hyperlink
            }
        ]
    };

    // Convert the payload to string and store it in a variable for later use
    var teamsPayloadString = JSON.stringify(teamsPayload);
    context.setVariable("teamsPayload", teamsPayloadString);
}
