from .leetcode_scraper import LeetcodeScraper
from .github_repo_handler import GithubRepoHandler
from time import sleep

class LeetcodeToGithub:

    @staticmethod
    def run():
      print("Hello World...")
      return
      # setup handle to github repo
      gt_repo_handler = GithubRepoHandler()
      if not gt_repo_handler.repo_exists():
        gt_repo_handler.create_repo()

      # setup and get committed submission urls from github into leetcode_scraper to remember where we left off since the last run
      lc_scraper = LeetcodeScraper()
      #pdb.set_trace()
      lc_scraper.set_accepted_submission_urls(
        gt_repo_handler.get_commited_accepted_submission_urls()
        )
      lc_scraper.login()

      # go
      while True:
        # Schedule every X hours/days
        lc_scraper.scrape_latest_accepted_submissions()
        latest = lc_scraper.get_latest_accepted_submissions()

        gt_repo_handler.commit(latest)
        lc_scraper.reset_latest_accepted_submissions()

        exit(0)

        sleep(5)
