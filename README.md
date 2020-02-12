# leetcode2Github
Simple python program or service that polls your leetcode challenge entries and commits them to github

An MVP implemntation will be able to
- Login to github
- Browse to https://leetcode/progress
- Scrape new Successful submissions
- Decide what is new by comparing with local db
- Save new submissions in files with CamelCase of problem name
- Commit to repo with message
- Push to github

On start up steps will need to be taken to create a repository or "connect" to one
by syncing with the master on github and remote on disk.

