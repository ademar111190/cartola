import requests
import json

from Enums import Position
from Enums import Status


class Team:
    def __init__(self, args):
        self.id = int(args["id"])
        self.name = str(args["nome"])
        self.nick = str(args["abreviacao"])
        self.position = int(args["posicao"] if "posicao" in args else -1)


class Score:
    def __init__(self, args):
        self.turn = int(args["rodada_id"])
        self.point = float(args["pontos"])
        self.average = float(args["media"])


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
