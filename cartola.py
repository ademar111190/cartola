#!/usr/bin/python2.7

from sys import argv
from json import loads
from os.path import isfile
from sqlite3 import connect
from getpass import getpass
from mechanize import Browser
from optparse import OptionParser
from collections import OrderedDict

def parseRemovePlayers(option, opt, value, parser):
    setattr(parser.values, option.dest, [int(i) for i in value.split(',')])

def parseTeams(option, opt, value, parser):
    setattr(parser.values, option.dest, [i for i in value.split(',')])

parser = OptionParser()
parser.add_option("-u", "--user", dest="user", type="string", help="the cartola username, e.g. -u ademar@mail.com")
parser.add_option("-c", "--maxCartoletas", dest="maxMoney", type="float", help="the max money (cartoletas) allowed to be spent, e.g. -c 100.0")
parser.add_option("-m", "--minValorization", dest="minValorization", type="float", help="the min valorization, e.g. -m -0.4")
parser.add_option("-M", "--maxValorization", dest="maxValorization", type="float", help="the max valorization, e.g. -M 0.5")
parser.add_option("-f", "--forceFormation", dest="forceFormation", type="int", help="force a formation, e.g. -f 442")
parser.add_option("-r", "--removePlayers", action="callback", type="string", help="remove these players, e.g. -r 12345,67890", callback=parseRemovePlayers)
parser.add_option("-t", "--removeTeams", action="callback", type="string", help="remove these teams, e.g. -t \"Barcelona,Real Madrid\"", callback=parseTeams)
parser.add_option("-T", "--forceTeams", action="callback", type="string", help="force these teams, e.g. -T \"Barcelona,Real Madrid\"", callback=parseTeams)
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
    cursor.execute("CREATE TABLE IF NOT EXISTS player(id int, name text, position int, price real, status int, club text)")
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
                                                            + str(status[player["status"].encode('utf-8').strip()]) + ", '" \
                                                            + str(player["clube"]["nome"].encode('utf-8').strip()) + "');")
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
            valorization = 0.0 if matches == 0 else nextScore - averages[-1:][0]
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

if options.minValorization is not None and options.maxValorization is not None and options.minValorization > options.maxValorization:
    parser.error('minValorization cannot be bigger than maxValorization')

playersNeeded = 12
positions = { 1: "GOL", 2: "LAT", 3: "ZAG", 4: "MEI", 5: "ATA", 6: "TEC" }
formations =  { 343 : [1, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 6], \
                352 : [1, 3, 3, 3, 4, 4, 4, 4, 4, 5, 5, 6], \
                433 : [1, 2, 2, 3, 3, 4, 4, 4, 5, 5, 5, 6], \
                442 : [1, 2, 2, 3, 3, 4, 4, 4, 4, 5, 5, 6], \
                451 : [1, 2, 2, 3, 3, 4, 4, 4, 4, 4, 5, 6], \
                532 : [1, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 6], \
                541 : [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 6], }

playersComparation = {}
moneysComparation = {}
pointsComparation = {}

if (options.forceFormation):
    key = options.forceFormation
    formations = { key : formations[key] }

for k,v in formations.iteritems():
    allowedFormations = [v]

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

    connection = connect("cartola.db")
    cursor = connection.cursor()

    spentMoney = 0.0
    expectedPoints = 0.0
    players = []
    for i in range(playersNeeded):
        maxMoneyRule = ""
        if options.maxMoney is not None:
            avaliableMoney = options.maxMoney - spentMoney if options.maxMoney is not None else 9999.9
            currentMaxMoneyForPlayer = avaliableMoney / float(playersNeeded - i)
            maxMoneyRule = " AND player.price <= " + str(currentMaxMoneyForPlayer)
        forbiddenPlayers = [player[0] for player in players]
        if (options.removePlayers is not None):
            forbiddenPlayers.extend(options.removePlayers)
        removeTeamsRule = "" if options.removeTeams == None else " AND LOWER(player.club) NOT IN ('{0}')".format("','".join([t.lower() for t in options.removeTeams]))
        forceTeamsRule = "" if options.forceTeams == None else " AND LOWER(player.club) IN ('{0}')".format("','".join([t.lower() for t in options.forceTeams]))
        query = ''' SELECT player.id, player.price, player.name, player.position, player.club, projection.score, projection.valorization
                            FROM player JOIN projection ON player.id = projection.id
                            WHERE player.id NOT IN ({0}) AND player.position IN ({1}) {2} {3} {4} {5} {6}
                            ORDER BY projection.score DESC;
                            '''.format(",".join([str(p) for p in forbiddenPlayers]), \
                                        ",".join([str(p) for p in allowedPositionsForAlreadySelectedPlayers(players)]), \
                                        removeTeamsRule, \
                                        forceTeamsRule, \
                                        maxMoneyRule, \
                                        "" if options.minValorization == None else " AND projection.valorization > " + str(options.minValorization), \
                                        "" if options.maxValorization == None else " AND projection.valorization < " + str(options.maxValorization))
        cursor.execute(query)
        player = cursor.fetchone()
        spentMoney = spentMoney + float(player[1])
        expectedPoints = expectedPoints + player[5]
        players.append(player)
    players.sort(key = lambda player: player[3])
    playersComparation[k] = players
    moneysComparation[k] = spentMoney
    pointsComparation[k] = expectedPoints

orderedPoints = OrderedDict(sorted(pointsComparation.items(), key=lambda x: x[1]))

def printLine():
    print "+-----+--------+--------+"

printLine()
print u'| {:<4}|{:>7} |{:>7} |'.format("", "Points", "$")
printLine()
bestFormation = None
for k,v in orderedPoints.iteritems():
    bestFormation = k
    players = playersComparation[k]
    spentMoney = moneysComparation[k]
    expectedPoints = pointsComparation[k]
    print u'| {:<4}|{:>7} |{:>7} |'.format(k, format(expectedPoints, ".2f"), format(spentMoney, ".2f"))
printLine()

def printLine():
    print "+-----+-------+---------------------+---------------+--------+--------+"

printLine()
print u'| {:<4}| {:<6}| {:<20}| {:<14}|{:>7} |{:>7} |'.format(bestFormation, "ID", "Name", "Club", "Points", u"\u2191\u2193")
printLine()
for player in players:
    print u'| {:<4}| {:<6}| {:<20}| {:<14}|{:>7} |{:>7} |'.format(positions[int(player[3])], player[0], player[2].title(), player[4].title(), format(player[5], ".2f"), format(player[6], ".2f"))
printLine()

connection.commit()
connection.close()
