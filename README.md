# Netlify deploy bundle

This folder is the **complete site** to deploy to Netlify. Drag the entire
folder into Netlify's "Deploy manually" area and you'll have three pages
on one domain:

| URL | What it is | Who uses it |
|---|---|---|
| `/` | Intake form (policyholders, prospect demos) | Policyholders, prospects |
| `/dashboard.html` | Carrier portal — KPIs, workload, recent claims | Admin / manager |
| `/claim.html?id=<uuid>` | Single-claim work surface | Adjusters |

## Files

- `index.html` — existing intake demo (drop yours in here)
- `dashboard.html` — carrier dashboard (auto-detects role and shows the right view)
- `claim.html` — claim detail page with file uploads + refresh AI brief

## Deploy

1. Make sure all three files are in this folder.
2. Open https://app.netlify.com → drag this folder (the `netlify-site` folder
   itself, not its contents) onto the deploy area of your existing site
   (or create a new site).
3. Wait for the deploy to finish — usually ~10 seconds.
4. Visit `https://your-site.netlify.app/` to see the intake, and
   `https://your-site.netlify.app/dashboard.html` to see the carrier portal.

## CORS update on Render

Your Render backend's `CORS_ORIGINS` env var must include the Netlify URL
**without** any specific path. So `https://claims-intake-demo.netlify.app`
covers all three pages on that domain.

## Required: drop your existing index.html in here

The `dashboard.html` and `claim.html` files in this folder assume your
existing intake `index.html` (with the Warp-built login flow + multi-step
form) lives alongside them. Copy your existing `index.html` into this
folder before deploying.
