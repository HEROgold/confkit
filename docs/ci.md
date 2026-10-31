# CI workflows

Every check runs from one workflow, `.github/workflows/ci.yml`. Its first job, `changes`, compares the push or PR against `.github/ci-filters.yml`. Each check only starts when one of its inputs changed, so a docs-only PR doesn't run the tests.

## Workflow files

| File | What it does | Runs when these change |
|---|---|---|
| `ci.yml` | Decides which checks run, then calls them in order. | Every push and PR to `master` |
| `test.yml` | Runs pytest on Python 3.11 to 3.14, and imports the built wheel with only its declared dependencies. | `src/`, `tests/`, `pyproject.toml`, `uv.lock` |
| `lint.yml` (lint) | Runs ruff, ty and undersort on the package. | `src/`, `tests/`, `examples/`, `ruff.toml`, `pyproject.toml`, `uv.lock` |
| `lint.yml` (lint-public) | Runs ruff, ty, pyrefly, zuban, mypy and pyright on `examples/`, the way users call the public API. | `src/`, `examples/`, `ruff.toml`, `pyproject.toml`, `uv.lock` |
| `gitleaks.yml` | Scans the history for leaked secrets. | Every push and PR |
| `docs.yml` | Builds this site. | `src/`, `docs/`, `zensical.toml`, `mkdocs.yml`, `pyproject.toml`, `uv.lock` |
| `docs-publish.yml` | Publishes the built site, as a PR preview or to the root for `master`. It isn't a check, so `all-checks` doesn't wait on it. | Whenever the docs build passed, and when a PR closes |
| `coverage.yml` | Uploads coverage to Coveralls. It's informational, so nothing waits on it. | `src/`, `tests/`, `examples/`, `pyproject.toml`, `uv.lock` |
| `bump-version-by-labels.yml` | Opens a version bump PR from the merged PR's `Major`, `Minor` or `Patch` label. | Pushes to `master` |
| `release.yml` | Tags and releases a version that has no tag yet, then triggers `pypi.yml`. | Pushes to `master` |
| `pypi.yml` | Builds the package and publishes it to PyPI. | A release from `release.yml` |

A change to `ci.yml`, `ci-filters.yml` or `.github/actions/setup/` reruns every check.

Test, lint, coverage and the docs build also cache their result. The cache key hashes the check's inputs, `uv.lock` and its workflow files. On a hit, the check skips its heavy steps, because these exact inputs already passed. The `lint` dependency group pins every lint tool, so a tool upgrade changes `uv.lock` and the key.

## When a PR is opened or updated

```mermaid
flowchart TD
    open([PR opened, updated or reopened]) --> changes[changes: compare against ci-filters.yml]
    open --> gitleaks[gitleaks]
    changes -->|test inputs changed| test[test: pytest 3.11 to 3.14, clean install]
    changes -->|lint inputs changed| lint[lint: ruff, ty, undersort]
    changes -->|lint-public inputs changed| lintpub[lint-public: six type checkers on examples]
    changes -->|docs inputs changed| build[docs build]
    build -->|PR from this repo| preview[docs-publish: preview at gh-pages/pr-previews/pr-n, link in a comment]
    test --> all[all-checks]
    lint --> all
    lintpub --> all
    gitleaks --> all
    build --> all
    all --> result([PR shows pass or fail])
```

A check whose inputs didn't change is skipped, and `all-checks` counts a skipped check as passed. `all-checks` fails only when a check failed or was cancelled, which makes it the one check to require in branch protection.

A newer push to the same PR cancels the older run. PRs from forks build the docs but get no preview, because their token can't push to `gh-pages`.

Publishing runs in one concurrency group per PR and one for `master`, so each PR's preview and the main docs never cancel each other. Previews only write inside `pr-previews/`, so they never change the main docs.

## When a PR is closed

```mermaid
flowchart TD
    closed([PR closed or merged]) --> remove[docs-publish: delete gh-pages/pr-previews/pr-n]
```

No checks run on close. A merged PR also starts the push flow below.

## When a PR is merged to master

```mermaid
flowchart TD
    push([Push to master]) --> changes[changes: compare against ci-filters.yml]
    push --> gitleaks[gitleaks]
    changes -->|test inputs changed| test[test]
    changes -->|lint inputs changed| lint[lint]
    changes -->|lint-public inputs changed| lintpub[lint-public]
    changes -->|docs inputs changed| build[docs build]
    changes -->|coverage inputs changed| coverage[coverage: upload to Coveralls]
    build --> deploy[docs-publish: publish to the gh-pages root, keeping pr-previews]
    test --> all[all-checks]
    lint --> all
    lintpub --> all
    gitleaks --> all
    build --> all
    all -->|passed| bump[bump: read the merged PR's label]
    bump -->|Major, Minor or Patch| bumppr[open a bump PR]
    bump --> release[release: is the version in pyproject.toml tagged?]
    release -->|no tag yet| tag[create the tag and GitHub release]
    tag --> pypi[pypi.yml: build and publish to PyPI]
    release -->|already tagged| done([done])
```

The release job also creates a Sentry release on every run, whether or not the version is new.

Coverage runs next to the checks but isn't part of the chain, so a Coveralls problem never blocks a release.

Each push to `master` gets its own run, so a quick series of merges can't cancel a run and lose its version bump.

## How a release happens

A release takes two merges.

```mermaid
sequenceDiagram
    participant Dev as You
    participant CI as ci.yml on master
    participant Bump as bump PR
    Dev->>CI: merge a PR labelled Minor
    CI->>Bump: all-checks passed, open "bump version to 2.3.0"
    CI->>CI: release finds 2.2.0 already tagged and stops
    Dev->>CI: merge the bump PR
    CI->>CI: the bump PR has no label, so bump does nothing
    CI->>CI: release finds 2.3.0 untagged, tags it and publishes to PyPI
```

The first merge only opens the bump PR, because the version on `master` hasn't changed yet. Merging the bump PR changes `pyproject.toml`, and the run for that push releases it.
