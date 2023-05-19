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

## Configuration

Use a `.env` file, as per the example.env.



## Usage

Note, to link an app, the full project name as returned from Sentry in `--list-apps` must be used.

When creating new, two projects are created, "projectname-test" and "projectname-prod".

usage: main.py [-h] [--app APP] [--list-apps] [--teamlink] [--new]

Update sentry project with a set of standard rules

optional arguments:
  -h, --help         show this help message and exit
  --app APP, -a APP  Name of the app to link or create
  --list-apps, -la   list apps, or a single app if you pass in the app full slug
  --teamlink, -tl    Link the app. Requires the full slug
  --new, -n          Creates a new app and links the prod. Should not have `-prod` in the app name
### Create a new project
`python3 main.py --new --app=myprojectname`

### List projects from Sentry
`python3 main.py --list-apps`

### Link existing project to Teams
`python3 main.py --teamlink --app=myprojectname-prod`

