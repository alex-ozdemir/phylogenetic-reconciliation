# MasterReconciliation.py
# Juliet Forman, Srinidhi Srinivasan, Annalise Schweickart, and Carter Slocum
# July 2015

# This file contains functions for computing maximum parsimony 
# DTL reconciliations using the edge-based DP algorithm.  The main # # function in this file is called Reconcile and the remaining 
# functions are helper functions that are used by Reconcile.

import DP
import Greedy
import newickToVis
import reconConversion
import orderGraph
import newickFormatReader
import reconciliationGraph
from sys import argv
import copy
import calcCostscapeScore
import detectCycles
import os

def Reconcile(argList):
	"""Takes command-line arguments of a .newick file, duplication, transfer, 
	and loss costs, the type of scoring desired and possible switch and loss 
	ranges. Creates Files for the host, parasite, and reconciliations"""
	fileName = argList[1] #.newick file
	D = float(argList[2]) # Duplication cost
	T = float(argList[3]) # Transfer cost
	L = float(argList[4]) # Loss cost
	freqType = argList[5] # Frequency type
	# Optional inputs if freqType == xscape
	switchLo = float(argList[6]) # Switch lower boundary
	switchHi = float(argList[7]) # Switch upper boundary
	lossLo = float(argList[8]) # Loss lower boundary
	lossHi = float(argList[9]) # Loss upper boundary

	host, paras, phi = newickFormatReader.getInput(fileName)
	hostRoot = findRoot(host)
	hostv = treeFormat(host)
	DTLReconGraph, numRecon = DP.DP(host, paras, phi, D, T, L)
	#uses xScape scoring function
	if freqType == "xscape":
		DTLReconGraph = calcCostscapeScore.newScoreWrapper(fileName, switchLo, \
			switchHi, lossLo, lossHi, D, T, L)
	#uses Unit scoring function
	elif freqType == "unit":
		DTLReconGraph = unitScoreDTL(host, paras, phi, D, T, L)

	DTLGraph = copy.deepcopy(DTLReconGraph)
	scoresList, rec = Greedy.Greedy(DTLGraph, paras)
	for n in range(len(rec)):
		currentRecon = rec[n]
		graph = reconciliationGraph.buildReconstruction(host, paras, currentRecon)
		currentOrder = orderGraph.date(graph)
		if currentOrder == "timeTravel":
			newOrder = detectCycles.detectCyclesWrapper(host, paras, currentRecon)
			currentRecon = newOrder
			currentOrder = reconciliationGraph.buildReconstruction\
			(host, paras, newOrder)
			currentOrder = orderGraph.date(currentOrder)
		hostOrder = hOrder(hostv,currentOrder)
		hostBranchs = branch(hostv,hostOrder)

		if n == 0:
			newickToVis.convert(fileName,hostBranchs, n, 1)
		else:
			newickToVis.convert(fileName,hostBranchs, n, 0)
		reconConversion.convert(rec[n], DTLGraph, paras, fileName[:-7], n)

def unitScoreDTL(hostTree, parasiteTree, phi, D, T, L):
	""" Takes a hostTree, parasiteTree, tip mapping function phi, and 
	duplication cost (D), transfer cost (T), and loss cost (L) and returns the
	DTL graph in the form of a dictionary, with event scores set to 1. 
	Cospeciation is assumed to cost 0. """
	DTLReconGraph, numRecon = DP.DP(hostTree, parasiteTree, phi, D, T, L)
	newDTL = {}
	for vertex in DTLReconGraph:
		newDTL[vertex] = []
		for event in DTLReconGraph[vertex][:-1]:
			newEvent = event[:-1] + [1.0]
			newDTL[vertex].append(newEvent)
		newDTL[vertex].append(DTLReconGraph[vertex][-1])
	return newDTL

def branch(tree, treeOrder):
	"""Computes Ultra-metric Branchlength from a tree dating"""
	branches = {}
	for key in tree:
		if key != None:
			for child in tree[key]:
				if child != None:
					branches[child] = abs(treeOrder[child] - treeOrder[key])
	for key in treeOrder:
		if not key in branches:
			branches[key] = 0
	return branches


def hOrder(hTree, orderMess):
	"""takes in the host tree and the ordering of the reconciliation and returns
	a dictionary reresentation of the host tree ordering for that reconciliation"""
	hostOrder = {} 
	leaves = []
	messList = sorted(orderMess, key=orderMess.get)
	place = 0
	for item in range(len(messList)):
		if messList[item] in hTree and not hTree[messList[item]] == [None, None]:
			hostOrder[messList[item]] = place

			place+=1
		elif messList[item] in hTree and hTree[messList[item]] == [None,None]:

			leaves.append(messList[item])
	for item in leaves:
		hostOrder[item] = place
	return hostOrder 





def findRoot(Tree):
    """This function takes in a parasiteTree and returns a string with the 
    name of the root vertex of the tree"""

    if 'pTop' in Tree:
    	return Tree['pTop'][1]
    return Tree['hTop'][1]

def InitDicts(tree):
	"""This function takes as input a tree dictionary and returns a dictionary
	with all of the bottom nodes of the edges as keys and empty lists as 
	values."""
	treeDict = {}
	for key in tree:
		if key == 'pTop':
			treeDict[tree[key][1]] = [] 
		elif key == 'hTop':
			treeDict[tree[key][1]] = []
		else:
			treeDict[key[1]] = []
	return treeDict

def treeFormat(tree):
	"""Takes a tree in the format that it comes out of newickFormatReader and
	converts it into a dictionary with keys which are the bottom nodes of the
	edge and values which are the children."""
	treeDict = InitDicts(tree)
	treeRoot = findRoot(tree)
	for key in tree:
		if key == 'hTop' or key == 'pTop':
			if tree[key][-2] == None:
				treeDict[treeRoot] = treeDict[treeRoot] + [tree[key][-2]]
			else:
				treeDict[treeRoot] = treeDict[treeRoot] + [tree[key][-2][1]]
			if tree[key][-1] == None:
				treeDict[treeRoot] = treeDict[treeRoot] + [tree[key][-1]]
			else:
				treeDict[treeRoot] = treeDict[treeRoot] + [tree[key][-1][1]]
		else:
			if tree[key][-2] == None:
				treeDict[key[1]] = treeDict[key[1]] + [tree[key][-2]]
			else:
				treeDict[key[1]] = treeDict[key[1]] + [tree[key][-2][1]]
			if tree[key][-1] == None:
				treeDict[key[1]] = treeDict[key[1]] + [tree[key][-1]]
			else:
				treeDict[key[1]] = treeDict[key[1]] + [tree[key][-1][1]]
	return treeDict


def main():
	Reconcile(argv)

if __name__ == "__main__": main()