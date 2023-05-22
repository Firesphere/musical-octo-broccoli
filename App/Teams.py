import os
import dotenv

env_path = os.path.join(os.getcwd(), '.env')
dotenv.load_dotenv(dotenv_path=env_path)

action_team = os.getenv('ACTION_TEAM', False)
action_channel = os.getenv('ACTION_CHANNEL', '')
action_channel_id = os.getenv('ACTION_CHANNEL_ID', '')


class Teams:
    def payload(self):
        return [
                {
                    "tags": "environment,url",
                    "team": action_team,
                    "id": "sentry.integrations.msteams.notify_action.MsTeamsNotifyServiceAction",
                    "channel": action_channel,
                    "channel_id": action_channel_id,
                    "name": "Send a notification to the Sentry Team"
                }
            ]

