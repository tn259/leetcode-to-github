from getpass import getpass
import sys
import logging
# import pdb
# from pprint import pprint as pp
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common import exceptions
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)

"""
Scrapes leetcode for your latest accepted submissions
"""
class LeetcodeScraper:
    def __init__(self):
        self.driver = webdriver.Firefox()
        self.latest_accepted_submissions = {}  # problem_name -> (accepted_url, language, code)
        self.accepted_submission_urls = []  # e.g. https://leetcode.com/submissions/detail/303813534/

    """
    Login to leetcode and wait for users homepage
    """
    def login(self):
        logger.debug("Logging into Leetcode...")

        self.driver.get("https://leetcode.com/accounts/login")

        username = input("Leetcode username: ")
        password = getpass()

        self.driver.find_element_by_name("login").send_keys(username)
        self.driver.find_element_by_name("password").send_keys(password)
        self.driver.find_element_by_class_name("btn__2FMG").click()

        # wait for response
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "nav-user-app"))
            )
        except (exceptions.NoSuchElementException, exceptions.TimeoutException):
            logger.warning("Login failed, TERMINATING")
            self.driver.close()
            sys.exit(1)

        logger.debug("Login Success!")

    """
    Get dict of problem name to code submissions accepted
    """
    def scrape_latest_accepted_submissions(self):
        self.driver.get("https://leetcode.com/progress")

        logger.debug("Requesting progress page")

        # wait for response
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "submission-status"))
            )
        except (exceptions.NoSuchElementException, exceptions.TimeoutException):
            logger.error("Progress page failed to load, stop scraping")
            return

        logger.debug("Progress page loaded")

        accepted_submissions_table = self.driver.find_element_by_xpath("//table[@id='recent_ac_list']")

        problem_names_to_accepted_urls = {}
        for row in accepted_submissions_table.find_elements_by_xpath(".//tbody/tr"):

            data_elements = row.find_elements_by_xpath(".//td")

            problem_url = data_elements[1].find_element_by_xpath(".//a").get_attribute("href")
            accepted_url = data_elements[2].find_element_by_class_name("status-accepted").get_attribute("href")

            if accepted_url in self.accepted_submission_urls:
                logger.info("Already scraped %s, problem: %s", accepted_url, problem_url)
                break  # submissions are ordered in most recent first so once we have seen one already we move on

            self.accepted_submission_urls.append(accepted_url)

            problem_url = problem_url[:-1]
            problem_name = problem_url[problem_url.rfind('/') + 1:]  # https://leetcode.com/problems/A/ -> A

            if problem_name not in problem_names_to_accepted_urls:
                problem_names_to_accepted_urls[problem_name] = accepted_url

        for k, v in problem_names_to_accepted_urls.items():
            self.driver.get(v)

            logger.debug("Getting latest submission for %s", k)

            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "/html/body/div[1]/div[3]/div[1]/div/div[2]/h3[text() = 'Submission Detail']")
                    )
                )
            except (exceptions.NoSuchElementException, exceptions.TimeoutException):
                logger.error("Submission page for %s failed to load", k)
                return

            language = self.driver.find_element_by_id("result_language").text

            code = ""
            ace_lines = self.driver.find_elements_by_class_name("ace_line")
            for l in ace_lines:
                code += l.text + '\n'

            self.latest_accepted_submissions[k] = (v, language, code)

    """
    Have we scraped new accpeted submissions?
    """
    def latest_accepted_submissions_updated(self):
        return len(self.latest_accepted_submissions) > 0

    """
    returns dict of accepted submissions
    """
    def get_latest_accepted_submissions(self):
        return self.latest_accepted_submissions

    """
    clear accepted submissions dict
    """
    def reset_latest_accepted_submissions(self):
        self.latest_accepted_submissions = {}

    """
    set accepted submissions url list
    """
    def set_accepted_submission_urls(self, accepted_submission_urls):
        self.accepted_submission_urls = accepted_submission_urls
