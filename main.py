#!/usr/bin/python3

import argparse
import json
import requests
import dotenv
import os
from string import Template
from terminaltables import AsciiTable
from App.Teams import Teams
from App.Slack import Slack

env_path = os.path.join(os.getcwd(), '.env')
dotenv.load_dotenv(dotenv_path=env_path)

AUTH_TOKEN = os.getenv('AUTH_TOKEN', '')
org = os.getenv('ORG', '')
owner = os.getenv('OWNER', '')
action_team = os.getenv('ACTION_TEAM', False)
action_slack_id = os.getenv('ACTION_SLACK_ID', False)

# Update or edit conditions & filters as you wish.
default_conditions = [
    {
        "id": "sentry.rules.conditions.first_seen_event.FirstSeenEventCondition"
    },
    {
        "id": "sentry.rules.conditions.regression_event.RegressionEventCondition"
    }
]
default_filters = [
    {
        "comparison_type": "newer",
        "time": "minute",
        "id": "sentry.rules.filters.age_comparison.AgeComparisonFilter",
        "value": "60"
    }
]


def rule_payload(app: str):
    action = []
    if action_team is not False:
        action = Teams().payload()
    if action_slack_id is not False:
        action = Slack().payload()
    return {
        "conditions": default_conditions,
        "filters": default_filters,
        "actions": action,
        "actionMatch": "all",
        "filterMatch": "all",
        "frequency": 1440,
        "name": "Sentry alert",
        "owner": owner,
        "projects": [app],
    }


def _request(path, method="post", paginate=False, parse_json=True, **kwargs):
    # A token with scopes project:read,project:write fetched from
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}", "Content-Type": "application/json"}

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


def create_rule(app: str, data: dict):
    # If there's no Teams or Slack id, skip setting up rules
    if not action_team and not action_slack_id:
        print("No Slack or Teams connection set up, skipping creating rules")
        return {}
    path = f"/projects/{org}/{app}/rules/"
    res = _request(path, json=data)
    return res


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
        new: bool,
        as_yml: bool,
):
    list_dsns = {}

    # Get the app. It's passed in as a list, we need item one from the list
    if app is not None:
        app = app[0]

    if list_apps:
        table = [
            ['Sentry label', 'Project', 'DSN\nCSP']
        ]
        for project in list_projects():
            if (app is None) or (project["slug"].find(app) >= 0):
                keys = _request(f"/projects/{org}/{project['slug']}/keys/")
                list_dsns = populate_list_dsn(as_yml, keys, list_dsns, project)
                table.append([
                    keys["label"],
                    project["slug"],
                    f"{keys['dsn']['public']}\n{keys['dsn']['csp']}"
                ])
        tbl = AsciiTable(table, "Sentry projects")
        tbl.inner_heading_row_border = True
        tbl.inner_row_border = True
        print(tbl.table)
        print(list_dsns)

    if create_rules:
        data = rule_payload(app)
        create_rule(app, data)

    if new:
        dsns = create_for_env(app)
        as_yml = True
        list_dsns = {'app': dsns}

    if as_yml:
        file = open("./assets/sentry.tmpl", "r")
        contents = Template(file.read())
        file.close()
        for dsn in list_dsns:
            print(dsn)
            print("Sentry yml for Silverstripe:")
            print("###")
            print(contents.substitute(list_dsns[dsn]))
            print("###")
    return


def populate_list_dsn(as_yml, keys, list_dsns, project):
    dsn_key = project['slug'].split('-')
    dsn_key = dsn_key[0]
    if dsn_key not in list_dsns:
        list_dsns[dsn_key] = {
            'TEST_DSN': None,
            'LIVE_DSN': None
        }
    if as_yml:
        if project["slug"].find('-test') >= 0:
            list_dsns[dsn_key]["TEST_DSN"] = keys["dsn"]["public"]
        else:
            list_dsns[dsn_key]["LIVE_DSN"] = keys["dsn"]["public"]

    return list_dsns

def create_for_env(app):
    dsns = {}
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
    return dsns


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
    parser.add_argument("--as-yml", "-yml", action="store_true",
                        help="Output a Silverstripe based YML to copy in to the project.")
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
    if not args.teamlink and not args.new and not args.list_apps and args.app is None:
        parser.error("You might need some --help (-h)")
    main(args.app, args.teamlink, args.list_apps, args.new, args.as_yml)
