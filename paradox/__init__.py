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

import os

JIRA_API = os.environ.get('JIRA_API')
JIRA_USERNAME = os.environ.get('JIRA_USERNAME')
JIRA_PASSWORD = os.environ.get('JIRA_PASSWORD')
credentials = (JIRA_USERNAME, JIRA_PASSWORD)

from .subtasks import SubTaskGenerator
from jiralite import jiralite

jira = jiralite(JIRA_API, credentials)

from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('base.html')


# Subtask Generator
@app.route('/subtasks', methods=['GET'])
def subtasks_index():
	return render_template('subtasks/index.html')


@app.route('/api/v1/subtasks')
def subtasks():
	deployment_issue = request.args.get('deployment_issue')
	build_issues = request.args.get('build_issues')
	build_issues = build_issues.split(',')

	Generator = SubTaskGenerator(
		jiraclient=jira,
		deployment_issue=jira.issue(deployment_issue.strip()),
		build_issues=[jira.issue(issue.strip()) for issue in build_issues])
	Generator.run()
	return render_template('subtasks/report.html', data=Generator.report())