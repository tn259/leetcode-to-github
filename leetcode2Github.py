from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common import exceptions as exceptions
from selenium.webdriver.support.ui import WebDriverWait
import selenium
from getpass import getpass
import sys
import pdb
from pprint import pprint as pp

"""
Scrapes leetcode for your latest accepted submissions
"""
class LeetcodeScraper:
  def __init__(self):
    self.driver = webdriver.Firefox()
    self.loggedIn = False
    self.acceptedSubmissions = {} # name to code as string

  """
  Login to leetcode and wait for users homepage
  """
  def login(self):
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
      print("Login failed")
      self.driver.close()
      self.loggedIn = False
      sys.exit(1)

    print("Login succeeded")
    self.loggedIn = True

  """
  Get latest dict of problem name to code submissions accepted
  """
  def scrape_accepted_submissions(self, latest=False):
    if self.loggedIn:
      self.driver.get("https://leetcode.com/progress")

      print("Getting progress page")

      # wait for response
      try:
        WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "submission-status"))
        )
      except (exceptions.NoSuchElementException, exceptions.TimeoutException):
        print("Progress page failed to load")
        return
    
      print("Progress page loaded")

      accepted_submissions_table = self.driver.find_element_by_xpath("//table[@id='recent_ac_list']")

      problem_names_to_accepted_urls = {}
      for row in accepted_submissions_table.find_elements_by_xpath(".//tbody/tr"):

        data_elements = row.find_elements_by_xpath(".//td")

        # TODO only get submissions since last scrape
        datetime_str = data_elements[0].text
        problem_url = data_elements[1].find_element_by_xpath(".//a").get_attribute("href")
        accepted_url = data_elements[2].find_element_by_class_name("status-accepted").get_attribute("href")

        problem_url = problem_url[:-1]
        problem_name = problem_url[problem_url.rfind('/')+1:] # https://leetcode.com/problems/A/ -> A

        if not problem_name in problem_names_to_accepted_urls:
          problem_names_to_accepted_urls[problem_name] = accepted_url

      for k, v in problem_names_to_accepted_urls.items():
        self.driver.get(v)

        print("Getting latest submission for "+k)

        try:
          WebDriverWait(self.driver, 10).until(
                   EC.presence_of_element_located((By.XPATH, 
                       "/html/body/div[1]/div[3]/div[1]/div/div[2]/h3[text() = 'Submission Detail']"))
          )
        except (exceptions.NoSuchElementException, exceptions.TimeoutException):
          print("Submission page for "+problem+" failed to load")
          return

        code = ""
        ace_lines = self.driver.find_elements_by_class_name("ace_line")
        for l in ace_lines:
          code += l.text + '\n'

        self.acceptedSubmissions[k] = code

      pp(self.acceptedSubmissions)

  """
  Have we scraped new accpeted submissions?
  """
  def accepted_submissions_updated(self):
    return len(self.acceptedSubmissions) > 0

  """
  returns dict of accepted submissions
  """
  def get_accepted_submissions(self):
    return self.acceptedSubmissions

  """
  clear accepted submissions dict
  """
  def reset_accepted_submissions(self):
    self.acceptedSubmissions = {}

def main():
  lc = LeetcodeScraper()
  lc.login()
  lc.scrape_accepted_submissions()

if __name__ == "__main__":
  main()
