#! /usr/bin/env python
# -*- coding: utf8 -*-


import time, multiprocessing, os, re

##parallel start of a gpu search programms - 
def sort_nicely( l ):
    """ Sort the given list in the way that humans expect.
    """
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    l.sort( key=alphanum_key )

def runrara( atexindex, lwindex, texpath ):
    print( "python3 3gpusearch.py "+atexindex+" "+lwindex+" "+texpath )
    os.system("python3 3gpusearch.py "+atexindex+" "+lwindex+" "+texpath)
    #os.system("ls -la")
    

if __name__ == "__main__":
    #0. check python+openGL
    #1. conf+run CTStoTXT.py
    #2. conf+run TXTencode.py
    #3. conf 3gpusearch.py
    #4. run parastratGPUsearch.py
    #5. conf+run check.py
    inpath = "OUTenc/brokentextures" #such basis
    fifafiles = os.listdir( inpath )
    sort_nicely( fifafiles )
    texindex = 0
    currworkers = []
    for name in fifafiles:
        twoparts = name.split("-")
        texindex = twoparts[0]
        lastwordindex = twoparts[1].split(".")[0]
        p = "%s/%s" % ( inpath, name )
        print("start for texture", texindex, p, lastwordindex)
        
        w = multiprocessing.Process(target=runrara, args=(texindex,lastwordindex, p) )
        currworkers.append( w )
        w.start( )
    for ws in currworkers:
        ws.join( )
