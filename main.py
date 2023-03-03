from requests import get
from bs4 import BeautifulSoup
import re


def get_hs_scores(request):
    state = request.args.get("state")
    city = request.args.get("city")
    school = request.args.get("school")
    sport = request.args.get("sport")
    day = request.args.get("day")

    table_c = "sc-a6604bad-2 gncptz"
    score_c = "sc-f584fccb-0 frvEmC"
    lose_c = "sc-f584fccb-0 cBtcvw"
    win_c = "sc-f584fccb-0 eTgSjp"
    opp_c = "sc-333a63d7-0 rNzPc"
    date_c = ["sc-f584fccb-0", "hYLYjP"]

    date_regex = r"^[a-zA-Z]{3}, (0?[1-9]|1[0-2])/(0?[1-9]|[12][0-9]|3[01])$"

    r = get(f"https://www.maxpreps.com/{state}/{city}/{school}/{sport}/schedule/")
    html = BeautifulSoup(r.text, "html.parser")
    table = html.find("table", {"class": table_c})
    tbody = table.find("tbody")
    trows = tbody.find_all("tr")

    games = []
    for trow in trows:
        score = trow.find("span", {"class": score_c})
        if score:
            score = score.text
            win = trow.find("span", {"class": win_c})
            if win:
                win = win.text
            else:
                win = trow.find("span", {"class": lose_c}).text

        else:
            score = False
            win = False

        opp = trow.find("a", {"class": opp_c}).text
        game_date = trow.find_all("div", {"class": date_c})

        for d in game_date:
            if re.match(date_regex, d.text):
                game_date = d.text
                game_date = game_date.split(",")[1].lstrip()
                month, game_day = game_date.split("/")
                if len(month) == 1:
                    month = "0" + month
                if len(game_day) == 1:
                    game_day = "0" + game_day
                game_date = f"{month}-{game_day}"
                break

        game = {
            "school": school,
            "score": score,
            "win": win,
            "date": game_date,
            "opp": opp,
        }
        games.append(game)

    for game in games:
        if game["date"] in day:
            if game["win"] and game["score"]:
                if game["win"] == "W":
                    win_lose = "beat"
                else:
                    win_lose = "lost to"
                message = f"{game['school']} {win_lose} {game['opp']} {game['score']} on {game['date']}"
                return message
    return "No score found :("
