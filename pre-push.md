## What to do before you push
### Remove All Debug Code and Make sure the Code Runs
Make sure console logs/print statements are removed. If you have blocks of commented code, delete it (if reasonable) to keep the codebase clean.
### Run All Linters AND CHECKS:
(The checks pick up on things you'll have to manually do)
Backend: `docker exec -it tma_backend bash scripts/fix.sh` and
`docker exec -it tma_backend bash scripts/check.sh`

Frontend: `docker exec -it tma_frontend npm run fix` and 
`docker exec -it tma_frontend npm run check`

Mobile: `cd mobile` then `npm run fix` and `npm run check`
### Run All Tests:
-*Feel free to remove the `:verbose`*-

Backend: `docker exec -it tma_backend poetry run pytest`

Frontend: `docker exec -it tma_frontend npm run test:verbose`

Mobile: `cd mobile` then `npm run test:verbose`
### Make sure Commits are Clean
If you want to add more files or change the commit message to make sure commits are clean do the following.

Change just the message: `git commit -m "New Message" --amend. `

Add/Change Files: Stage your new changes `git add .`  then `git commit --amend` (Combines them with the last commit) 

Then use `git push --force` when pushing
### Rebase with Main
```
# Update main branch
git checkout main
git pull

# Rebase your branch onto latest main
git checkout your-branch
git rebase main

# Continue rebase after resolving conflicts
git add .  # stage the edits you made
git rebase --continue

# Abort rebase if something goes wrong
git rebase --abort
```
### Finally, Push the Commit

## For the PR
Make sure that the "base repository" is **rsciaudo/tma-starter-app** (it usually doesn't default to this, so make sure you check), then choose the desired branch for the "compare:" option.

Please reference Dr. Sarah's [PR Description Template](https://csci373-apps.github.io/spring2026/resources/howto-03-git-workflow) for a guide to writing good PRs.

ONLY do "rebase and merge" after your PR is approved - we don't want merge commits!

### Squash Commits Locally for PR
In order to simplify the commit history, your PR should contain a single commit.
To squash the commits on your branch, do the folllowing:

```
# Make sure you're on your feature branch
git checkout your-branch

# N is the number of commits you made on this branch
git reset --soft HEAD~N

# Make a new commit that describes the feature you implemented
git commit -m "[message goes here]"

# Force push your branch
git push --force
```

Now when you make your PR, there should only be a single commit!