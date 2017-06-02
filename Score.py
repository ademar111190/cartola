#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class Score:
    def __init__(self, args):
        self.turn = int(args["rodada_id"])
        self.point = float(args["pontos"])
        self.average = float(args["media"])
