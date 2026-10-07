# Collaboration Guide

## 1. Main Branch

`main` is the stable version of the project.

Please do not directly make large experimental changes on `main`.

## 2. Coding Branches

Coding Team members should work on separate branches.

Suggested branch names:

- P1: `p1-data`
- P2: `p2-eda-feature`
- P3: `p3-model`

When the work is ready, open a Pull Request before merging it into `main`.

## 3. Files

Use the following locations:

- Data information → `data/`
- Code / notebooks → `notebooks/`
- Final figures → `results/figures/`
- Final tables → `results/tables/`
- Report → `report/`
- Slides → `slides/`

## 4. File Naming

Use descriptive filenames.

Good:

`feature_correlation.png`

`02_eda_feature_engineering.ipynb`

Avoid:

`final2.png`

`new_final.ipynb`

`test123.ipynb`

## 5. Commit Messages

Use short and meaningful commit messages.

Examples:

`feat: add EDA correlation analysis`

`fix: correct preprocessing logic`

`docs: update README`

`results: add model comparison table`

## 6. Project Status

Update the GitHub Project when starting or finishing a task:

`Todo → In Progress → Review → Done`

## 7. Final Results

Do not independently change final numerical results in the report or slides.

Final figures and tables should be checked against the agreed final results before submission.
