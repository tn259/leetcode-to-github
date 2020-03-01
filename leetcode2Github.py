from leetcode_scraper import LeetcodeScraper
from github_repo_handler import GithubRepoHandler

def main():
  # setup handle to github repo
  gt_repo_handler = GithubRepoHandler()
  if not gt_repo_handler.repo_exists():
    gt_repo_handler.create_repo()

  # setup and get committed submission urls from github into leetcode_scraper to remember where we left off since the last run
  #lc_scraper = LeetcodeScraper()
  #lc_scraper.set_accepted_urls(gt_repo_handler.get_commited_accepted_urls())
  #lc_scraper.login()

  # go
  #while True:
    # Schedule every X hours/days
    #latest = lc_scraper.scrape_latest_accepted_submissions()
    #gt_repo_handler.commit(latest)




if __name__ == "__main__":
  main()
