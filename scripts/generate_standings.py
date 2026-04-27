"""
Golf Pool 2026 — Standings Generator
Reads all tournament result files from results/ folder and outputs data/standings.json
Run automatically by GitHub Actions when new results are uploaded.
"""

import os, json, glob
import pandas as pd
from datetime import datetime, timezone

PENALTY     = -350_000
PENALTY_MAJ = -525_000  # -350,000 * 1.5

TOURNAMENTS = [
    {"name": "Farmers Insurance Open",           "date": "Jan 29",  "short": "Farmers",       "wt": 1.0, "seg": 1, "major": False, "small": True},
    {"name": "Waste Management Phoenix Open",     "date": "Feb 5",   "short": "WM Phoenix",    "wt": 1.0, "seg": 1, "major": False, "small": True},
    {"name": "AT&T Pebble Beach National Pro-Am", "date": "Feb 12",  "short": "Pebble Beach",  "wt": 1.0, "seg": 1, "major": False, "small": False},
    {"name": "Genesis Invitational",              "date": "Feb 19",  "short": "Genesis Inv.",  "wt": 1.0, "seg": 1, "major": False, "small": False},
    {"name": "Cognizant Classic",                 "date": "Feb 26",  "short": "Cognizant",     "wt": 1.0, "seg": 1, "major": False, "small": True},
    {"name": "Arnold Palmer Invitational",        "date": "Mar 5",   "short": "Arnold Palmer", "wt": 1.0, "seg": 2, "major": False, "small": False},
    {"name": "Players Championship",              "date": "Mar 12",  "short": "The Players",   "wt": 1.0, "seg": 2, "major": False, "small": False},
    {"name": "Valspar Championship",              "date": "Mar 19",  "short": "Valspar",       "wt": 1.0, "seg": 2, "major": False, "small": True},
    {"name": "Houston Open",                      "date": "Mar 26",  "short": "Houston",       "wt": 1.0, "seg": 2, "major": False, "small": True},
    {"name": "Valero Texas Open",                 "date": "Apr 2",   "short": "Valero TX",     "wt": 1.0, "seg": 2, "major": False, "small": True},
    {"name": "The Masters",                       "date": "Apr 9",   "short": "The Masters",   "wt": 1.5, "seg": 3, "major": True,  "small": False},
    {"name": "RBC Heritage",                      "date": "Apr 16",  "short": "RBC Heritage",  "wt": 1.0, "seg": 3, "major": False, "small": False},
    {"name": "Miami Championship",                "date": "Apr 30",  "short": "Miami",         "wt": 1.0, "seg": 3, "major": False, "small": False},
    {"name": "Truist Championship",               "date": "May 7",   "short": "Truist",        "wt": 1.0, "seg": 3, "major": False, "small": False},
    {"name": "PGA Championship",                  "date": "May 14",  "short": "PGA Champ.",    "wt": 1.5, "seg": 3, "major": True,  "small": False},
    {"name": "The CJ Cup Byron Nelson",           "date": "May 21",  "short": "Byron Nelson",  "wt": 1.0, "seg": 4, "major": False, "small": True},
    {"name": "Charles Schwab Challenge",          "date": "May 28",  "short": "Schwab",        "wt": 1.0, "seg": 4, "major": False, "small": True},
    {"name": "The Memorial Tournament",           "date": "Jun 4",   "short": "Memorial",      "wt": 1.0, "seg": 4, "major": False, "small": False},
    {"name": "RBC Canadian Open",                 "date": "Jun 11",  "short": "Canadian Open", "wt": 1.0, "seg": 4, "major": False, "small": True},
    {"name": "U.S. Open Championship",            "date": "Jun 18",  "short": "US Open",       "wt": 1.5, "seg": 4, "major": True,  "small": False},
    {"name": "Travelers Championship",            "date": "Jun 25",  "short": "Travelers",     "wt": 1.0, "seg": 5, "major": False, "small": False},
    {"name": "John Deere Classic",                "date": "Jul 2",   "short": "John Deere",    "wt": 1.0, "seg": 5, "major": False, "small": True},
    {"name": "Genesis Scottish Open",             "date": "Jul 9",   "short": "Scottish Open", "wt": 1.0, "seg": 5, "major": False, "small": True},
    {"name": "British Open Championship",         "date": "Jul 16",  "short": "The Open",      "wt": 1.5, "seg": 5, "major": True,  "small": False},
    {"name": "3M Open",                           "date": "Jul 23",  "short": "3M Open",       "wt": 1.0, "seg": 5, "major": False, "small": True},
    {"name": "Rocket Mortgage Classic",           "date": "Jul 30",  "short": "Rocket Mtg.",   "wt": 1.0, "seg": 6, "major": False, "small": True},
    {"name": "Wyndham Championship",              "date": "Aug 6",   "short": "Wyndham",       "wt": 1.0, "seg": 6, "major": False, "small": True},
    {"name": "FedEx St. Jude Championship",       "date": "Aug 13",  "short": "St. Jude",      "wt": 1.0, "seg": 6, "major": False, "small": False},
    {"name": "BMW Championship",                  "date": "Aug 20",  "short": "BMW Champ.",    "wt": 1.0, "seg": 6, "major": False, "small": False},
]

