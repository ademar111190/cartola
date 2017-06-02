#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json


def get_teams():
    response = requests.get("https://api.cartolafc.globo.com/clubes")
    teams = json.loads(response.content)
    teams = teams.values()
    teams = [Team(team) for team in teams]
    teams_dict = {}
    for team in teams:
        teams_dict[team.id] = team
    return teams_dict


class Team:
    def __init__(self, args):
        self.id = int(args["id"])
        self.name = str(args["nome"])
        self.nick = str(args["abreviacao"])
        self.position = int(args["posicao"] if "posicao" in args else -1)
