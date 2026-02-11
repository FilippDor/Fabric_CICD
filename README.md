# Power BI Visual Testing - Results Dashboard

This branch hosts the auto-generated test results dashboard, deployed to GitHub Pages.

**Live dashboard:** [https://filippdor.github.io/Fabric-UI-testing/report/](https://filippdor.github.io/Fabric-UI-testing/report/)

## What's here

| File | Description |
|------|-------------|
| `report/index.html` | Dashboard with summary stats, report table, and failed pages |
| `report/all_reports_results.json` | Raw test results (JSON) |
| `report/report.html` | Detailed HTML report with embedded screenshots |
| `report/*.png` | Screenshots of failed pages |

## How it's updated

The GitHub Actions pipeline on `main` automatically deploys new results here after every test run. Do not edit this branch manually — it gets overwritten on each deploy.

Source code and documentation: [main branch](https://github.com/FilippDor/Fabric-UI-testing)
