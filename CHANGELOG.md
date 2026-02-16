# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-16

### Added

- Automated visual regression testing for Power BI reports using Playwright and headless Chromium.
- Service Principal authentication (OAuth2 client_credentials) for Azure AD.
- Automatic workspace discovery — fetches all reports and datasets via Power BI REST API.
- Row-Level Security (RLS) auto-detection and embed token generation with effective identity.
- Per-page visual rendering validation using Power BI JavaScript SDK events.
- Screenshot capture for failed pages with base64-embedded HTML reports.
- GitHub Actions CI/CD pipeline with artifact upload and GitHub Pages deployment.
- Pre-flight unit tests for environment variables, report metadata, auth, and embed tokens.
- Parallel test execution support via pytest-xdist.
- CLI interface (`fabric-ci-test`) with `init`, `fetch`, `test`, and `report` commands.
- Python API module for programmatic usage.
- GCC High / sovereign cloud support (`gov` environment).
