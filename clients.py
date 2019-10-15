import requests
import json

from models import Athlete, Team


def get_athletes(teams):
    response = requests.get("https://api.cartolafc.globo.com/atletas/mercado")
    athletes = json.loads(response.content)
    athletes = athletes["atletas"]
    athletes = [Athlete(athlete, teams) for athlete in athletes]
    return athletes


def get_teams():
    response = requests.get("https://api.cartolafc.globo.com/clubes")
    teams = json.loads(response.content)
    teams = teams.values()
    teams = [Team(team) for team in teams]
    teams_dict = {}
    for team in teams:
        teams_dict[team.id] = team
    return teams_dict