TAB_ALIASES = {
    "AT&T Pebble Beach Pro-Am": "AT&T Pebble Beach National Pro-Am",
}

ACTIVE_ENTRIES = [
    "ADAHMER", "AustinAb", "BALL_IS_LIFE", "BENHAILE", "BIG T",
    "BIRKSBADBOYZ", "CCRICHARDS83", "DILLY DILLY", "D_PRICE", "FRUSCH",
    "Hershiness", "J BROTHERS", "JBSMOOVE", "JBSOUTHERLAND", "KATT MUCHAR",
    "KENBAER", "KNBETHUNE", "KONRADE", "Lane Boy", "MPRICE21",
    "PALACEJ", "RISCHCO", "RYAN4371", "SEAGULL", "STUMPCAT",
    "SWITZ AND GIGGLES", "TCRAWFORD", "THIS FOOL RIGHT HERE", "TSWANY05",
    "Texastank", "Therealjasondufner", "You Only LIV Twice", "larrymahomes",
]


def load_results(results_dir):
    """Load all XLS/CSV result files. Returns:
       scores[entry][tname]  = points (already weighted for positives; penalty applied for majors)
       details[entry][tname] = {"golfer": "First Last", "position": N, "raw": dollars}
    """
    scores  = {e: {} for e in ACTIVE_ENTRIES}
    details = {e: {} for e in ACTIVE_ENTRIES}
    loaded_tournaments = []

    files = (glob.glob(os.path.join(results_dir, "*.xls")) +
             glob.glob(os.path.join(results_dir, "*.xlsx")) +
             glob.glob(os.path.join(results_dir, "*.csv")))

    for fpath in files:
        ext = os.path.splitext(fpath)[1].lower()
        if ext in (".xls", ".xlsx"):
            sheets = pd.read_excel(fpath, sheet_name=None)
        else:
            df = pd.read_csv(fpath)
            sheets = {os.path.splitext(os.path.basename(fpath))[0]: df}

        for tab_name, df in sheets.items():
            # Strip whitespace from column names
            df.columns = [c.strip() for c in df.columns]

            canonical = TAB_ALIASES.get(tab_name, tab_name)
            t_cfg = next((t for t in TOURNAMENTS if t["name"] == canonical), None)
            if t_cfg is None:
                continue

            if canonical not in loaded_tournaments:
                loaded_tournaments.append(canonical)

            is_major = t_cfg["major"]
            penalty  = PENALTY_MAJ if is_major else PENALTY

            result_map = {}
            for _, row in df.iterrows():
                ename = str(row.get("Entry Name", "")).strip()
                if ename not in ACTIVE_ENTRIES:
                    continue

                w    = row.get("Winnings", None)
                fn   = str(row.get("First Name", "")).strip()
                ln   = str(row.get("Last Name",  "")).strip()
                pos  = row.get("Position", None)

                golfer = f"{fn} {ln}".strip() if (fn or ln) else None
                pos_val = int(pos) if pd.notna(pos) else None

                if pd.isna(w):
                    pts = penalty
                    result_map[ename] = {"pts": pts, "golfer": golfer, "position": pos_val, "raw": penalty}
                else:
                    # Winnings already weighted in source file for positives
                    result_map[ename] = {"pts": float(w), "golfer": golfer, "position": pos_val, "raw": float(w)}

            for e in ACTIVE_ENTRIES:
                if e in result_map:
                    r = result_map[e]
                else:
                    # No pick submitted
                    r = {"pts": penalty, "golfer": None, "position": None, "raw": penalty}

                scores[e][canonical]  = r["pts"]
                details[e][canonical] = {"golfer": r["golfer"], "position": r["position"], "raw": r["raw"]}

    return scores, details, loaded_tournaments


