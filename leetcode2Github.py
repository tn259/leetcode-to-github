from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import selenium
from getpass import getpass
import sys
import pdb

class leetcode:
  def __init__(self):
    self.driver = webdriver.Firefox()
    self.loggedIn = False

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
    except selenium.common.exceptions.NoSuchElementException:
      print("Login failed")
      self.driver.close()
      self.loggedIn = False
      sys.exit(1)

    print("Login succeeded")
    self.loggedIn = True

  def scrape_latest_accepted_submissions(self):
    if self.loggedIn:
      self.driver.get("https://leetcode.com/progress")

      print("Getting progress page")

      # wait for response
      try:
        WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "submission-status"))
        )
      except selenium.common.exceptions.NoSuchElementException:
        print("Progress page failed to load")
        return
    
      print("Progress page loaded")

      accepted_submissions_table = self.driver.find_element_by_xpath("//table[@id='recent_ac_list']")

      # TODO only get submissions since last scrape
      problem_urls_to_time_submitted = {}
      for row in accepted_submissions_table.find_elements_by_xpath(".//tbody/tr"):
        data_elements = row.find_elements_by_xpath(".//td")
        datetime_str = data_elements[0].text
        problem_url = data_elements[1].find_element_by_xpath(".//a").get_attribute("href")
        if not problem_url in problem_urls_to_time_submitted:
          problem_urls_to_time_submitted[problem_url] = datetime_str

      for k, v in problem_urls_to_time_submitted.items():
        print(k+" -> "+v)


def main():
  lc = leetcode()
  lc.login()
  lc.scrape_latest_accepted_submissions()

if __name__ == "__main__":
  main()
