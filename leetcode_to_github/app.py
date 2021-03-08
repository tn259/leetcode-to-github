from time import sleep
import sys
import logging
import schedule
from .credentials import Credentials
from .leetcode_scraper import LeetcodeScraper
from .github_repo_handler import GithubRepoHandler


logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

class LeetcodeToGithub:

    @staticmethod
    def iteration(lc_scraper, gt_repo_handler):
        logger.debug("Scraping Leetcode for latest accepted submissions...")
        lc_scraper.scrape_accepted_submissions()
        latest = lc_scraper.get_latest_accepted_submissions()

        logger.debug("Committing latest accepted submissions to Github...")
        gt_repo_handler.commit(latest)
        lc_scraper.reset_latest_accepted_submissions()

    @staticmethod
    def start_up():
        # Get github creds
        github_credentials = Credentials()
        # setup handle to github repo
        gt_repo_handler = GithubRepoHandler(github_credentials)
        if not gt_repo_handler.repo_exists():
            gt_repo_handler.create_repo()

        # setup and get committed submission urls from github into
        # leetcode_scraper to remember where we left off since the last run
        lc_scraper = LeetcodeScraper()
        # pdb.set_trace()
        lc_scraper.set_accepted_submission_urls(
            gt_repo_handler.get_commited_accepted_submission_urls()
        )
        lc_scraper.login_via_github(github_credentials)

        logger.debug("Startup complete")

        return lc_scraper, gt_repo_handler

    @staticmethod
    def run():
        lc_scraper, gt_repo_handler = LeetcodeToGithub.start_up()

        schedule.every(1).minutes.do(LeetcodeToGithub.iteration, lc_scraper, gt_repo_handler)

        # go
        while True:
            # Schedule every X hours/days
            schedule.run_pending()
            sleep(10)
