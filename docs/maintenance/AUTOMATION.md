# Daily project health automation

[Current report](daily-health.md) · [Workflow runs](https://github.com/danielpan01/PlantDiseaseClassifier/actions/workflows/daily-health.yml)

This workflow tests application compatibility, audits installed dependencies, checks repository maintenance items, and commits a dated observation to the repository's default branch. The report is explicitly automated. It does not automatically upgrade packages.

## Checks

Checks repository documentation, Python syntax, the SVG banner, publication/dataset link reachability, current PyPI release metadata, and known vulnerabilities reported by PyPI through `pip-audit --strict`. The audit covers the installed environment, including transitive dependencies and the scanner's dependencies. The helper inventories every installed package, then passes the complete exact-version inventory to `pip-audit --strict --no-deps --disable-pip`. Only the official `+cpu` suffix on torch/torchvision is normalized to its upstream release for PyPI advisory lookup; unknown private builds still fail verification. No advisories are suppressed. The workflow also tests JPEG loading/caching, normalization, real MLP training/evaluation/plotting, the main sweep flow on synthetic data, and offline CLIP inference with locally generated weights. It does not download PlantVillage, perform full-dataset training, or reproduce the historical accuracy claim.

Configure the input files and external URLs in `.github/daily-health.json`. The workflow installs `requirements.txt` and `requirements-dev.txt` on Ubuntu, using PyTorch's official CPU wheel index for CI, then runs `pip check` and the integration tests. Daily checks use Python 3.11; pull requests and pushes to `main` validate Python 3.11 and 3.12. CLIP tests run offline and require no account, dataset, or pretrained-model download.

External documentation checks have 15-second timeouts; an unreachable publication/dataset link is labeled WARN/unverified. Vulnerability scanning has a five-minute timeout and fails closed: a vulnerability, skipped package, malformed/empty result, scanner error, or timeout produces FAIL. Missing files, invalid Python/SVG, and checksum mismatches also fail. The daily workflow publishes the diagnostic report before returning a failure. Installation, dependency compatibility, and test failures stop the run before report generation, so the existing report's date must always be checked against the latest Actions run.

## Schedule

GitHub checks four daytime slots in **America/New_York**: 9:17 a.m., 10:43 a.m., 12:29 p.m., and 2:11 p.m. A deterministic hash of the repository name and local calendar date selects a slot within alternating pairs of times, so adjacent dates choose different slots. This varies the selected time across dates and projects without spending runner minutes sleeping. The other three invocations only evaluate the selector and skip report generation.

Daylight saving time follows the named timezone. GitHub can delay or skip scheduled runs, so a contribution every calendar day is not guaranteed. Manual **Run workflow** on the default branch bypasses the slot selector and runs immediately. If today's results are unchanged, rerunning will not create another commit. Public-repository schedules may be disabled by GitHub after 60 days without repository activity.

## Attribution and publishing

Daniel is the authorized commit author using the existing GitHub-linked address `146807695+danielpan01@users.noreply.github.com`. `github-actions[bot]` is the committer; commit messages explicitly identify automated reports. Commits land on the default branch of this standalone repository and therefore meet GitHub's commit-attribution criteria. GitHub controls profile indexing, which can take up to 24 hours.

Only the report job receives `contents: write` through the automatic `GITHUB_TOKEN`; no personal access token or extra secret is required. It stages only `docs/maintenance/daily-health.md`, uses an ordinary fast-forward push, and will fail rather than overwrite a concurrent change. Rerun manually if a concurrent push rejects publication. Publishing is restricted to schedule/manual events in `danielpan01/PlantDiseaseClassifier` on its default branch. Pull-request validation has read-only permissions and does not persist checkout credentials. Pushes changing only the generated report are ignored to avoid recursion.

Dependabot checks pip packages and GitHub Actions weekly. PyTorch and torchvision updates are grouped because their binary compatibility must be tested together. Proposed updates go through the same application tests and vulnerability audit.

To pause: Actions → Daily project health → menu → Disable workflow. To remove: delete `.github/workflows/daily-health.yml`.

## Local verification

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pip check
python -m unittest discover -s scripts -p 'test_*.py' -v
python scripts/audit_dependencies.py
python scripts/daily_health.py
```

The report uses the actual check date in New York. Same-day identical observations are stable; Git history retains prior dates. A clean audit means no known vulnerabilities were reported for that installed environment at check time; it does not establish absence of unknown flaws or reproduce the research results. Direct dependencies are pinned; transitive resolutions can vary by platform and date and are audited on every run.
