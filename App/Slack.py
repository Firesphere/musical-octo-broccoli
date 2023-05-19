import os

AUTH_TOKEN = os.getenv('AUTH_TOKEN', '')
org = os.getenv('ORG', '')
owner = os.getenv('OWNER', '')
action_team = os.getenv('ACTION_TEAM', False)
action_channel = os.getenv('ACTION_CHANNEL', '')
action_channel_id = os.getenv('ACTION_CHANNEL_ID', '')

action_slack_id = os.getenv('ACTION_SLACK_ID', False)

class Slack:

    # Todo, support Slack
    def payload(self, app: str):
        return {
            "conditions": [
                {
                    "interval": "5m",
                    "id": "sentry.rules.conditions.event_frequency.EventFrequencyCondition",
                    "value": 10,
                    "comparisonType": "count",
                    "name": "The issue is seen more than 10 times in 5m"
                },
                {
                    "id": "sentry.rules.conditions.regression_event.RegressionEventCondition",
                    "name": "The issue changes state from resolved to unresolved"
                }
            ],
            "filters": [],
            "actions": [
                {
                    "tags": "environment,url",
                    "workspace": action_slack_id,
                    "id": "sentry.integrations.slack.notify_action.SlackNotifyServiceAction",
                    "channel": action_channel,
                    "name": "Send a notification to Slack"
                }
            ],
            "actionMatch": "all",
            "filterMatch": "all",
            "frequency": 1440,
            "name": "Sentry alert",
            "owner": owner,
            "projects": [
                app
            ]
        }


