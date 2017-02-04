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
    def TestGame(self):
        self.Send('INFO|GAME|{}')
    def TestGetCard(self):
        self.Send('INFO|GETCARD|[1,2,3,4,5,6,7,8,9,10]')
    def TestGetScore(self):
        self.Send('INFO|GETSCORE|p1|[1,2]')
    def TestPickCard(self):
        s = set()
        self.Send('INFO|GETCARD|[1,2,3,4,5,6,7,8,9,10]')
        for i in range(10):
            self.Send('CMD|PICKCARD')
            s.add(int(self.Receive()))
        if s != set(range(1,11)):
            print "Failure! Pick Card from 1-10 results in", s
    def TestPickRow(self):
        self.Send('CMD|PICKROW')
        r = int(self.Receive())
        if not 0 <= r <= 3:
            print "Failure! Pick row gives back", r

    def RunTests(self):
        self.TestGame()
        self.TestGetCard()
        self.TestPickCard()
        self.TestGetScore()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='*')
    options = parser.parse_args()
    for f in options.files:
        t = Tests(f)
        t.RunTests()

