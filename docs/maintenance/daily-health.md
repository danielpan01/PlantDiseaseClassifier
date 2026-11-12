# Plant Disease Classifier daily maintenance report

Checked on **2026-11-12** (America/New_York).

Generated automatically by the daily project health workflow. This is a maintenance observation, not a new research result or full-dataset training run.

**Summary:** 0 failed checks; 0 unverified external checks.

| Check | Status | Observation |
| --- | --- | --- |
| README.md | PASS | Required file exists and is nonempty |
| CITATION.cff | PASS | Required file exists and is nonempty |
| docs/RESEARCH_NOTES.md | PASS | Required file exists and is nonempty |
| docs/assets/research-banner.svg | PASS | Required file exists and is nonempty |
| plantDisease.py | PASS | Required file exists and is nonempty |
| requirements.txt | PASS | Required file exists and is nonempty |
| README.md: CITATION.cff | PASS | Local target exists; fragment not checked |
| README.md: docs/RESEARCH_NOTES.md | PASS | Local target exists; fragment not checked |
| README.md: docs/RESEARCH_NOTES.md#dataset-layout | PASS | Local target exists; fragment not checked |
| README.md: docs/RESEARCH_NOTES.md#evaluation-scope | PASS | Local target exists; fragment not checked |
| README.md: docs/assets/research-banner.svg | PASS | Local target exists; fragment not checked |
| README.md: docs/maintenance/AUTOMATION.md | PASS | Local target exists; fragment not checked |
| README.md: plantDisease.py | PASS | Local target exists; fragment not checked |
| README.md: requirements-dev.txt | PASS | Local target exists; fragment not checked |
| README.md: requirements.txt | PASS | Local target exists; fragment not checked |
| docs/RESEARCH_NOTES.md: ../.gitignore | PASS | Local target exists; fragment not checked |
| docs/RESEARCH_NOTES.md: ../README.md | PASS | Local target exists; fragment not checked |
| docs/RESEARCH_NOTES.md: ../plantDisease.py | PASS | Local target exists; fragment not checked |
| Python syntax: plantDisease.py | PASS | Parsed without importing or executing the application |
| SVG: docs/assets/research-banner.svg | PASS | SVG root and XML structure checked |
| https://doi.org/10.58445/rars.1772 | PASS | HTTP 200; reachability only |
| https://www.kaggle.com/datasets/emmarex/plantdisease | PASS | HTTP 200; reachability only |
| Dependency vulnerability audit | PASS | 74 installed packages audited; no known vulnerabilities reported by PyPI (official PyTorch CPU builds matched to upstream versions) |

## Dependency release watch

Live PyPI metadata compared alongside the declared constraints. The reported latest release may be outside those constraints. This does not resolve installed versions, test compatibility, or upgrade packages. The separate dependency vulnerability audit above checks the installed environment.

| Package | Repository constraint | PyPI latest | Latest release requires Python |
| --- | --- | --- | --- |
| numpy | ==2.4.6 | 2.5.4 | >=3.12 |
| matplotlib | ==3.11.2 | 3.11.2 | >=3.11 |
| torch | ==2.15.0 | 2.15.0 | >=3.11 |
| torchvision | ==0.29.2 | 0.29.2 | !=3.14.1,>=3.10 |
| scikit-learn | ==1.9.1 | 1.9.1 | >=3.11 |
| pillow | ==13.0.0 | 13.0.0 | >=3.11 |
| tqdm | ==4.70.1 | 4.70.1 | >=3.8 |
| transformers | ==5.22.2 | 5.22.2 | >=3.11.0 |

## Scope and history

Checks repository documentation, Python syntax, the SVG banner, publication/dataset link reachability, current PyPI release metadata, and known vulnerabilities in all installed dependencies using pip-audit. The workflow also runs synthetic image/MLP and offline CLIP integration tests. It does not download PlantVillage, perform full-dataset training, or reproduce the historical accuracy claim.

Local link checks cover inline Markdown and HTML file targets; heading fragments and reference-style links are not validated. External checks verify HTTP responses only, not page content. WARN means unverified, not a confirmed broken link.

The current report is replaced after each check; Git history preserves earlier observations. Same-day reruns with identical results produce no new commit.

[Workflow and attribution details](AUTOMATION.md)
