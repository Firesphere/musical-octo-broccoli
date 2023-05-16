# Sentry & MS Teams

This little project creates/links a sentry project to a Teams team.

## Installation:

`git clone git@github.com:Firesphere/musical-octo-broccoli.git`

`pip3 install -r requirements.txt`

### Or, better yet, use a venv

`git clone git@github.com:Firesphere/musical-octo-broccoli.git`

`python3 -m venv musical-octo-broccoli`

`source musical-octo-broccoli/bin/activate`

`pip3 install -r requirements.txt`

## Usage

Note, to link an app, the full project name as returned from Sentry in `--list-apps` must be used.

When creating new, two projects are created, "projectname-test" and "projectname-prod".

### Create a new project
`python3 main.py --new --app=myprojectname`

### List projects from Sentry
`python3 main.py --list-apps`

### Link existing project to Teams
`python3 main.py --create --app=myprojectname-prod`

