#!/usr/bin/env python

import sys

filename = sys.argv[1]

infile = open(filename)
out1 = open("bt1.txt", "w")
out2 = open("bt2.txt", "w")
out3 = open("bt3.txt", "w")
out4 = open("bt4.txt", "w")
out5 = open("bt5.txt", "w")
template = """               "%s" : {
                  "value": "%s",
                  "answer": "%s"
               },
"""

for line in infile:
    print line
    (name, bt1, bt2, bt3, bt4, bt5, answer) = line.split(",")
    #print "What is the answer for this flag?"
    #answer = raw_input("> ")
    out1.write(template % (name, bt1, answer))
    out2.write(template % (name, bt2, answer))
    out3.write(template % (name, bt3, answer))
    out4.write(template % (name, bt4, answer))
    out5.write(template % (name, bt5, answer))
