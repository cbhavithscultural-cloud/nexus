# Project Nexus (automatic daily update)
Runs on GitHub Actions at 02:00 IST (20:30 UTC), writes JSON to /data, site reads it. No laptop needed.
## Setup (about 15 minutes)
1. Create a GitHub account, then a new PUBLIC repository named nexus. Upload all these files (drag them in on the web page, keep folder names).
2. Get an Anthropic API key at console.anthropic.com (separate from a chat subscription, billed per use; set a low spend limit).
3. Repo > Settings > Secrets and variables > Actions > New repository secret. Name: ANTHROPIC_API_KEY, value: your key.
4. Repo > Settings > Pages > Source: Deploy from a branch > main > / (root) > Save. Your site URL appears there.
5. Repo > Actions > daily-update > Run workflow. After it turns green, reload your site. Expect status "ok" per section.
## Check tomorrow
Actions tab shows a run near 02:00 IST (GitHub may delay scheduled runs). data/days/ gets one file per day. Re-running the same day does nothing unless FORCE is set.
## Known limits
Not tested by me. Pages may not redeploy after bot commits: if the site stays old after a green run, tell me. GitHub may pause schedules after 60 days without repo activity.
