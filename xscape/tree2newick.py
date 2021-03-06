#!/usr/bin/env python

# tree2newick.py
# Ran Libeskind-Hadas, October 2013
# Convert .tree file to .newick file

import sys
from sys import argv
from collections import Counter

def input(arglist):
    treeFile = arglist[1]
    outputName = arglist[2]
    infileHandle = open(treeFile, 'r')
    outfileHandle = open(outputName, 'w')
        
    lines = list(infileHandle)
    infileHandle.close()

    # Strip whitespace and check that the HOSTREE, PARASITETREE,
    # and PHI entries appear in the input
    
    cleanLines = [line.strip().split("\t") for line in lines]
    if not ['HOSTTREE'] in cleanLines \
       or not ['PARASITETREE'] in cleanLines \
       or not ['PHI'] in cleanLines:
        print "This does not appear to be a valid .tree file."
        sys.exit(0)

    # Advance to HOSTNAMES section and read into hnames dictionary.
    hnames = {}
    pointer = cleanLines.index(['HOSTNAMES']) + 1
    while len(cleanLines[pointer]) >= 2:  # read host names
        nextLine = cleanLines[pointer]
        assert len(nextLine) == 2, nextLine
        node, name = str(nextLine[0]), '_'.join(''.join(str(nextLine[1]).split("'")).split(' '))
        if name.isdigit():
            name = "h" + name
        hnames[node] = name
        pointer += 1

    # Advance to HOSTTREE section and read into h dictionary.
    h = {}
    pointer = cleanLines.index(['HOSTTREE']) + 1
    while len(cleanLines[pointer]) >= 2:  # read host tree
        nextLine = cleanLines[pointer]
        if len(nextLine) == 2:
            root, left, right = str(nextLine[0]), "null", "null"
        else:
            root, left, right = str(nextLine[0]), str(nextLine[1]), str(nextLine[2])

        root = hnames[root]
        if left != "null": left = hnames[left]
        if right != "null" : right = hnames[right]
        
        h[root] = (left, right)
        pointer += 1
    hroot = findRoot(h)
    hostTree = buildNewickTree(h, hroot)       
    outfileHandle.write(hostTree + ";\n")

    # Advance to PARASITENAMES section and read into pnames dictionary.
    pnames = {}
    pointer = cleanLines.index(['PARASITENAMES']) + 1
    while len(cleanLines[pointer]) >= 2:  # read host names
        nextLine = cleanLines[pointer]
        assert len(nextLine) == 2, nextLine
        node, name = str(nextLine[0]), '_'.join(''.join(str(nextLine[1]).split("'")).split(' '))
        if name.isdigit():
            name = "p" + name
        pnames[node] = name
        pointer += 1

    # Advance to PARASITETREE section and read into p dictionary.
    p = {} 
    pointer = cleanLines.index(['PARASITETREE']) + 1
    while len(cleanLines[pointer]) >= 2: # read parasite tree
        nextLine = cleanLines[pointer]
        if len(nextLine) == 2:
            root, left, right = str(nextLine[0]), "null", "null"
        else:   
            root, left, right = str(nextLine[0]), str(nextLine[1]), str(nextLine[2])
        
        root = pnames[root]
        if left != "null": left = pnames[left]
        if right != "null" : right = pnames[right]
        
        p[root] = (left, right)
        pointer += 1
    proot = findRoot(p)
    parasiteTree = buildNewickTree(p, proot)
    outfileHandle.write(parasiteTree + ";\n")
    
    # Advance to PHI section
    pointer = cleanLines.index(['PHI']) + 1
    while len(cleanLines[pointer]) == 2: # read Phi
        nextLine = cleanLines[pointer]
        hnode, pnode = str(nextLine[0]), str(nextLine[1])
        htip = hnames.get(hnode, "h" + hnode)
        ptip = pnames.get(pnode, "p" + pnode)
        outfileHandle.write(ptip + ":" + htip + "\n")
        pointer += 1
    outfileHandle.close()
    print "File written to " + treeFile[:-5] + ".newick"

def findRoot(treeDict):
    parent = Counter()
    for vertex in treeDict:
        left, right = treeDict[vertex]
        parent[left] += 1
        parent[right] += 1
    for vertex in treeDict:
        if parent[vertex] == 0: return vertex  # No parent?  You're the root!
            
def buildNewickTree(treeDict, root):
    left, right = treeDict[root]
    if left == "null": return root
    else:
        leftNewick = buildNewickTree(treeDict, left)
        rightNewick = buildNewickTree(treeDict, right)
        return "(" + leftNewick + ", " + rightNewick + ")" + " " + str(root)
def main():
    input(argv)
        
if __name__ == '__main__': main()
