import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def scrape_smcaen_matches(annee_debut, annee_fin, delay_seconds=0.8, timeout=20):
    """Scrape SM Caen matches over a season range and return a DataFrame."""
    if annee_debut > annee_fin:
        raise ValueError("Start year must be less than or equal to end year")

    all_matches = []

    for annee in range(annee_debut, annee_fin + 1):
        saison = f"{annee}-{annee + 1}"
        url = f"https://www.smcaen.fr/calendrier-resultat/{saison}/premiere/complet"

        try:
            response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
        except requests.RequestException:
            time.sleep(delay_seconds)
            continue

        if response.status_code != 200:
            time.sleep(delay_seconds)
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        current_month_year = ""

        for row in soup.find_all("tr"):
            classes = row.get("class", [])

            if "tr-cr-mois" in classes:
                month = row.find("span", class_="rouge")
                year = row.find("span", class_="bleu")
                if month and year:
                    current_month_year = f"{month.text.strip()} {year.text.strip()}"
                continue

            if "tr-cr" not in classes or "tr-cr-mois" in classes:
                continue

            match = _parse_match_row(row, saison, current_month_year)
            if match is not None:
                all_matches.append(match)

        time.sleep(delay_seconds)

    df = pd.DataFrame(all_matches)
    if df.empty:
        return df

    return df


def _parse_match_row(row, saison, current_month_year):
    """Extract match data from an HTML table row."""
    try:
        date_cell = row.find("td", class_="cr-date")
        comp_cell = row.find("td", class_="cr-comp")
        home = row.find("td", class_="cr-dom")
        away = row.find("td", class_="cr-ext")
        score_cell = row.find("td", class_="cr-score")

        if not all([date_cell, comp_cell, home, away, score_cell]):
            return None

        day_span = date_cell.find("span", class_="l")
        date_spans = date_cell.find_all("span")
        if day_span is None or not date_spans:
            return None

        day_number = day_span.text.strip()
        time_str = date_spans[-1].text.strip()
        full_date = f"{day_number} {current_month_year}".strip()

        comp_span = comp_cell.find("span", class_="joue")
        competition = comp_span.text.strip() if comp_span else comp_cell.text.strip()

        home_txt = home.text.strip()
        away_txt = away.text.strip()
        score = score_cell.text.strip()

        # Ignore unplayed matches ("coming soon", "postponed", etc.)
        goals = re.findall(r"\d+", score)
        if len(goals) < 2:
            return None

        home_goals = int(goals[0])
        away_goals = int(goals[1])

        if _is_caen_team(home_txt):
            opponent = away_txt
            goals_for = home_goals
            goals_against = away_goals
            location = "Home"
        elif _is_caen_team(away_txt):
            opponent = home_txt
            goals_for = away_goals
            goals_against = home_goals
            location = "Away"
        else:
            # Safety: if row is not about Caen, ignore it.
            return None

        if goals_for > goals_against:
            result = "Win"
        elif goals_for < goals_against:
            result = "Loss"
        else:
            result = "Draw"

        return {
            "Season": saison,
            "Date": full_date,
            "Time": time_str,
            "Competition": competition,
            "Home": home_txt,
            "Away": away_txt,
            "Score": score,
            "Opponent": opponent,
            "Goals_For": goals_for,
            "Goals_Against": goals_against,
            "Location": location,
            "Result": result,
        }
    except AttributeError:
        return None


def _is_caen_team(team_name):
    """Detect common variations of SM Caen name."""
    normalized = team_name.strip().lower()
    return "caen" in normalized or "malherbe" in normalized or normalized == "smc"
