#!/usr/bin/python2.7

from json import loads
from os.path import isfile
from sqlite3 import connect
from getpass import getpass
from mechanize import Browser
from optparse import OptionParser

def parseOptionFormation(option, opt, value, parser):
    setattr(parser.values, option.dest, [int(i) for i in value.split(',')])

parser = OptionParser()
parser.add_option("-u", "--user", dest="user", type="string", help="the cartola username, e.g. -u ademar@mail.com")
parser.add_option("-m", "--maxMoney", dest="maxMoney", type="float", help="the max money allowed to be spent, e.g. -m 100.0")
parser.add_option("-f", "--formation", action="callback", type="string", help="the allowed formations, e.g. -f 442,433", callback=parseOptionFormation)
(options, args) = parser.parse_args()

needCreateDb = not isfile("cartola.db")
password = None

if needCreateDb:
    if not options.user:
        parser.error('You need send an user to load first database')
    password = getpass("enter the password for user " + options.user + ": ")
    if not password:
        parser.error('You need informe your password to sign in')

connection = connect("cartola.db")
cursor = connection.cursor()

if (needCreateDb):
    cursor.execute("CREATE TABLE IF NOT EXISTS score(id int, score real, game int)")
    cursor.execute("CREATE TABLE IF NOT EXISTS projection(id int, score real, valorization real, matches real)")
    cursor.execute("CREATE TABLE IF NOT EXISTS player(id int, name text, position int, price real, status int)")
    connection.commit()

    browser = Browser()
    browser.open("https://loginfree.globo.com/login/438")
    browser.select_form(nr=0)
    browser.form["login-passaporte"] = options.user
    browser.form["senha-passaporte"] = password
    browser.submit()

    status = { "Nulo": 1, "D\xc3\xbavida": 2, "Contundido": 3, "Suspenso": 4, "Prov\xc3\xa1vel": 5 }
    current = 0
    needRead = True
    while needRead:
        current = current + 1
        print "reading the page " + str(current)
        read = browser.open("http://cartolafc.globo.com/mercado/filtrar.json?page=" + str(current))
        item = loads(read.read())
        if (int(item["page"]["total"]) < current):
            needRead = False
        else:
            players = item["atleta"]
            for player in players:
                cursor.execute("INSERT INTO player VALUES (" + str(player["id"]) + ", '" \
                                                            + player["apelido"].encode('utf-8').replace("'","''") + "', " \
                                                            + str(player["posicao"]["id"]) + ", " \
                                                            + str(player["preco"]) + ", " \
                                                            + str(status[player["status"].encode('utf-8')]) + ");")
            connection.commit()

    def triangular(matches):
        if matches > 0.0:
            return matches + triangular(matches - 1.0)
        else:
            return 1.0

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

    def readEvolution(player):
        try:
            playerId = str(player[0])
            address = "http://cartolafc.globo.com/atleta/" + playerId + "/evolucao/5rodadas.json"
            read = str(browser.open(address).read())
            evolution = loads(read)
            averages = evolution["medias"]
            games = evolution["rodadas"]
            nextScore = makeProbableNextScore(averages)
            matches = len(averages)
            valorization = 0.0 if matches == 0 else averages[-1:][0]
            cursor.execute("INSERT INTO projection VALUES (" + str(playerId) + ", " \
                                                                + str(nextScore) + ", " \
                                                                + str(valorization) + ", " \
                                                                + str(matches) + ");")
            for i in range(matches):
                cursor.execute("INSERT INTO score VALUES (" + str(playerId) + ", " \
                                                            + str(averages[i]) + ", " \
                                                            + str(games[i]) + ");")
            connection.commit()
            return True
        except Exception as exception:
            return False

    needRead = True
    while needRead:
        players = set(cursor.execute("SELECT player.id FROM player WHERE player.id NOT IN (SELECT score.id FROM score GROUP BY score.id) AND player.status = 5;"))
        print "need to read " + str(len(players)) + " players"
        needRead = False
        for player in players:
            if (not readEvolution(player)):
                needRead = True
        connection.commit()

if not options.maxMoney:
    parser.error('You need send the maxMoney')

playersNeeded = 12
positions = { 1: "GOL", 2: "LAT", 3: "ZAG", 4: "MEI", 5: "ATA", 6: "TEC" }
formations =  { 343 : [1, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 6], \
                352 : [1, 3, 3, 3, 4, 4, 4, 4, 4, 5, 5, 6], \
                433 : [1, 2, 2, 3, 3, 4, 4, 4, 5, 5, 5, 6], \
                442 : [1, 2, 2, 3, 3, 4, 4, 4, 4, 5, 5, 6], \
                451 : [1, 2, 2, 3, 3, 4, 4, 4, 4, 4, 5, 6], \
                532 : [1, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 6], \
                541 : [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 6], }
allowedFormations = []
if (options.formation is None):
    allowedFormations.extend(formations.values())
else:
    for f in options.formation:
        allowedFormations.append(formations[f])

def allowedPositionsForAlreadySelectedPlayers(players):
    positionsCount = { 1:0, 2:0, 3:0, 4:0, 5:0, 6:0 }
    for player in players:
        positionsCount[player[3]] = positionsCount[player[3]] + 1
    stillAllowedFormations = []
    for allowedFormation in allowedFormations:
        allowed = True
        for key, value in positionsCount.iteritems():
            if (allowedFormation.count(key) < value):
                allowed = False
                break
        if (allowed):
            stillAllowedFormations.append(allowedFormation)
    allowedPositions = []
    for allowedFormation in stillAllowedFormations:
        for key, value in positionsCount.iteritems():
            if (key not in allowedPositions and allowedFormation.count(key) > value):
                allowedPositions.append(key)
    return allowedPositions

def listToNotInSql(list):
    return str(list).replace("[","(").replace("]",")")

connection = connect("cartola.db")
cursor = connection.cursor()

spentMoney = 0.0
players = []
for i in range(playersNeeded):
    avaliableMoney = options.maxMoney - spentMoney
    currentMaxMoneyForPlayer = avaliableMoney / float(playersNeeded - i)
    cursor.execute('''  SELECT player.id, player.price, player.name, player.position
                        FROM player JOIN projection ON player.id = projection.id
                        WHERE player.price <= {0} AND player.id NOT IN {1} and player.position IN {2}
                        ORDER BY projection.score DESC;
                        '''.format(str(currentMaxMoneyForPlayer), \
                                    listToNotInSql([player[0] for player in players]), \
                                    listToNotInSql(allowedPositionsForAlreadySelectedPlayers(players))))
    player = cursor.fetchone()
    spentMoney = spentMoney + float(player[1])
    players.append(player)
players.sort(key = lambda player: player[3])

for player in players:
    print positions[int(player[3])] + ": " + player[2].encode('utf8').strip()
print "Spent Money: " + str(spentMoney)

connection.commit()
connection.close()
