# Platypus Affiliated Society Website

Hugo static site for [platypus1917.org](https://platypus1917.org), migrated from WordPress.

## Prerequisites

- **Hugo** v0.157.0 — install via `brew install hugo` (macOS) or see [gohugo.io/installation](https://gohugo.io/installation/)
- **Python 3.12+** (only needed for content migration)
- **Git**

## Local Development

```bash
git clone <repo-url>
cd pas-rewrite

# Start dev server (http://localhost:1313)
hugo server

# Production build (output in public/)
hugo --minify
```

**Note:** Images reference `/uploads/*` paths that are proxied through Netlify to the live WordPress server. In local dev, images will load as long as you have internet access — they're fetched directly from the WP server.

## Pulling Content from WordPress

The migration script fetches content from the WordPress REST API and converts it to Hugo markdown files.

### Setup

```bash
cd scripts
python3 -m venv .venv
source .venv/bin/activate
pip install requests markdownify pyyaml beautifulsoup4
```

### Commands

```bash
# Full download of all content from WP REST API (saves JSON to scripts/data/raw/)
python migrate.py fetch

# Transform fetched JSON into Hugo markdown files in content/
python migrate.py transform

# fetch + transform in one step
python migrate.py all

# Incremental sync — only fetch/transform content modified since last sync
python migrate.py sync

# Sync from a specific date
python migrate.py sync --since 2026-03-01

# Overwrite existing files during sync (protected files still skipped)
python migrate.py sync --force
```

The `fetch` step hits the WP API at `https://platypus1917.org/wp-json/wp/v2` with a 0.25s delay between requests. Raw JSON is saved to `scripts/data/raw/` (gitignored, re-fetchable). The `transform` step reads that JSON and writes Hugo content files.

## Project Structure

```
pas-rewrite/
├── hugo.toml              # Hugo config (6 languages: en/de/el/sq/es/pt)
├── netlify.toml           # Netlify build config + media proxy redirects
├── content/               # Hugo content pages
│   ├── review/            # Platypus Review articles (EN)
│   ├── events/            # Events (EN)
│   ├── chapters/          # Chapter pages (EN)
│   ├── reading-groups/    # Reading group pages (EN)
│   ├── about/             # About pages (EN)
│   ├── de/                # German content
│   └── el/, sq/, es/, pt/ # Other languages
├── layouts/               # Hugo templates (custom theme)
├── assets/                # CSS, JS
├── data/                  # Hugo data files (YAML)
├── i18n/                  # Translation strings (6 languages)
├── static/_redirects      # WordPress URL redirects (2,291 entries)
└── scripts/
    ├── migrate.py         # WP-to-Hugo migration script
    └── data/              # Migration data (raw JSON, curated YAML)
```

## Deployment

Netlify auto-deploys from the main branch. Build command: `hugo --minify`. The live site is at [platypus1917.netlify.app](https://platypus1917.netlify.app).
