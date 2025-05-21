# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "beautifulsoup4",
#     "requests",
# ]
#
# [tool.uv]
# exclude-newer = "2025-05-21T17:18:40.000901-04:00"
# ///
import csv
import re
from time import sleep

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://basketball.realgm.com/nba/draft/lottery_results/{}"
YEARS = range(1985, 2026)

def parse_percentage(s: str) -> float:
    match = re.search(r"[\d.]+", s)
    assert match, "No match"
    return float(match.group()) / 100

def parse_pick_change(s: str) -> int:
    return int(s.replace("+", "").replace("−", "-"))

def main() -> None:
    with open("data.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "year",
            "pick",
            "team",
            "record",
            "odds",
            "pre_lottery_position",
            "pick_change",
            "player",
        ])

        for year in YEARS:
            print(f"Scraping {year}...")
            url = BASE_URL.format(year)
            res = requests.get(url)
            if res.status_code != 200:
                print(f"Failed to fetch {year}")
                continue

            soup = BeautifulSoup(res.text, "html.parser")
            table = soup.find("table")
            if not table:
                print(f"No table for {year}")
                continue

            rows = table.find_all("tr")[1:]  # skip header
            for row in rows:
                cells = row.find_all("td")
                if len(cells) < 8:
                    continue

                writer.writerow([
                    year,
                    int(cells[0].text.strip()),
                    cells[1].text.strip(),
                    cells[2].text.strip(),
                    parse_percentage(cells[3].text.strip()),
                    int(re.sub(r"(st|nd|rd|th)", "", cells[5].text.strip())),
                    parse_pick_change(cells[6].text.strip()),
                    cells[7].text.strip(),
                ])

            sleep(0.1)

if __name__ == "__main__":
    main()

