from getpass import getpass
from time import sleep
import sys
import logging
import pdb
# from pprint import pprint as pp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common import exceptions
from selenium.webdriver.support.ui import WebDriverWait
from .credentials import Credentials

logger = logging.getLogger(__name__)

def set_chrome_options():
    """Sets chrome options for Selenium.
    Chrome options for headless browser is enabled.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_prefs = {}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    return chrome_options


"""
Scrapes leetcode for your latest accepted submissions
"""
class LeetcodeScraper:
    def __init__(self):
        self.driver = webdriver.Chrome(options=set_chrome_options())
        self.latest_accepted_submissions = {}  # problem_name -> (accepted_url, language, code)
        self.accepted_submission_urls = {}  # e.g. https://leetcode.com/submissions/detail/303813534/


    """
    Login to leetcode with github creds and wait for users homepage
    """
    def login_via_github(self, credentials):
        logger.debug("Logging into Leetcode via Github...")

        self.driver.get("https://leetcode.com/accounts/github/login/?next=%2F")

        self.driver.find_element_by_name("login").send_keys(credentials.get_username())
        self.driver.find_element_by_name("password").send_keys(credentials.get_password())
        self.driver.find_element_by_class_name("btn-primary").click()

        # wait for response
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "navbar-root"))
            )
        except (exceptions.NoSuchElementException, exceptions.TimeoutException):
            logger.error("Login failed, TERMINATING")
            self.driver.close()
            sys.exit(1)


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
    Get dict of problem name to code submissions accepted from progress url
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
        self.__populate_submissions(accepted_submissions_table)


    """
    Get dict of problem name to code submissions accepted from submissions urls
    """
    def scrape_accepted_submissions(self):
        submissions_page = 1

        while True:
            url = "https://leetcode.com/submissions/#/{}".format(submissions_page)

            self.driver.get(url)

            # wait for response
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "submission-list-app"))
                )
            except (exceptions.NoSuchElementException, exceptions.TimeoutException):
                logger.error("Submissions page {} did not load, exit".format(submissions_page))
                sys.exit(1)

            sleep(10)
            table_elements = self.driver.find_elements_by_xpath("//table")
            if len(table_elements) == 0:
                logger.info("Submissions tables finished")
                return

            logger.debug("Successfully loaded {}".format(url))

            submissions_table = table_elements[0]
            self.__populate_submissions(submissions_table)

            submissions_page += 1


    def __populate_submissions(self, submissions_table):
        new_accepted_urls = []
        for row in submissions_table.find_elements_by_xpath("//tbody/tr"):
            data_elements = row.find_elements_by_xpath(".//td")

            text_success_elements = data_elements[2].find_elements_by_class_name("text-success")
            if len(text_success_elements) > 0:
                accepted_url = text_success_elements[0].get_attribute("href")

                if accepted_url in self.accepted_submission_urls:
                    logger.info("Already scraped %s", accepted_url)
                    #break  # submissions are ordered in most recent first so once we have seen one already we move on
                else:
                    logger.info("Not yet scraped %s", accepted_url)
                    self.accepted_submission_urls[accepted_url] = True
                    new_accepted_urls += [accepted_url]

        for url in new_accepted_urls:
            pdb.set_trace()
            self.driver.get(url)

            logger.debug("Getting latest submission %s", url)

            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//h3[text() = 'Submission Detail']")
                    )
                )
            except (exceptions.NoSuchElementException, exceptions.TimeoutException):
                logger.error("Submission page %s failed to load", url)
                return

            problem_url = self.driver.find_element_by_xpath("//h4/a").get_attribute("href")[:-1]
            problem_name = problem_url[problem_url.rfind('/') + 1:]  # https://leetcode.com/problems/A/ -> A
            if problem_name in self.latest_accepted_submissions:
                continue # we will only take the latest submission for now assuming it is the latest and greatest

            language = self.driver.find_element_by_id("result_language").text

            code = ""
            ace_lines = self.driver.find_elements_by_class_name("ace_line")
            for l in ace_lines:
                code += l.text + '\n'

            self.latest_accepted_submissions[problem_name] = (url, language, code)


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
