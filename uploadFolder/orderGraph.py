# orderGraph.py
# Carter Slocum
# July 2015

# This file contains a function for topologically ordering a tree graph and detecting cyclic graphs


import copy


def date(recon):
	"""takes a Tree and returns a dictionary representation of the ordering of the tree. 
	If there is a cycle, the function returns None"""
	order = {}
	dicto = {}
	Leaves = {}
	LonerList = []
	for key in recon.keys():
		if  key != None:
			dicto[key] = 0
		for child in recon[key]:
			if child != None:
				dicto[child] = 0
			else:
				Leaves[key] = True
	for key in Leaves.keys():
		if key in dicto.keys():
			del dicto[key]
	for key in dicto.keys():
		for child in recon[key]:
			if child != None and child in dicto:
				dicto[child] += 1
	place = 0
	for key in dicto.keys():
		if dicto[key] == 0:
			del dicto[key]
			LonerList.append(key)
	while LonerList:
		x = LonerList[0]
		del LonerList[0]
		order[x] = place
		place += 1
		for child in recon[x]:
			if child in dicto.keys():
				dicto[child] -= 1
				if dicto[child] == 0:
					del dicto[child]
					LonerList.append(child)
	if len(dicto.keys()) > 0:
		return "timeTravel"
	else:
		for item in Leaves:
			order[item] = len(Leaves)
		return order

	