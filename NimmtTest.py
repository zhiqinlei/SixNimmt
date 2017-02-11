#!usr/bin/env python
import argparse
import os
from subprocess import Popen, PIPE

class Tests:
    def __init__(self, path):
        self.path = path
        if os.path.exists(path):
            self.proc = Popen(path, stdin = PIPE, stdout = PIPE, bufsize=0)
        else:
            print "Can't find path for", path
    def Send(self, s):
        self.proc.stdin.write(s+'\n')
    def Receive(self):
        line = self.proc.stdout.readline()
        return line
    def TestCase(testFunc):
        def wrapper(*args):
            try:
                testFunc(*args)
                print "{:15} {}".format(testFunc.__name__, "passed!")
            except Exception as e:
                print "{:15} {}".format(testFunc.__name__, "failed!")
                print e
        return wrapper
    @TestCase
    def TestSetup(self):
        self.Send('INFO|SETUP|{"name":"p1", "playerNum":2}')
    @TestCase
    def TestNewGame(self):
        self.Send('INFO|NEWGAME|[1,2,3,4,5,6,7,8,9,10]')
    @TestCase
    def TestGame(self):
        self.Send('INFO|GAME|{"rows":[[1],[2],[3],[4]],"players":{"p1":0, "p2":1}}')
    @TestCase
    def TestMove(self):
        self.Send('INFO|NEWGAME|[11,22,33,44,55,66,77,88,99,101]')
        self.Send('INFO|MOVE|{"p1":1, "p2":2}')
    @TestCase
    def TestScore(self):
        self.Send('INFO|SCORE|{"player":"p1", "cards":[1,2], "score":2}')
    @TestCase
    def TestGameEnd(self):
        self.Send('INFO|GAMEEND|{"p1":105, "p2":78}')
    @TestCase
    def TestPickCard(self):
        s = set()
        self.Send('INFO|NEWGAME|[11,12,13,14,15,16,17,18,19,20]')
        self.Send('INFO|GAME|{"rows":[[1],[2],[3],[4]],"players":{"p1":0, "p2":1}}')
        for i in range(10):
            self.Send('CMD|PICKCARD')
            s.add(int(self.Receive()))
        if s != set(range(11,21)):
            raise Exception("Failure! Pick Card from 1-10 results in", s)
    @TestCase
    def TestPickRow(self):
        self.Send('CMD|PICKROW')
        r = int(self.Receive())
        if not 0 <= r <= 3:
            raise Exception("Failure! Pick row gives back", r)

    def RunTests(self):
        self.TestSetup()
        self.TestNewGame()
        self.TestGame()
        self.TestMove()
        self.TestScore()
        self.TestPickCard()
        self.TestPickRow()
        self.TestGameEnd()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+')
    options = parser.parse_args()

    for f in options.files:
        t = Tests(f)
        t.RunTests()

