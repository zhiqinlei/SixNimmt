#!/usr/bin/env python
import logging
import random
from subprocess import Popen, PIPE
import os

class AiHandler:
    def __init__(self):
        self.procs = {}
    def AddAi(self, name, path):
        if os.path.exists(path):
            p = Popen(path, stdin=PIPE, stdout=PIPE, bufsize=0)
            self.procs[name] = p
        else:
            raise Exception("there's no path" + path)
        print "Added AI", name, path
    def Send(self, s, player = None):
        if player == None:
            for p in self.procs.values():
                p.stdin.write(s+'\n')
        else:
            self.procs[player].stdin.write(s+'\n')
    def Receive(self, player):
        line = self.procs[player].stdout.readline()
        return line
    def InfoPlayers(self, players):
        self.Send('INFO|PLAYERS|'+str(players))
    def InfoGame(self, game):
        self.Send('INFO|GAME|'+str(game))
    def InfoGetCard(self, card, player):
        self.Send('INFO|GETCARD|'+str(card), player = player)
    def InfoGetScore(self, score, player):
        self.Send('INFO|GETSCORE|'+str(player)+'|'+str(score))
    def InfoMove(self, move):
        self.Send('INFO|MOVE|'+str(move))
    def CmdPickCard(self, player):
        self.Send('CMD|PICKCARD', player = player)
        c = self.Receive(player)
        return int(c.strip())
    def CmdPickRow(self, player):
        self.Send('CMD|PICKROW', player = player)
        r = self.Receive(player)
        return int(r.strip())

class Player:
    def __init__(self, name, aiHandler):
        self.name = name
        self.cards = []
        self.score = 0
        self.aiHandler = aiHandler
    def GetNewCards(self, cards):
        self.cards = cards[:]
        if self.aiHandler != None:
            self.aiHandler.InfoGetCard(self.cards, player = self.name)
        else:
            print 'New cards:', self.cards
        
    def PutCard(self):
        if self.aiHandler != None:
            c = self.aiHandler.CmdPickCard(self.name)
        else:
            print 'Current Card:', self.cards
            c = eval(input('Please choose a card to put'))
        self.cards.remove(c)
        return c
    def PickRow(self):
        if self.aiHandler != None:
            c = self.aiHandler.CmdPickRow(self.name) 
        else:
            print 'Choose a row to pick'
            c = eval(input('Please choose a row'))
        return c
    def GetScore(self, row):
        self.aiHandler.InfoGetScore(row, player = self.name)
        self.score += len(row)
    def PrintData(self):
        print "Name: {}, Cards: {}, Score: {}".format(self.name, self.cards, self.score)

class SixNimmtGame:
    def __init__(self, **kwarg):
        self.playerNum = 0
        self.rows = [[],[],[],[]]
        self.players = {}
        self.aiHandler = AiHandler()

    def AddPlayer(self, playerName, path):
        if playerName in self.players:
            raise NameError('Same player name')
        else:
            if path != None:
                self.players[playerName] = Player(playerName, self.aiHandler)
                self.aiHandler.AddAi(playerName, path)
            else:
                self.players[playerName] = Player(playerName, None)
        self.playerNum += 1

    def NewGame(self):
        self.deck = list(range(1, 105))
        random.shuffle(self.deck)
        for i in range(4):
            self.rows[i] = [self.deck.pop()]
        self.rows.sort(key = lambda x:x[-1], reverse = True)
        for p in self.players.values():
            p.GetNewCards([self.deck.pop() for i in range(10)])
        for r in range(10):
            self.NewRound()

    def NewRound(self):
        self.newCards = []
        #self.PrintData()
        self.SendGameInfo()
        self.SendPlayerInfo()
        for name, p in self.players.items():
            self.newCards.append((p.PutCard(), name))
        self.SendMoveInfo(self.newCards)
        self.PrintData()
        self.ProcessGame()
        
    def ProcessGame(self):
        self.newCards.sort()
        for c, name in self.newCards:
            if c < min([self.rows[i][-1] for i in range(4)]):
                rowNum = self.players[name].PickRow()
                self.players[name].GetScore(self.rows[rowNum])
                self.rows[rowNum] = [c]
                # sort rows based on the last value
                self.rows.sort(key = lambda x:x[-1], reverse=True)
            else:
                for r in self.rows:
                    if c > r[-1]:
                        if len(r) == 5:
                            self.players[name].GetScore(r)
                            r = [c]
                        else:
                            r.append(c)
                        break
                else:
                    raise Exception("Value should be in range!")

    def SendGameInfo(self):
        game = {}
        game['playerNum'] = self.playerNum
        game['rows'] = self.rows
        self.aiHandler.InfoGame(game)

    def SendPlayerInfo(self):
        pInfo = {}
        for p in self.players:
            pInfo[p] = {}
            pInfo[p]['score'] = self.players[p].score
        self.aiHandler.InfoPlayers(pInfo)

    def SendMoveInfo(self, move):
        self.aiHandler.InfoMove(move)

    def PrintData(self):
        print "Current Row:"
        for r in self.rows:
            print r
        print 'New Cards: {}'.format(self.newCards)
        for p in self.players.values():
            p.PrintData()

if __name__ == '__main__':
    game = SixNimmtGame()
    game.AddPlayer('p1', './ai/stupid.py')
    game.AddPlayer('p2', './ai/stupid.py')
    game.AddPlayer('Player', None)
    game.NewGame()
    #handler = AiHandler()
    #handler.AddAi('stupid', './ai/stupid.py')
