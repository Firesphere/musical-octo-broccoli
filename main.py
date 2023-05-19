#!/usr/bin/python3

import argparse
import json
import requests
import dotenv
import os
from string import Template
from terminaltables import AsciiTable

env_path = os.path.join(os.getcwd(), '.env')
dotenv.load_dotenv(dotenv_path=env_path)

AUTH_TOKEN = os.getenv('AUTH_TOKEN')
org = os.getenv('ORG')
owner = os.getenv('OWNER')
action_team = os.getenv('ACTION_TEAM')
action_id = os.getenv('ACTION_ID')
action_channel = os.getenv('ACTION_CHANNEL')
action_channel_id = os.getenv('ACTION_CHANNEL_ID')


def rule_payload(app: str):
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
                "team": action_team,
                "id": action_id,
                "channel": action_channel,
                "channel_id": action_channel_id,
                "name": "Send a notification to the Sentry Team to General"
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


def _request(path, method="post", paginate=False, parse_json=True, **kwargs):
    # A token with scopes project:read,project:write fetched from
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}", "Content-Type": f"application/json"}

    url = f"https://sentry.io/api/0{path}"
    res = requests.request(method, url, headers=headers, **kwargs)
    res.raise_for_status()
    if paginate and res.links.get("next", {}).get("results", False):
        params = {"cursor": res.links["next"]["cursor"]}
        return res.json() + _request(path, method=method, params=params, **kwargs)
    return res.json() if parse_json else res


def list_projects():
    path = "/projects/"
    res = _request(path, method="get", paginate=True)
    return res


def list_rules(app: str):
    path = f"/projects/{org}/{app}/rules/"
    res = _request(path, method="get", paginate=True)
    return res


def fetch_rule(app: str, rule_id: int):
    path = f"/projects/{org}/{app}/rules/{rule_id}/"
    res = _request(path, method="get")
    return res


def create_rule(app: str, data: dict):
    path = f"/projects/{org}/{app}/rules/"
    res = _request(path, json=data)
    return res


def delete_rule(app: str, rule_id: int):
    path = f"/projects/{org}/{app}/rules/{rule_id}/"
    try:
        _request(path, method="delete", parse_json=False)
    except requests.exceptions.HTTPError:
        return False
    return True


def create_project(app: str):
    path = f"/teams/{org}/{org}/projects/"
    data = {
        "default_rules": True,
        "name": app,
        "platform": "php"
    }
    res = _request(path, 'post', json=data)
    return res


def main(
        app,
        create_rules: bool,
        list_apps: bool,
        new: bool
):
    # Get the app. It's passed in as a list, we need item one from the list
    if app is not None:
        app = app[0]

    if list_apps:
        table = [
            ['Sentry label', 'Project', 'DSN\nCSP']
        ]
        for project in list_projects():
            if app is None or app == project["slug"]:
                keys = _request(f"/projects/{org}/{project['slug']}/keys/")
                table.append([
                    keys["label"],
                    project["slug"],
                    f"{keys['dsn']['public']}\n{keys['dsn']['csp']}"
                ])
        tbl = AsciiTable(table, "Sentry projects")
        tbl.inner_heading_row_border = True
        tbl.inner_row_border = True
        print(tbl.table)

        return

    if create_rules:
        data = rule_payload(app)
        create_rule(app, data)

    if new:
        dsns = {}
        app = app
        for env in ['test', 'prod']:
            prj = f"{app}-{env}"
            res = create_project(prj)
            print("Project slug:")
            print(json.dumps(res["slug"]))
            keys = _request(f"/projects/{org}/{prj}/keys/")
            print("DSN:")
            print(keys["dsn"]["public"])
            if env == 'prod':
                dsns["LIVE_DSN"] = keys["dsn"]["public"]
                data = rule_payload(res["slug"])
                create_rule(prj, data)
            else:
                dsns["TEST_DSN"] = keys["dsn"]["public"]
        file = open("./assets/sentry.tmpl", "r")
        contents = Template(file.read())
        file.close()
        print("Sentry yml for Silverstripe:")
        print("###")
        print(contents.substitute(dsns))
        print("###")


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Update sentry project with a set of standard rules"
    )
    parser.add_argument("--app", '-a', nargs=1, help="Name of the app to link or create")
    parser.add_argument("--list-apps", '-la', action="store_true", help="List projects in Sentry")
    parser.add_argument("--teamlink", "-tl", action="store_true",
                        help="Link the app. Requires the full slug, with `-prod` or `-test`")
    parser.add_argument("--new", "-n", action="store_true",
                        help="Creates a production and test project, and links the production to Teams."
                             " Should not have `-prod` or `-test` in the app name")
    args = parser.parse_args()
    if args.app is None:
        if args.teamlink:
            parser.error("Please tell me the full slug of the app to link (use -la, --list-apps)")
        if args.new:
            parser.error("I don't know what you expected, but without an app name, I can't create a project.")
    elif not args.teamlink and not args.new and not args.list_apps:
        parser.error(
            "I'm unsure what to do with this app...\ncreate it? (use -n, --new)\n"
            "link it? (use -tl, --teamlink)\nget its DSN and CSP? (use -la, --list-apps)")
    main(args.app, args.teamlink, args.list_apps, args.new)
