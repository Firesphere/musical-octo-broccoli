import os
import dotenv

env_path = os.path.join(os.getcwd(), '.env')
dotenv.load_dotenv(dotenv_path=env_path)

action_channel = os.getenv('ACTION_CHANNEL', '')
action_slack_id = os.getenv('ACTION_SLACK_ID', False)


class Slack:

    # Todo, support Slack
    def payload(self):
        return [
                {
                    "tags": "environment,url",
                    "workspace": action_slack_id,
                    "id": "sentry.integrations.slack.notify_action.SlackNotifyServiceAction",
                    "channel": action_channel,
                    "name": "Send a notification to Slack"
                }
            ]
