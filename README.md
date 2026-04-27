# 2026 Golf Pool — Live Standings

Automated standings page for the 2026 Golf Pool.  
Live URL (once set up): `https://YOUR-USERNAME.github.io/golf-pool-2026/`

---

## How It Works

1. You upload a weekly results file to the `results/` folder in this repo
2. GitHub automatically runs a script that recalculates all standings
3. The website updates within ~60 seconds — no action needed from you

---

## One-Time Setup (do this once)

### Step 1 — Create the GitHub repository

1. Go to [github.com](https://github.com) and sign in
2. Click the **+** button (top right) → **New repository**
3. Name it: `golf-pool-2026`
4. Set it to **Public** (required for free GitHub Pages)
5. Click **Create repository**

### Step 2 — Upload these files

Drag and drop the entire contents of this ZIP into the repo:
- `.github/workflows/update-standings.yml`
- `scripts/generate_standings.py`
- `index.html`
- `data/standings.json`
- `results/` (folder — upload your first results file here)
- `README.md`

Or use the GitHub Desktop app for easier uploading.

### Step 3 — Enable GitHub Pages

1. In your repo, go to **Settings** → **Pages** (left sidebar)
2. Under **Source**, select **Deploy from a branch**
3. Select branch: `main`, folder: `/ (root)`
4. Click **Save**
5. After ~2 minutes, your site will be live at:
   `https://YOUR-USERNAME.github.io/golf-pool-2026/`

### Step 4 — Upload the initial results

1. In your repo, click into the `results/` folder
2. Click **Add file** → **Upload files**
3. Drop in `Golf_Pool_2026_YTD_Tournament_Results.xls`
4. Commit the file — GitHub Actions will fire automatically

---

## Every Week: Adding New Results

When you get the new week's results file:

1. Go to your GitHub repo
2. Click into the `results/` folder
3. Click **Add file** → **Upload files**
4. Upload the new results file (each week is a tab in the XLS, or a separate file)
5. Click **Commit changes**

That's it. The standings page updates automatically within about a minute.

### Results File Format

The script accepts:
- **XLS/XLSX** — one tab per tournament, tab name = tournament name
- **CSV** — one file per tournament, filename = tournament name

Each file must have at minimum these columns:
| Column | Description |
|--------|-------------|
| `Entry Name` | Must match exactly the entry names in the roster |
| `Winnings` | Dollar amount won. Leave blank/NaN for missed cuts, WDs |

Missing entries (no pick submitted) are automatically assessed the −$350,000 penalty.

---

## Scoring Rules Applied Automatically

| Situation | Score |
|-----------|-------|
| Normal finish | Dollar winnings earned |
| Major tournament | Dollar winnings × 1.5 |
| Missed cut / WD / DQ | −$350,000 (−$525,000 for majors) |
| No pick submitted | −$350,000 (−$525,000 for majors) |

---

## Segments

| Segment | Tournaments |
|---------|-------------|
| Segment 1 | Farmers · WM Phoenix · Pebble Beach · Genesis · Cognizant |
| Segment 2 | Arnold Palmer · The Players · Valspar · Houston · Valero TX |
| Segment 3 | The Masters · RBC Heritage · Miami · Truist · PGA Champ. |
| Segment 4 | Byron Nelson · Schwab · Memorial · Canadian Open · US Open |
| Segment 5 | Travelers · John Deere · Scottish Open · The Open · 3M Open |
| Segment 6 | Rocket Mtg. · Wyndham · St. Jude · BMW Champ. |
| Majors | The Masters · PGA Champ. · US Open · The Open (all 1.5×) |
| Small Purse | 14 non-signature, non-major events |

---

## Troubleshooting

**The page isn't updating after I upload results**
- Check the **Actions** tab in your GitHub repo — you'll see the workflow running or any errors
- Make sure the tournament tab name in your XLS matches exactly (see `scripts/generate_standings.py` for the full list)

**An entry name doesn't match**
- Entry names in results must match exactly (case-sensitive) what's in `ACTIVE_ENTRIES` in `generate_standings.py`
- If a name changes, update `ACTIVE_ENTRIES` and `PARTICIPANT_NAMES` in the script
