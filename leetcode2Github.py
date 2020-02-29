from leetcode_scraper import LeetcodeScraper
from github_repo_handler import GithubRepoHandler

def main():
  #lc_scraper = LeetcodeScraper()
  #lc_scraper.login()
  #lc_scraper.scrape_accepted_submissions()

  gt_repo_handler = GithubRepoHandler()
  if not gt_repo_handler.repo_exists():
    gt_repo_handler.create_repo()




if __name__ == "__main__":
  main()
