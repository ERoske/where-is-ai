"""
May 15+ refresh pipeline: fetch new BLS May 2025 data, regenerate USA artifacts,
compute year-over-year diff, commit + push to repo.

Designed to be run by a scheduled job once BLS publishes oesm25ma.zip.
Idempotent: if 2025 data isn't available yet, exits cleanly with a message.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SCRIPTS = ROOT / "scripts"


def run(cmd, cwd=ROOT):
    print(f"\n>>> {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str))
    if result.returncode != 0:
        print(f"FAIL exit={result.returncode}")
        sys.exit(result.returncode)


def main():
    print("=== May 15+ refresh: fetching latest BLS data ===")
    run([sys.executable, str(SCRIPTS / "fetch_bls_oews.py")])

    cache_25 = DATA_DIR / "oesm25ma.zip"
    if not cache_25.exists():
        print("\n=== May 2025 BLS data not yet available. Exiting cleanly. ===")
        print("Re-run after BLS publishes (scheduled 2026-05-15 at 10am ET).")
        sys.exit(0)

    print("\n=== May 2025 data available. Running full USA pipeline ===")
    run([sys.executable, str(SCRIPTS / "render_usa_heatmap.py")])
    run([sys.executable, str(SCRIPTS / "compose_top10_verticals.py")])
    run([sys.executable, str(SCRIPTS / "compose_vertical_shorts.py")])
    run([sys.executable, str(SCRIPTS / "year_over_year_diff.py")])

    print("\n=== Committing and pushing to GitHub ===")
    run(["git", "add", "."])
    # Public repo: keep commit message bare. No Co-Authored-By trailers, no Claude footers.
    run([
        "git",
        "commit",
        "-m",
        "Refresh USA data with BLS May 2025 release (year-over-year update)",
    ])
    run(["git", "push"])

    print("\n=== Done. New data published. ===")
    print("Files updated:")
    print(f"  data/usa_ai_employment_by_msa.csv  (now May 2025 data)")
    print(f"  data/usa_findings.md")
    print(f"  data/usa_ai_employment_yoy.csv  (year-over-year)")
    print(f"  data/usa_yoy_findings.md")
    print(f"  images/Heatmap-USA-AI-Jobs.png")
    print(f"  images/USA-Top-10-AI-Cities-Vertical.png")
    print(f"  images/Heatmap-USA-AI-Jobs-Vertical.png")


if __name__ == "__main__":
    main()
