from jiralite.utils import contains
from jiralite.defaults import SUMMARY_TEMPLATE, DESCRIPTION_TEMPLATE
from .handlers import DeploymentIssueHanlder


class SubTaskGenerator(object):
	CHAR_CROSS_BOLD = u'\u2716'
	CHAR_CROSS = u'\u2715'
	CHAR_CHECK_BOLD = u'\u2714'
	CHAR_CHECK = u'\u2713'

	def __init__(self, jiraclient, deployment_issue, build_issues):
		self._jira = jiraclient
		self._deployment = deployment_issue
		self._build = build_issues
		self._parsed_deployment = DeploymentIssueHanlder(deployment_issue)
		self._compare_build_and_deployment()
		self._get_issues_with_pending_dba_or_code_review()
		

	def set_build_issues(self, build_issues):
		self._build = build_issues
		self._compare_build_and_deployment()


	def _compare_build_and_deployment(self):
		self.build_issues_in_deployment_issue = []
		self.build_issues_not_in_deployment_issue = []
		self.build_issues_with_subtask = []
		self.build_issues_without_subtask = []

		for issue in self._build:
			instructions = self._parsed_deployment.get_instructions()
			if issue.key in instructions:
				self.build_issues_in_deployment_issue.append(issue.key)

				for instruction in instructions[issue.key]:
					is_sql_script = contains(r'.*sql', instruction)
				has_subtask = self._deployment.has_subtask(issue.key)
				if is_sql_script and not has_subtask:
					self.build_issues_without_subtask.append(issue.key)
				if has_subtask:
					self.build_issues_with_subtask.append(issue.key)
			else:
				self.build_issues_not_in_deployment_issue.append(issue.key)


	def _get_issues_with_pending_dba_or_code_review(self):
		self.issues_with_pending_dba_or_code_review = []

		for issue in self._build:
			for subtask in issue.subtasks:
				status = subtask["fields"]["status"]["name"].strip()
				summary = subtask["fields"]["summary"]
				is_dba_subtask = contains(r'dba review', summary)
				is_dev_subtask = contains(r'code review', summary)
				if status != "Done" and (is_dba_subtask or is_dev_subtask):
					self.issues_with_pending_dba_or_code_review.append(issue)


	def can_subtasks_be_created(self):
		return self.issues_with_pending_dba_or_code_review == [] and \
		self.build_issues_not_in_deployment_issue == []


	def run(self):
		if not self.can_subtasks_be_created():
			return None

		self.subtask_created = []
		for issue in self._build:
			if issue.key in self.build_issues_without_subtask:
				deploy = self._parsed_deployment.get_instructions(issue.key)
				revert = self._parsed_deployment.get_revert_instructions(issue.key)
				summary = SUMMARY_TEMPLATE.format(issue.key)
				description = DESCRIPTION_TEMPLATE.format(
					'\r\n# '.join(deploy), '\r\n# '.join(revert))
				response = self._jira.create_issue(issue.project_id, \
					summary, description, assignee="it_dba", \
					parent_issue=self._deployment)

				try:
					response = response.json()
					self.subtask_created.append(issue.key)
				except:
					response = None


	def report(self):
		return self
