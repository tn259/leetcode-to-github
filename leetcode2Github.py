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


def main():
  lc = leetcode()
  lc.login()

if __name__ == "__main__":
  main()
