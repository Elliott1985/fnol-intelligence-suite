# Claims Intake — Demo

🚀 **[Live Demo](https://claims-intake-demo.netlify.app)**

A static HTML/JS frontend for the Claims Intake platform, connecting to a
FastAPI backend hosted on Render.

| URL | What it is | Who uses it |
|---|---|---|
| `/` | Intake form with login and multi-step claim flow | Policyholders, prospects |
| `/dashboard.html` | Carrier portal — KPIs, workload, recent claims | Admin / manager |
| `/claim.html?id=<uuid>` | Single-claim work surface | Adjusters |

**Backend API:** https://claims-intake-api.onrender.com

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
