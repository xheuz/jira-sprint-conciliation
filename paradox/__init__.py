#!/usr/bin/env python
import logging
import sys

log = logging.getLogger()
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
log.addHandler(handler)

# log_file = os.path.join(os.path.abspath('.'), "paradox.log")
# logging.basicConfig(filename=log_file, level=logging.DEBUG)

import os

JIRA_API = os.environ.get('JIRA_API')
JIRA_USERNAME = os.environ.get('JIRA_USERNAME')
JIRA_PASSWORD = os.environ.get('JIRA_PASSWORD')

from .subtaskgen import SubTaskAutoGen
from jiralite import jiralite
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def index():
	return 'some documentation'


@app.route('/<username>')
def hello_user(username):
	return 'Hello ' + username


@app.route('/subtaskgen')
def subtaskgen():
	deployment_issue = request.args.get('deployment_issue')
	build_issues = request.args.get('build_issues')
	build_issues = build_issues.split(',')

	credentials = (JIRA_USERNAME, JIRA_PASSWORD)
	jira = jiralite(JIRA_API, credentials)

	settings = {
		"jiraclient": jira,
		"deployment_issue": jira.issue(deployment_issue, deployment=True),
		"build_issues": [jira.issue(issue.strip()) for issue in build_issues]
	}

	bot = SubTaskAutoGen(**settings)
	bot.run()
	return bot.report()


app.run(debug=True, port=8080)