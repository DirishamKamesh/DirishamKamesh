#!/usr/bin/env python3
"""
fetch_contributions.py
Scrapes public GitHub contribution data for DirishamKamesh.
No token or credentials needed — uses the public contributions endpoint.
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

import requests
from bs4 import BeautifulSoup

USERNAME = "DirishamKamesh"
CONTRIBUTIONS_URL = f"https://github.com/users/{USERNAME}/contributions"
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "contributions.json")


def fetch_html():
    """Fetch the contribution calendar HTML from GitHub."""
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; contribution-scraper/1.0)",
        "Accept": "text/html",
    }
    resp = requests.get(CONTRIBUTIONS_URL, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_contributions(html):
    """Parse contribution data from the HTML calendar."""
    soup = BeautifulSoup(html, "html.parser")

    # Find all contribution day cells
    cells = soup.find_all("td", class_="ContributionCalendar-day")

    days_data = []
    for cell in cells:
        date_str = cell.get("data-date")
        level = int(cell.get("data-level", 0))
        if not date_str:
            continue

        # Try to extract exact count from the tooltip
        count = 0
        cell_id = cell.get("id", "")
        if cell_id:
            tooltip = soup.find("tool-tip", attrs={"for": cell_id})
            if tooltip:
                tooltip_text = tooltip.get_text(strip=True)
                match = re.search(r"(\d+)\s+contribution", tooltip_text)
                if match:
                    count = int(match.group(1))
                # "No contributions" → count stays 0

        # Parse the date to get weekday
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        weekday = dt.weekday()  # 0=Mon ... 6=Sun
        # GitHub uses Sun=0, so convert
        github_weekday = (weekday + 1) % 7  # 0=Sun, 1=Mon, ..., 6=Sat

        days_data.append({
            "date": date_str,
            "level": level,
            "count": count,
            "weekday": github_weekday,
        })

    # Sort by date
    days_data.sort(key=lambda d: d["date"])

    return days_data


def organize_into_weeks(days_data):
    """Organize daily data into weeks (columns) for the heatmap grid."""
    if not days_data:
        return []

    weeks = []
    current_week = []

    for day in days_data:
        dt = datetime.strptime(day["date"], "%Y-%m-%d")
        day_of_week = dt.weekday()
        # GitHub weeks start on Sunday
        github_dow = (day_of_week + 1) % 7  # 0=Sun

        if github_dow == 0 and current_week:
            weeks.append(current_week)
            current_week = []

        current_week.append(day)

    if current_week:
        weeks.append(current_week)

    return [{"week_index": i, "days": w} for i, w in enumerate(weeks)]


def compute_statistics(days_data):
    """Compute derived statistics from contribution data."""
    total = sum(d["count"] for d in days_data)
    active_days = sum(1 for d in days_data if d["count"] > 0)

    # Streaks
    current_streak = 0
    longest_streak = 0
    streak = 0

    # Sort by date for streak computation
    sorted_days = sorted(days_data, key=lambda d: d["date"])

    for day in sorted_days:
        if day["count"] > 0:
            streak += 1
            longest_streak = max(longest_streak, streak)
        else:
            streak = 0

    # Current streak: count backwards from most recent day
    current_streak = 0
    for day in reversed(sorted_days):
        if day["count"] > 0:
            current_streak += 1
        else:
            break

    # Best day
    best_day = {"date": "", "count": 0}
    for day in sorted_days:
        if day["count"] > best_day["count"]:
            best_day = {"date": day["date"], "count": day["count"]}

    # Monthly totals
    monthly = {}
    for day in sorted_days:
        month_key = day["date"][:7]  # YYYY-MM
        monthly[month_key] = monthly.get(month_key, 0) + day["count"]

    return {
        "total_contributions": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "active_days": active_days,
        "monthly_totals": monthly,
    }


def main():
    print(f"Fetching contributions for {USERNAME}...")
    html = fetch_html()

    print("Parsing contribution data...")
    days_data = parse_contributions(html)
    print(f"  Found {len(days_data)} days of data")

    weeks = organize_into_weeks(days_data)
    stats = compute_statistics(days_data)

    result = {
        "username": USERNAME,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        **stats,
        "weeks": weeks,
    }

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to {OUTPUT_PATH}")
    print(f"  Total contributions: {stats['total_contributions']}")
    print(f"  Current streak: {stats['current_streak']} days")
    print(f"  Longest streak: {stats['longest_streak']} days")
    print(f"  Best day: {stats['best_day']['date']} ({stats['best_day']['count']} contributions)")
    print(f"  Active days: {stats['active_days']}")


if __name__ == "__main__":
    main()
