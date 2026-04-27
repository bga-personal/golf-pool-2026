"""
Golf Pool 2026 — Standings Generator
Reads all tournament result files from results/ folder and outputs data/standings.json
Run automatically by GitHub Actions when new results are uploaded.
"""

import os, json, glob
import pandas as pd
from datetime import datetime

PENALTY = -350_000

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
    "PGA Championship": "PGA Championship",
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

PARTICIPANT_NAMES = {
    "ADAHMER": "Andrew Dahmer", "AustinAb": "Austin Abelbeck",
    "BALL_IS_LIFE": "J.D. Meyer", "BENHAILE": "Benjamin Haile",
    "BIG T": "Theresa Carlson", "BIRKSBADBOYZ": "Brandon Rich",
    "CCRICHARDS83": "Chris Richards", "DILLY DILLY": "Patrick Cowden",
    "D_PRICE": "Daniel Price", "FRUSCH": "Craig Fusch",
    "Hershiness": "Adam Hersh", "J BROTHERS": "Jon Aronson",
    "JBSMOOVE": "Josh Bauer", "JBSOUTHERLAND": "Brayden Southerland",
    "KATT MUCHAR": "B G", "KENBAER": "Ken Baer",
    "KNBETHUNE": "Kenneth Bethune", "KONRADE": "Eric Konrade",
    "Lane Boy": "Your Boy", "MPRICE21": "Matthew Price",
    "PALACEJ": "Justin Palace", "RISCHCO": "Andrew Rische",
    "RYAN4371": "Ryan Lafield", "SEAGULL": "Kyle Siegel",
    "STUMPCAT": "Russell Musgrove", "SWITZ AND GIGGLES": "Steve Switzer",
    "TCRAWFORD": "Trey Crawford", "THIS FOOL RIGHT HERE": "Ryan Swanson",
    "TSWANY05": "Tracy Swanson", "Texastank": "Jimmy Greene",
    "Therealjasondufner": "Matt Kapoulas", "You Only LIV Twice": "Chris Simmons",
    "larrymahomes": "Lawrence Kroenke",
}


def load_results(results_dir):
    """Load all XLS/CSV result files from results/ folder."""
    scores = {e: {} for e in ACTIVE_ENTRIES}
    loaded_tournaments = []

    # Collect all result files
    files = (glob.glob(os.path.join(results_dir, "*.xls")) +
             glob.glob(os.path.join(results_dir, "*.xlsx")) +
             glob.glob(os.path.join(results_dir, "*.csv")))

    for fpath in files:
        ext = os.path.splitext(fpath)[1].lower()
        if ext in (".xls", ".xlsx"):
            sheets = pd.read_excel(fpath, sheet_name=None)
        else:
            df = pd.read_csv(fpath)
            # Assume CSV tab name is the filename stem
            sheets = {os.path.splitext(os.path.basename(fpath))[0]: df}

        for tab_name, df in sheets.items():
            canonical = TAB_ALIASES.get(tab_name, tab_name)
            t_cfg = next((t for t in TOURNAMENTS if t["name"] == canonical), None)
            if t_cfg is None:
                continue  # unknown tab, skip

            if canonical not in loaded_tournaments:
                loaded_tournaments.append(canonical)

            # Build result map
            result_map = {}
            for _, row in df.iterrows():
                ename = str(row.get("Entry Name", "")).strip()
                if ename in ACTIVE_ENTRIES:
                    w = row.get("Winnings", None)
                    result_map[ename] = PENALTY if pd.isna(w) else float(w)

            for e in ACTIVE_ENTRIES:
                raw = result_map.get(e, PENALTY)  # no pick = penalty
                scores[e][canonical] = raw

    return scores, loaded_tournaments


def compute_standings(scores, loaded_tournaments):
    """Compute points (raw * wt) for each entry across all views."""

    def pts(entry, tname):
        raw = scores[entry].get(tname)
        if raw is None:
            return None
        t = next(t for t in TOURNAMENTS if t["name"] == tname)
        return raw * t["wt"]

    def build_view(tournament_list):
        totals = {}
        for e in ACTIVE_ENTRIES:
            total = sum(
                pts(e, t["name"])
                for t in tournament_list
                if t["name"] in loaded_tournaments and pts(e, t["name"]) is not None
            )
            totals[e] = total

        ranked = sorted(ACTIVE_ENTRIES, key=lambda e: -totals[e])
        result = []
        prev_total, prev_rank = None, 0
        for i, e in enumerate(ranked):
            rank = prev_rank if totals[e] == prev_total else i + 1
            prev_total, prev_rank = totals[e], rank

            tourn_scores = []
            for t in tournament_list:
                p = pts(e, t["name"])
                if t["name"] not in loaded_tournaments:
                    tourn_scores.append({"status": "upcoming", "points": None, "raw": None})
                elif p is None:
                    tourn_scores.append({"status": "upcoming", "points": None, "raw": None})
                elif p < 0:
                    tourn_scores.append({"status": "penalty", "points": p, "raw": scores[e].get(t["name"])})
                else:
                    tourn_scores.append({"status": "scored", "points": p, "raw": scores[e].get(t["name"])})

            result.append({
                "rank": rank,
                "entry": e,
                "name": PARTICIPANT_NAMES.get(e, e),
                "total": totals[e],
                "scores": tourn_scores,
            })
        return result

    return {
        "overall": build_view(TOURNAMENTS),
        "seg1": build_view([t for t in TOURNAMENTS if t["seg"] == 1]),
        "seg2": build_view([t for t in TOURNAMENTS if t["seg"] == 2]),
        "seg3": build_view([t for t in TOURNAMENTS if t["seg"] == 3]),
        "seg4": build_view([t for t in TOURNAMENTS if t["seg"] == 4]),
        "seg5": build_view([t for t in TOURNAMENTS if t["seg"] == 5]),
        "seg6": build_view([t for t in TOURNAMENTS if t["seg"] == 6]),
        "majors": build_view([t for t in TOURNAMENTS if t["major"]]),
        "small": build_view([t for t in TOURNAMENTS if t["small"]]),
    }


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    results_dir = os.path.join(repo_root, "results")
    data_dir = os.path.join(repo_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    print(f"Loading results from: {results_dir}")
    scores, loaded = load_results(results_dir)
    print(f"Tournaments loaded: {loaded}")

    standings = compute_standings(scores, loaded)

    # Tournament metadata for the frontend
    tourn_meta = [
        {
            "name": t["name"],
            "short": t["short"],
            "date": t["date"],
            "wt": t["wt"],
            "seg": t["seg"],
            "major": t["major"],
            "small": t["small"],
            "played": t["name"] in loaded,
        }
        for t in TOURNAMENTS
    ]

    output = {
        "generated": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "tournaments": tourn_meta,
        "standings": standings,
    }

    out_path = os.path.join(data_dir, "standings.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Written: {out_path}")


if __name__ == "__main__":
    main()
