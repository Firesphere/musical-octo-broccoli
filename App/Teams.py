import os

AUTH_TOKEN = os.getenv('AUTH_TOKEN', '')
org = os.getenv('ORG', '')
owner = os.getenv('OWNER', '')
action_team = os.getenv('ACTION_TEAM', False)
action_channel = os.getenv('ACTION_CHANNEL', '')
action_channel_id = os.getenv('ACTION_CHANNEL_ID', '')

action_slack_id = os.getenv('ACTION_SLACK_ID', False)


class Teams:
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
                    "team": action_team,
                    "id": "sentry.integrations.msteams.notify_action.MsTeamsNotifyServiceAction",
                    "channel": action_channel,
                    "channel_id": action_channel_id,
                    "name": "Send a notification to the Sentry Team"
                }
            ],
            "actionMatch": "all",
            "filterMatch": "all",
            "frequency": 1440,
            "name": "Sentry alert",
            "owner": owner,
            "projects": [
                app
            ],
        }