def compute_standings(scores, details, loaded_tournaments):

    def build_view(tournament_list):
        played_tnames = [t["name"] for t in tournament_list if t["name"] in loaded_tournaments]
        total_played  = len(played_tnames)

        totals    = {}
        cuts_made = {}
        for e in ACTIVE_ENTRIES:
            total = 0
            cuts  = 0
            for tname in played_tnames:
                p = scores[e].get(tname, 0)
                total += p
                if p > 0:
                    cuts += 1
            totals[e]    = total
            cuts_made[e] = cuts

        ranked = sorted(ACTIVE_ENTRIES, key=lambda e: -totals[e])
        leader_total = totals[ranked[0]] if ranked else 0

        result = []
        prev_total, prev_rank = None, 0
        for i, e in enumerate(ranked):
            rank = prev_rank if totals[e] == prev_total else i + 1
            prev_total, prev_rank = totals[e], rank

            tourn_scores = []
            for t in tournament_list:
                tname = t["name"]
                if tname not in loaded_tournaments:
                    tourn_scores.append({"status": "upcoming", "points": None, "golfer": None, "position": None})
                else:
                    p   = scores[e].get(tname, 0)
                    det = details[e].get(tname, {})
                    if p < 0:
                        status = "penalty"
                    else:
                        status = "scored"
                    tourn_scores.append({
                        "status":   status,
                        "points":   p,
                        "golfer":   det.get("golfer"),
                        "position": det.get("position"),
                    })

            result.append({
                "rank":         rank,
                "entry":        e,
                "total":        totals[e],
                "behind":       totals[e] - leader_total,  # negative = behind
                "cuts_made":    cuts_made[e],
                "total_played": total_played,
                "scores":       tourn_scores,
            })
        return result

    seg_tourns = {
        "seg1":   [t for t in TOURNAMENTS if t["seg"] == 1],
        "seg2":   [t for t in TOURNAMENTS if t["seg"] == 2],
        "seg3":   [t for t in TOURNAMENTS if t["seg"] == 3],
        "seg4":   [t for t in TOURNAMENTS if t["seg"] == 4],
        "seg5":   [t for t in TOURNAMENTS if t["seg"] == 5],
        "seg6":   [t for t in TOURNAMENTS if t["seg"] == 6],
        "majors": [t for t in TOURNAMENTS if t["major"]],
        "small":  [t for t in TOURNAMENTS if t["small"]],
    }

    views = {"overall": build_view(TOURNAMENTS)}
    for key, tlist in seg_tourns.items():
        views[key] = build_view(tlist)

    # Determine completed segments (all tournaments in segment have been played)
    completed_segs = {}
    for key, tlist in seg_tourns.items():
        all_played = all(t["name"] in loaded_tournaments for t in tlist)
        completed_segs[key] = all_played

    return views, completed_segs


def main():
    script_dir  = os.path.dirname(os.path.abspath(__file__))
    repo_root   = os.path.dirname(script_dir)
    results_dir = os.path.join(repo_root, "results")
    data_dir    = os.path.join(repo_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    print(f"Loading results from: {results_dir}")
    scores, details, loaded = load_results(results_dir)
    print(f"Tournaments loaded: {loaded}")

    standings, completed_segs = compute_standings(scores, details, loaded)

    tourn_meta = [
        {
            "name":   t["name"],
            "short":  t["short"],
            "date":   t["date"],
            "wt":     t["wt"],
            "seg":    t["seg"],
            "major":  t["major"],
            "small":  t["small"],
            "played": t["name"] in loaded,
        }
        for t in TOURNAMENTS
    ]

    output = {
        "generated":     datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "tournaments":   tourn_meta,
        "standings":     standings,
        "completed_segs": completed_segs,
    }

    out_path = os.path.join(data_dir, "standings.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Written: {out_path}")


if __name__ == "__main__":
    main()
