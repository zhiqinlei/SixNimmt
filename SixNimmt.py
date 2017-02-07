#!/usr/bin/env python
import logging
import random
from subprocess import Popen, PIPE
import os
import argparse

class AiHandler:
    def __init__(self):
        self.procs = {}
    def AddAi(self, name, path):
        if os.path.exists(path):
            p = Popen(['python', path], stdin=PIPE, stdout=PIPE, bufsize=0)
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
    def Info(self, subHeader, data, player = None):
        msg = 'INFO|' + subHeader + '|' + str(data)
        self.Send(msg, player)
    def Cmd(self, subHeader, player = None):
        msg = 'CMD|' + subHeader
        self.Send(msg, player)
        return int(self.Receive(player).strip())

class Player:
    def __init__(self, name, aiHandler):
        self.name = name
        self.cards = []
        self.score = 0
        self.aiHandler = aiHandler
    def NewGame(self, cards):
        self.cards = cards[:]
        if self.aiHandler != None:
            self.aiHandler.Info('NEWGAME', self.cards, player = self.name)
        else:
            print 'New cards:', self.cards
        
    def PickCard(self):
        if self.aiHandler != None:
            c = self.aiHandler.Cmd('PICKCARD', self.name)
        else:
            print 'Current Card:', sorted(self.cards)
            c = eval(raw_input('Please choose a card to put\n'))
        self.cards.remove(c)
        return c

    def PickRow(self):
        if self.aiHandler != None:
            c = self.aiHandler.Cmd('PICKROW', self.name) 
        else:
            print 'Choose a row to pick'
            c = eval(raw_input('Please choose a row\n'))
        return c
    def Score(self, score):
        self.score += score
    def PrintData(self):
        print "Name: {}, Cards: {}, Score: {}".format(self.name, self.cards, self.score)

class SixNimmtGame:
    def __init__(self, **kwargs):
        self.playerNum = 0
        self.rows = [[],[],[],[]]
        self.players = {}
        self.aiHandler = AiHandler()
        self.broadCast = True
        for key, val in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, val)
            else:
                raise Exception("Wrong keyword "+key)

    def AddPlayer(self, playerName, path):
        '''
        Add a player in the game
          * playerName: the name of the player
          * path: the path to the AI, if it's None then it's a human player
        '''
        if playerName in self.players:
            raise NameError('Same player name')
        else:
            if path != None:
                self.players[playerName] = Player(playerName, self.aiHandler)
                self.aiHandler.AddAi(playerName, path)
            else:
                self.players[playerName] = Player(playerName, None)
        self.playerNum += 1

    def Setup(self):
        for name in self.players:
            data = {}
            data["name"] = name
            data["playerNum"] = self.playerNum
            self.aiHandler.Info('SETUP', data, name)

    def StartTour(self, score):
        while True:
            self.NewGame()
            if any([p.score > score for p in self.players.values()]):
                self.BroadCast('Game ends!')
                self.BroadCast([(name, self.players[name].score) for name in self.players])
                break

    def NewGame(self):
        '''
        Create a new game, do not clear score.
        Deal 10 cards for each player
        '''
        self.deck = list(range(1, 105))
        random.shuffle(self.deck)
        for i in range(4):
            self.rows[i] = [self.deck.pop()]
        self.rows.sort(key = lambda x:x[-1], reverse = True)
        for p in self.players.values():
            p.NewGame([self.deck.pop() for i in range(10)])
        for r in range(10):
            self.NewRound()

    def NewRound(self):
        '''
        A new round of a game.
        Send the game status to all players.
        Request a card from each player
        Process the result
        '''
        self.newCards = []
        self.SendGameInfo()
        for name, p in self.players.items():
            self.newCards.append((name, p.PickCard()))
        self.SendMoveInfo(self.newCards)
        self.ProcessGame()
        
    def ProcessGame(self):
        self.newCards.sort(key = lambda x:x[-1])
        for name, c in self.newCards:
            if c < min([self.rows[i][-1] for i in range(4)]):
                rowNum = self.players[name].PickRow()
                self.BroadCast("{} picked row {}:{}".format(name, rowNum, self.rows[rowNum]))
                self.SendScoreInfo(name, self.rows[rowNum])
                self.players[name].Score(self.CountScore(self.rows[rowNum]))
                self.rows[rowNum] = [c]
                # sort rows based on the last value
                self.rows.sort(key = lambda x:x[-1], reverse=True)
            else:
                for r in self.rows:
                    if c > r[-1]:
                        if len(r) == 5:
                            self.SendScoreInfo(name, r)
                            self.players[name].Score(self.CountScore(r))
                            r[:] = [c]
                        else:
                            r.append(c)
                        break
                else:
                    raise Exception("Value should be in range!")

    def SendGameInfo(self):
        game = {}
        game['rows'] = self.rows
        game['players'] = {}
        for p in self.players:
            game['players'][p] = self.players[p].score
        self.aiHandler.Info('GAME', game)
        self.BroadCast('Current Game:')
        self.BroadCast(game['players'])
        for r in self.rows:
            self.BroadCast(r)

    def SendScoreInfo(self, player, cards):
        data = {}
        data['player'] = player
        data['cards'] = cards[:]
        data['score'] = self.CountScore(cards)
        self.aiHandler.Info('SCORE', data)
        self.BroadCast('Score!')
        self.BroadCast(data)

    def SendMoveInfo(self, cardInfo):
        move = {}
        for name, card in cardInfo:
            move[name] = card
        self.aiHandler.Info('MOVE', move)
        self.BroadCast('Move!')
        self.BroadCast(move)

    def CountScore(self, cards):
        score = 0
        for c in cards:
            if c == 55:
                score += 7
            elif c % 11 == 0:
                score += 5
            elif c % 10 == 0:
                score += 3
            elif c % 5 == 0:
                score += 2
            else:
                score += 1
        return score

    def BroadCast(self, s):
        if self.broadCast:
            print s
    def PrintData(self):
        print "Current Row:"
        for r in self.rows:
            print r
        print 'New Cards: {}'.format(self.newCards)
        for p in self.players.values():
            p.PrintData()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', type=int, default=100)
    options = parser.parse_args()
    game = SixNimmtGame(broadCast = True)
    game.AddPlayer('p1', './ai/example/exampleai.py')
    game.AddPlayer('p2', './ai/example/exampleai.py')
    game.Setup()
    #game.NewGame()
    game.StartTour(options.r)
