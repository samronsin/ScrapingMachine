# -*- coding: utf-8 -*-

f = open('clean_10000.txt')

l = f.readlines()
l = list(set(l))
for line in l:
	print line.replace('\n','')