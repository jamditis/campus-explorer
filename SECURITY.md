# Security policy

## Reporting a vulnerability

Please report security problems privately through [GitHub's private vulnerability reporting](https://github.com/jamditis/campus-explorer/security/advisories/new). Do not open a public issue for them.

## Scope

Campus explorer is a static site (three.js viewer and GLB files on GitHub Pages) plus Blender and Python scripts. There is no backend, no database, no user accounts, no forms, no cookies and no analytics. The main concerns are:

- **Supply chain.** Viewer libraries are vendored in `vendor/` rather than loaded from a CDN. GitHub Actions are kept current by Dependabot and scanned by CodeQL.
- **Secrets.** Secret scanning and push protection are on. No tokens or credentials belong in the repo.
- **Data that must not be published.** Reference photos, ortho/aerial imagery, LiDAR rasters and `.blend` files are blocked by `.gitignore` and the `repo-guard` check. If you find one committed, report it privately the same way.

## Response time

I'll acknowledge reports within 48 hours and aim to resolve confirmed vulnerabilities within 7 days.
