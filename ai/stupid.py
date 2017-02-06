#!/usr/bin/env python
import sys
import random
import logging
class AI:
    def __init__(self):
        self.name = ''
        self.cards = []
        logging.basicConfig(filename = './log', level=logging.INFO)
    def InfoNewGame(self, newGamedata):
        self.cards = newGamedata[:]
        pass
    def InfoGame(self, gameData):
        pass
    def InfoMove(self, cardData):
        pass
    def InfoScore(self, scoreData):
        pass
    def CmdPickCard(self):
        random.shuffle(self.cards)
        return self.cards.pop()
    def CmdPickRow(self):
        return random.randint(0,3)
    def ProcessInfo(self):
        line = sys.stdin.readline()
        if line == '':
            logging.info('No Input')
            sys.exit(1)
        data = line.strip().split('|')
        logging.info("Get Info " + str(line))
        if data[0] == 'INFO':
            if data[1] == 'NEWGAME':
                self.InfoNewGame(eval(data[2]))
            elif data[1] == 'GAME':
                self.InfoGame(eval(data[2]))
            elif data[1] == 'MOVE':
                self.InfoMove(eval(data[2]))
            elif data[1] == 'SCORE':
                self.InfoScore(eval(data[2]))
        elif data[0] == 'CMD':
            if data[1] == 'PICKCARD':
                self.Send(self.CmdPickCard())
            elif data[1] == 'PICKROW':
                self.Send(self.CmdPickRow())
        elif data[0] == 'HELLO':
            self.Send('WORLD')
    def Send(self, data):
        logging.info('Send Info ' + str(data))
        print str(data)
        sys.stdout.flush()
    def Start(self):
        while True:
            self.ProcessInfo()

if __name__ == '__main__':
    ai = AI()
    ai.Start()
