'''All handlers are going to be defined here
'''
from jiralite.utils import contains


class DeploymentIssueHanlder():

	def __init__(self, issue):
		self._issue = issue
		self._description = {}
		self._parse_description()


	def _parse_description(self):
		for line in self._issue.description.splitlines():
			is_h1_header = contains(r'^h1', line)
			if is_h1_header:
				index = line.index(" ")
				title, garbage = line[index+1:].strip().split(" ")
				self._description[title] = {}
				continue

			is_h2_header = contains(r'^h2', line)
			if is_h2_header:
				header, team = line.strip().split(" ")
				continue

			is_h3_header = contains(r'^h3', line)
			if is_h3_header:
				header, ticket = line.strip().split(" ")
				continue

			is_url = contains(r'^http', line)
			if is_url:
				if not ticket in self._description[title]:
					self._description[title][ticket] = []
				self._description[title][ticket].append(line.strip())
				continue

			is_comment = contains(r'^nothing', line)
			if is_comment and team == 'DBA':
				self._description[title][ticket] = line.strip()
				continue


	def get_instructions(self, ticket=None):
		if ticket:
			return self._description["Deployment"][ticket]
		return self._description["Deployment"]


	def get_revert_instructions(self, ticket=None):
		if ticket:
			return self._description["Revert"][ticket]
		return self._description["Revert"]


	def get_issues_without_revert_instructions(self):
		return [issue for issue in self._description["Deployment"]
		if issue not in self._description["Revert"]]
