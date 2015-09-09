#!/usr/bin/python2.7

from sqlite3 import connect
from os import listdir
from os.path import isfile, join

connection = connect("cartola.db")
cursor = connection.cursor()

cursor.execute("DROP TABLE projection;")
cursor.execute("CREATE TABLE IF NOT EXISTS projection(id int, score real, valorization real, matches real);")
connection.commit()

mypath = "oldDb"
onlyfiles = [ join(mypath,f) for f in listdir(mypath) if isfile(join(mypath,f)) ]

for f in onlyfiles:
    cursor.execute('attach "{0}" as toMerge'.format(f))
    cursor.execute("insert into score select * from toMerge.score;")
    cursor.execute("detach database toMerge;")
    connection.commit()

# Estimador de Media Movel http://www.ufjf.br/epd042/files/2009/02/previsao1.pdf
def makeProbableNextScore(knowScore):
    matches = len(knowScore)
    base = triangular(matches)
    probability = 0.0
    for i in range(matches):
        weight = (i + 1.0) / base
        value = knowScore[i] * weight
        probability = probability + value
    return probability

data = {}
cursor.execute("SELECT * from score;")
scores = cursor.fetchall()
for score in scores:
    if not score[0] in data:
        data[score[0]] = {}
    data[score[0]][score[2]] = score[1]

def triangular(matches):
    if matches > 0.0:
        return matches + triangular(matches - 1.0)
    else:
        return 1.0

for playerId, playerScore in data.iteritems():
    averages = playerScore.values()
    games = playerScore.keys()
    nextScore = makeProbableNextScore(averages)
    matches = len(averages)
    valorization = 0.0 if matches == 0 else nextScore - averages[-1:][0]
    cursor.execute("INSERT INTO projection VALUES (" + str(playerId) + ", " \
                                                        + str(nextScore) + ", " \
                                                        + str(valorization) + ", " \
                                                        + str(matches) + ");")
    connection.commit()
