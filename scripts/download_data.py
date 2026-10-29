"""Download the course dataset (raw job postings + skills) into data/raw/.

SUPPORTER VERSION: the 12 free months, plus every newer month of postings
from the supporter link (a new month lands by the 5th). Don't re-run the
curl command from the free lesson: it puts the free version back.

Run it FROM THE REPO ROOT (python scripts/download_data.py): files land in
data/raw/ relative to wherever you run it (~85MB, plus a few MB per supporter
month). Re-running skips files you already have. If `python` isn't found, your
environment isn't activated; `uv run scripts/download_data.py` always works.
"""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urljoin

REPO = "lukebarousse/dbt_Analytics_Engineering_Course"
TAG = "dataset-v1"
BASE = f"https://github.com/{REPO}/releases/download/{TAG}"

MONTHS = [
    "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12",
    "2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06",
]
FILES = [f"raw_job_postings_{m}.parquet" for m in MONTHS] + ["raw_job_skills.parquet"]

SUPPORTER_URL = "https://lukeb.co/dbt-supporter-data"   # short link to the supporter manifest

DATA_DIR = Path.cwd() / "data" / "raw"   # relative to where you RUN it

if __name__ == "__main__":
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        dest = DATA_DIR / name
        if dest.exists():
            print(f"  already have {name}")
            continue
        print(f"  downloading {name} ...")
        urllib.request.urlretrieve(f"{BASE}/{name}", dest)
    print(f"Done. {len(FILES)} files in {DATA_DIR}")

    # supporter months: manifest.json lists them, and each file sits next to it
    new = []
    try:
        with urllib.request.urlopen(SUPPORTER_URL) as resp:   # follows the short link
            manifest = json.load(resp)
            manifest_url = resp.geturl()   # the real address, after the redirect
        for month in manifest["supporter"]["months"]:
            for f in month["files"]:
                dest = DATA_DIR / f["name"]
                if f["kind"] != "postings" or dest.exists():
                    continue
                print(f"  downloading {f['name']} ...")
                part = dest.with_suffix(".part")   # the *.parquet glob can't see it yet
                urllib.request.urlretrieve(urljoin(manifest_url, f["name"]), part)
                if part.stat().st_size != f["bytes"]:
                    sys.exit(f"{f['name']} didn't download fully. Run the script again.")
                part.rename(dest)
                new.append(month["month"])
    except (urllib.error.URLError, ValueError) as e:
        sys.exit(f"Supporter download failed ({e}). Try again later. If it keeps failing,\n"
                 "the link may have changed: check the supporter lesson.")
    print(f"Supporter months downloaded: {', '.join(new) or 'none new'}")
