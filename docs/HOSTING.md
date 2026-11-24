# GitHub and Hosting Guide

## GitHub Upload

The repository is configured to include application code, documentation, the trained model, sample data, Docker configuration, and tests. It deliberately excludes raw downloaded corpora, generated training data, the local SQLite database, exports, Python virtual environments, and caches.

Create an empty GitHub repository named `phishguard-ai`, then run from the project folder:

```powershell
git add .
git commit -m "Initial release of PhishGuard AI"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/phishguard-ai.git
git push -u origin main
```

Before pushing, check what will be uploaded:

```powershell
git status
```

Do not force-add `data/raw/`, `data/training_emails.csv`, `data/phishguard.db`, or `data/exports/` to a public repository.

## Render Deployment

1. Push the repository to GitHub.
2. Sign in to Render and select **New +** > **Blueprint**.
3. Select the GitHub repository. Render detects `render.yaml`.
4. Review the proposed service and create it.
5. When the deployment finishes, open the generated `https://...onrender.com` URL.

The deployment uses Waitress rather than Flask's development server. `PHISHGUARD_DATA_DIR=/var/data` stores history on the mounted Render disk. A persistent disk may require a paid Render plan; without it, history can be lost whenever the service restarts.

## Docker Deployment

```powershell
docker build -t phishguard-ai .
docker run --rm -p 5000:5000 -v "${PWD}/runtime-data:/var/data" -e PHISHGUARD_DATA_DIR=/var/data phishguard-ai
```

Open `http://127.0.0.1:5000`.
