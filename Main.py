#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Auth import get_auth
from Athlete import get_athletes
from Enums import Status
from Enums import Position
from Team import get_teams
from gplearn.genetic import SymbolicRegressor


def main():
    escalation = {
        Position.GOALKEEPER: 1,
        Position.DEFENDER: 2,
        Position.SIDE: 2,
        Position.MIDFIELD: 4,
        Position.ATTACKER: 2,
        Position.COACH: 1
    }

    print("Getting auth")
    auth = get_auth()

    print("Getting teams")
    teams = get_teams()

    print("Getting athletes")
    athletes = get_athletes(teams)

    print("Getting scores")
    scores = [athlete.get_row(auth) for athlete in athletes]
    max_length = 0
    for score in scores:
        if len(score) > max_length:
            max_length = len(score)
    fixed_score = []
    for score in scores:
        fixed_score.append([0.0] * (max_length - len(score)) + score)

    generations = 2000
    print("Training using " + str(generations) + " generations. It can take a long time to end")
    est_gp = SymbolicRegressor(
        population_size=5000,
        generations=generations,
        stopping_criteria=0.01,
        p_crossover=0.7,
        p_subtree_mutation=0.1,
        p_hoist_mutation=0.05,
        p_point_mutation=0.1,
        max_samples=0.9,
        verbose=1,
        parsimony_coefficient=0.01,
        random_state=0,
        const_range=(-50., 50.),
        function_set=(
            'add', 'sub', 'mul', 'div', 'sqrt', 'log', 'abs', 'neg', 'inv', 'max', 'min', 'sin', 'cos', 'tan'))
    est_gp.fit([x[:-1] for x in fixed_score], [x[-1] for x in fixed_score])
    predictions = est_gp.predict([x[:-1] for x in fixed_score])

    print("Getting results")
    results = [[athlete, prediction] for athlete, prediction in zip(athletes, predictions)]
    results.sort(key=lambda x: -x[1])
    print("\"Scale\",\"Name\",\"Team\",\"Position\",\"Status\",\"Prediction\"")
    for result in results:
        athlete = result[0]
        prediction = result[1]
        scale = athlete.status == Status.Probable and escalation[athlete.position] > 0
        if scale:
            escalation[athlete.position] = escalation[athlete.position] - 1
        print("\"" +
              ("*" if scale else " ") + "\",\"" +
              athlete.nick + "\",\"" +
              athlete.club.name + "\",\"" +
              str(athlete.position.name) + "\",\"" +
              str(athlete.status.name) + "\"," +
              str(prediction))

    print("Done")


if __name__ == "__main__":
    main()
