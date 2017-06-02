#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum


class Position(Enum):
    GOALKEEPER = 1
    SIDE = 2
    DEFENDER = 3
    MIDFIELD = 4
    ATTACKER = 5
    COACH = 6


class Status(Enum):
    Probable = 7
    Injured = 5
    Doubt = 2
    Suspended = 3
    Null = 6
