from getpass import getpass
import base64
import pdb
import logging
import github
from .credentials import Credentials

logger = logging.getLogger(__name__)

LEETCODE_REPO_NAME = "leetcode-accepted-submissions"
README = "README.md"

"""
Convert language name to file extension
"""
def language_to_file_extension(language):
    if language.startswith('python'):
        return '.py'

    raise Exception(language + ' to extension conversion not implemented')


"""
Responsible for creating and maintaining the github repo with leetcode submissions
"""
class GithubRepoHandler:
    def __init__(self, credentials):
        self.github = None

        logger.debug("Logging into Github...")

        self.github = github.Github(credentials.get_token())
        self.repo = None

    """
    creates leetcode submission repo if non existent
    """
    def create_repo(self):
        try:
            logger.debug("Creating repo in github")
            self.repo = self.github.get_user().create_repo(LEETCODE_REPO_NAME)
        except github.GithubException as e:
            logger.info("%s: possible that the repo already exists", str(e))

    """
    returns leetcode submission repo
    """
    def repo_exists(self):
        if not self.repo:
            try:
                logger.debug("Checking if repo already exists in Github")
                self.repo = self.github.get_user().get_repo(LEETCODE_REPO_NAME)
            except github.UnknownObjectException as e:
                logger.info("%s: repo does not exist", str(e))

        return self.repo

    """
    Takes a dict of problem_name to (accepted_url, language, code_content) and commits the code in a file <problem_name>.<ext>
    """
    def commit(self, latest_accepted_submissions):
        for k, v in latest_accepted_submissions.items():
            problem_name = k
            accepted_submission_url = v[0]
            language = v[1]
            code_contents = v[2]

            self.__update_readme(problem_name, accepted_submission_url)

            filename = problem_name + language_to_file_extension(language)

            logger.debug("Committing %s to the repo for submission %s", filename, accepted_submission_url)

            # Try creating files first as it is more likely submissions will be made for new problems
            try:
                self.repo.create_file(filename, "Create " + filename, code_contents)
            except github.GithubException:
                # File already exists
                logger.debug("Updating %s since a submission for %s already exists", filename, problem_name)
                contents = self.repo.get_contents(filename)
                self.repo.update_file(contents.path, "Update " + filename, code_contents, contents.sha)

    """
    collect and return accepted_submission urls from README
    """
    def get_commited_accepted_submission_urls(self):
        logger.debug("Retrieving accepted submitted urls from README")
        readme_content = self.__get_readme()
        file_content = base64.b64decode(readme_content.content).decode("utf-8")
        lines = file_content.split("\n")
        urls = []
        for l in lines:
            # "-","https://leetcode.com/problems/....","->","https://leetcode.com/submissions/detail/...."
            if "https://leetcode.com" in l and len(l.split(" ")) == 4:
                urls.append(l.split(" ")[3])
        return urls

    """
    Get readme file contents from repo or create if not existent
    """
    def __get_readme(self):
        try:
            readme_content = self.repo.get_contents(README)
        except github.GithubException:
            # If we cannot create README here just let the exception go since there it is something fatal
            logger.debug("Creating README")
            readme_content = self.repo.create_file(README, "Create README", "# Leetcode Accepted Submissions")['content']

        return readme_content

    """
    Updates README with <problem_url> -> <accepted_url>
    """
    def __update_readme(self, problem_name, accepted_url):
        readme_content = self.__get_readme()
        file_content = base64.b64decode(readme_content.content).decode("utf-8")

        if accepted_url not in file_content:
            logger.debug("Adding %s to README", accepted_url)
            new_content = file_content + "\n" + "- https://leetcode.com/problems/" + problem_name + " -> " + accepted_url
            self.repo.update_file(readme_content.path, "Add " + accepted_url + " to README", new_content, readme_content.sha)
