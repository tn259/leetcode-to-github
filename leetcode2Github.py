from leetcode_scraper import LeetcodeScraper

def main():
  lc = LeetcodeScraper()
  lc.login()
  lc.scrape_accepted_submissions()

if __name__ == "__main__":
  main()
