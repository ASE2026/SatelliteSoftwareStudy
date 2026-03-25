import csv
import os
import time
from datetime import datetime, timedelta

import requests

# ===============================================================================
# GITHUB DATA EXTRACTION CONFIGURATION
# -------------------------------------------------------------------------------
# Generate your Personal Access Token (PAT) here:
# https://github.com/settings/tokens
# ===============================================================================
GITHUB_PAT = "YOUR_GITHUB_PAT"

# Keyword for GitHub Search API
SEARCH_KEYWORD = "satellite"

# Dataset output filename
OUTPUT_FILE = "satellite_repositories.csv"

# GitHub API v3 Endpoints
SEARCH_URL = "https://api.github.com/search/repositories"
REPO_URL = "https://api.github.com/repos/{full_name}"
ISSUE_URL = "https://api.github.com/search/issues"

HEADERS = {
    "Authorization": f"token {GITHUB_PAT}",
    "Accept": "application/vnd.github.v3+json",
}

# FINAL SCHEMA (14 attributes) - FIXED & VERIFIED
COLUMN_ORDER = [
    "repository_name",
    "stars",
    "forks",
    "open_issues_pure",
    "created_at",
    "updated_at",
    "pushed_at",
    "language",
    "license",
    "size_kb",
    "watchers_count",
    "is_archived",
    "description",
    "topics",
]
# ===============================================================================


def get_pure_issue_count(full_name):
    """
    Fetch open issues count (excluding Pull Requests).
    """
    params = {"q": f"repo:{full_name} is:open is:issue"}
    try:
        time.sleep(2.0)  # Search API Rate Limit: 30 requests/min
        resp = requests.get(ISSUE_URL, headers=HEADERS, params=params)
        resp.raise_for_status()
        return resp.json().get("total_count", 0)
    except Exception as e:
        print(f"[ERROR] Could not get issues for {full_name}: {e}")
        return -1


def get_detailed_info(full_name):
    """
    Fetch attributes not available in initial search results.
    """
    try:
        resp = requests.get(REPO_URL.format(full_name=full_name), headers=HEADERS)
        if resp.status_code == 200:
            data = resp.json()
            # Mapping remaining 8 attributes
            return {
                "pushed_at": data.get("pushed_at"),
                "language": data.get("language"),
                "license": data["license"]["spdx_id"] if data.get("license") else None,
                "size_kb": data.get("size"),
                "watchers_count": data.get("subscribers_count"),
                "is_archived": data.get("archived"),
                "description": data.get("description"),
                "topics": ", ".join(data.get("topics", [])),
            }
    except Exception as e:
        print(f"[ERROR] Metadata fetch failed for {full_name}: {e}")
    return {}


def main():
    """
    Main extraction loop. Monthly slices used to bypass 1000 results limit.
    """
    if GITHUB_PAT == "YOUR_GITHUB_PAT" or not GITHUB_PAT:
        print("Please Set Your GitHub Personal Access Token (GITHUB_PAT).")
        return

    start_date = datetime(2008, 1, 1)
    end_date = datetime.now()
    current_it = start_date

    print("--- [Started] ---")
    print(f"[CONF] Keyword: {SEARCH_KEYWORD}")
    print(f"[CONF] Output: {OUTPUT_FILE}")

    # File initialization
    file_exists = os.path.exists(OUTPUT_FILE)
    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMN_ORDER)
        if not file_exists:
            writer.writeheader()

        while current_it < end_date:
            s_str = current_it.strftime("%Y-%m-%d")
            next_month = (current_it.replace(day=28) + timedelta(days=4)).replace(day=1)
            e_str = (next_month - timedelta(days=1)).strftime("%Y-%m-%d")

            print(f"[SEARCH] {s_str} - {e_str}")

            page = 1
            while True:
                params = {
                    "q": f"{SEARCH_KEYWORD} created:{s_str}..{e_str}",
                    "sort": "created",
                    "order": "asc",
                    "per_page": 100,
                    "page": page,
                }

                time.sleep(2.0)
                response = requests.get(SEARCH_URL, headers=HEADERS, params=params)

                if response.status_code == 403:
                    print("[RETRY] Rate limit hit. Sleeping 60s...")
                    time.sleep(60)
                    continue
                elif response.status_code != 200:
                    print(
                        f"[ERROR] API Exception {response.status_code}. Skipping page."
                    )
                    break

                data = response.json()
                items = data.get("items", [])
                if not items:
                    break

                for repo in items:
                    full_name = repo["full_name"]
                    print(f"      > Indexing: {full_name}")

                    # 1. Base search metadata (5 attributes)
                    row = {
                        "repository_name": full_name,
                        "stars": repo["stargazers_count"],
                        "forks": repo["forks_count"],
                        "created_at": repo["created_at"],
                        "updated_at": repo["updated_at"],
                    }

                    # 2. Enrich with 8 more attributes
                    details = get_detailed_info(full_name)
                    row.update(details)

                    # 3. Final attribute: pure issues
                    row["open_issues_pure"] = get_pure_issue_count(full_name)

                    # Persistence: Write immediately to disk
                    writer.writerow(row)
                    f.flush()

                if len(items) < 100:
                    break
                page += 1

            current_it = next_month

    print("--- [Finished] ---")


if __name__ == "__main__":
    main()
