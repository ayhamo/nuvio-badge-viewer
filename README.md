# Nuvio Badge Viewer & Scraper
-- This is a AI-generated Text --

A lightweight viewer and backup utility for Nuvio media animated badge presets hosted on GitHub Gists from https://gist.github.com/darpit33.

He created a cool animated badges but links are getting deleted, so this was made as a backup for me, and others to benefit from



## 👏 Credits & Attribution

* **Original Creator:** All regex configurations, badge designs, and JSON presets are created by [**@darpit33**](https://github.com/darpit33).
* **Source Gists:** [darpit33's GitHub Gists](https://gist.github.com/darpit33)
* **Disclaimer:** This project is an independent community viewer and archival tool created solely for preservation and easy visual inspection. All intellectual credit for the filter logic and badge assets belongs entirely to the original author.



## 🎯 Purpose

Nuvio filter presets are distributed as JSON configuration files that include regex rules, filter groups, and animated GIF badge preview URLs. 

This repository serves two purposes:

1. **Visual Catalog (`index.html`)**: Dynamically fetches every public JSON preset via the GitHub API and renders the animated badge GIFs grouped cleanly by category.
2. **Complete Local Archival (`download_gists.py`)**: A Python utility that downloads all JSON files into a local `json-backup/` directory and pulls every remote GIF into a structured `gif-backup/` directory.



## 📁 Repository Structure

```text
nuvio-badge-viewer/
├── index.html            # Web interface to view animated badges
├── download_gists.py     # Python scraper for JSONs and GIF assets
├── json-backup/          # Local directory for JSON file backups
│   ├── MiniAnimated.json
│   ├── Hua.json
│   └── Se.json
├── gif-backup/           # Offline archive of all GIF icons
│   ├── MiniAnimated/
│   │   ├── Remux_q-r.gif
│   │   ├── BluRay_q-b.gif
│   │   └── ...
│   ├── Hua/
│   │   └── ...
│   └── Se/
│       └── ...
└── README.md