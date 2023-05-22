import os
import dotenv

env_path = os.path.join(os.getcwd(), '.env')
dotenv.load_dotenv(dotenv_path=env_path)

owner = os.getenv('OWNER', '')
action_channel = os.getenv('ACTION_CHANNEL', '')
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
