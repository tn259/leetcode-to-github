import github
from getpass import getpass

LEETCODE_REPO_NAME="leetcode-accepted-submissions"

"""
Convert language name to file extension
"""
def language_to_file_extension(language):
  if language.starts_with('python'):
    return '.py'
  else:
    raise Exception(language+' to extension conversion not implemented')


"""
Responsible for creating and maintaining the github repo with leetcode submissions
"""
class GithubRepoHandler:
  def __init__(self):
    self.github = None

    username = input("Github username: ")
    password = getpass()

    self.github = github.Github(username, password)
    self.repo = None

  """
  creates leetcode submission repo if non existent
  """
  def create_repo(self):
    try:  
      self.repo = self.get_user().create_repo(LEETCODE_REPO_NAME)
    except github.GithubException.GithubException as e:
      print(str(e)+": possible that the repo already exists")

  """
  returns leetcode submission repo
  """
  def repo_exists(self):
    if not self.repo:
      try 
        self.repo = self.github.get_repo(LEETCODE_REPO_NAME)
      except github.GithubException.UnknownObjectException as e:
        print(str(e)+": repo does not exist")

    return self.repo

  """
  Takes a dict of problem_name to (language, code_content) and commits the code in a file <problem_name>.<ext>
  """
  def commit(self, latest_accepted_submissions):
    for k, v in latest_accepted_submissions.items():
      problem_name = k
      language = v[0]
      code_contents = v[1]

      filename = problem_name + language_to_file_extension(language)

      # Try creating files first as it is more likely submissions will be made for new problems
      try:
        self.repo.create_file(filename, "Create "+filename, code_contents)
      except github.GithubException.GithubException:
        # File already exists
        contents = self.repo.get_content(filename)
        self.repo.update_file(contents.path, "Update "+filename, code_contents, contents.sha)
