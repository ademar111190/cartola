#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from Enums import Position
from Enums import Status
from Score import Score


def get_athletes(teams):
    response = requests.get("https://api.cartolafc.globo.com/atletas/mercado")
    athletes = json.loads(response.content)
    athletes = athletes["atletas"]
    athletes = [Athlete(athlete, teams) for athlete in athletes]
    return athletes


class Athlete:
    def __init__(self, args, teams):
        self.id = int(args["atleta_id"])
        self.name = str(args["nome"])
        self.nick = str(args["apelido"])
        self.club = teams[args["clube_id"]]
        self.position = Position(int(args["posicao_id"]))
        self.status = Status(args["status_id"])
        self.points = float(args["pontos_num"])
        self.price = float(args["preco_num"])
        self.variation = float(args["variacao_num"])
        self.average = float(args["media_num"])
        self.games = int(args["jogos_num"])
        self.turn = int(args["rodada_id"])
        self.score = None

    def get_scores(self, auth):
        if self.score is None:
            headers = {'x-glb-token': auth}
            url = "https://api.cartolafc.globo.com/auth/mercado/atleta/" + str(self.id) + "/pontuacao"
            response = requests.get(url, headers=headers)
            scores = json.loads(response.content)
            self.score = [Score(score) for score in scores if score["pontos"] is not None]
        return self.score

    def get_row(self, auth):
        print("\tGetting score of " + self.name)
        self.get_scores(auth)
        return [score.point for score in self.score]
