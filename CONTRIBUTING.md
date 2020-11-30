# Contributing

Thank you for your interest in contributing to `photomanager`!

## Pull requests

* PRs should target `master`. (Later, this may be changed to a `development` branch.)
* Please run `isort` then `black` (`pipenv run isort . && pipenv run black .`).
  CI will likely fail if you do not.
* Commit messages should follow the [Conventional Commits standard](https://conventionalcommits.org/) where possible.
* Keep PRs to a minimum; many small PRs is better than one big PR.
  * Before merging, please squash all your commits.
  * I only do rebase merges, so you may need to rebase against the latest `master`:
    ```bash
    git remote add upstream git@github.com:etnguyen03/photomanager.git
    git fetch upstream
    git rebase upstream/master
    git log                     # check to make sure everything looks fine
    git push origin +[BRANCH]   # Force push necessary
    ```
  
