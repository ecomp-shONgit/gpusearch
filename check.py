#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, codecs, unicodedata, time, hashlib, cPickle, re

'''
Prof. Charlotte Schubert, Alte Geschichte Leipzig 2017 

Script combines all output data of gpusearch to html visualization.

    # GPLv3 copyrigth
    # This program is free software: you can redistribute it and/or modify
    # it under the terms of the GNU General Public License as published by
    # the Free Software Foundation, either version 3 of the License, or
    # (at your option) any later version.
    # This program is distributed in the hope that it will be useful,
    # but WITHOUT ANY WARRANTY; without even the implied warranty of
    # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    # GNU General Public License for more details.
    # You should have received a copy of the GNU General Public License
    # along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''

###GOBALS
w = 1600
h = 1000
texsize = w*h
outdir = "/xx/xx/Siccon" #path out output directory
pa = "TXT15JH/15JH.txt" #path of search text as txt
pb = "TXTBTL/BTL.txt" #path of base text as txt
ia = "TXT15JH/15JH.index" #path of index of search text
ib = "TXTBTL/BTL.index" #path of index of base text
af = "alleFragen/allefragen.txt" #path of splitted search text


def sort_nicely( l ):
    """ Sort the given list in the way that humans expect.
    """
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    l.sort( key=alphanum_key )

if __name__ == "__main__":
    startdate = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
    print( "Loosss!!!!", startdate )
    
    

    augustfilehandel = open( pa, "r" ) 
    augustintext = augustfilehandel.read().split(" ")
    btlfilehandel = open( pb, "r" )
    btltext = btlfilehandel.read().split(" ")
    print("Sicco / BTL gelesen Text gelesen")
    
    
    wi1TOcts = cPickle.load( open( ia, "rb" ) )
    tiwi2TOcts = cPickle.load( open( ib, "rb" ) )
    print("wi 2 cts index file gelesen")

    fkTOwi1 = cPickle.load( open( af, "rb" ) )
    #umcodieren aller, falls noch nicht geschehen
    print("alle fragen gelesen")
    wi1TOfk = None
    try:
        wi1TOfk = cPickle.load( open( "alleFragen/wi1fk.txt", "rb" ) )
        print("fk wi1 wi1 fk geschrieben/gelesen")
    except: 
        wi1TOfk = {}
        for af in fkTOwi1:
            for wipf in fkTOwi1[ af ]:
                wi1TOfk[wipf] = af
        cPickle.dump( wi1TOfk, open( "alleFragen/wi1fk.txt", "wb" ) )
    
        print("fk wi1 wi1 fk geschrieben")
    #print(wi1TOfk[293996])#293996: '195819 195819 386587 451923 47952'
    
    gefunden = None
    try:
        gefunden = cPickle.load( open( "gefunden/GEFUNDEN.txt", "rb" ) )
        print("fk gefunden gelesen")
    except:
        gefunden = {}
        textures = os.listdir( "gefunden" )
        sort_nicely( textures )
        for t in textures:
            gefprotexturefiles = os.listdir( "gefunden/"+str(t) )
            sort_nicely( gefprotexturefiles )
            subtractoverlap = 200
            if(t == "0"):
                print("overlap 0", t)
                subtractoverlap = 0
            for geffile in gefprotexturefiles:
                #readfile
                gfh = open("gefunden/"+str(t)+"/"+geffile, "rb" )
                asfuckingstring = gfh.read()
                gfh.close()
                gefeintraege = asfuckingstring.split(";")
                for g in gefeintraege:
                    gasarray = g.split(",")
                    fktemp = gasarray[4].split(" ")
                    fkasarray = []
                    for cucu in range(len(fktemp)/3):
                        cucui = cucu * 3
                        tejaksd = fktemp[cucui]+fktemp[cucui+1]+fktemp[cucui+2]
                        fkasarray.append( int(tejaksd) )
                    gasarray[4] = " ".join(str(we) for we in fkasarray)
                    wi2corrected = (int(gasarray[1])-subtractoverlap ) + (int(t)*texsize)#hoffentlich stimmt das so
                    try:
                        gefunden[gasarray[4]].append([int(gasarray[0]), int(gasarray[1]), int(gasarray[2]), int(gasarray[3]), int(t), gasarray[5]])
                    except:
                        gefunden[gasarray[4]] = [[int(gasarray[0]), int(gasarray[1]), int(gasarray[2]), int(gasarray[3]), int(t), gasarray[5]]]
        cPickle.dump( gefunden, open( "gefunden/GEFUNDEN.txt", "wb" ) )
        print("fk gefunden geschrieben")
    # PUT THE SHIT OUT _ HELL _ NOT _ NEITHER _ NEVER FRITZ3000 HTML
    
    try:
        os.mkdir( outdir )
    except:
        pass
    print("build html")
    cou = 0
    ctsurnAOld = wi1TOcts[0]
    ctsurnA = wi1TOcts[0]
    RESULTSasHTML = []
    for aWI1 in wi1TOcts:
        tempCTSURNA = wi1TOcts[aWI1][1] 
        if(ctsurnA != tempCTSURNA):
            #prepare file and name it like
            zurueck = "Anfang"
            dies = "Anfang"
            vor = "Anfang"
            try:
                zurueck = "URN"+":".join( ctsurnAOld.split("http/CTS")[1].split("/")[0:-1] )
                dies = "URN"+":".join( ctsurnA.split("http/CTS")[1].split("/")[0:-1] )
                vor = "URN"+":".join( tempCTSURNA.split("http/CTS")[1].split("/")[0:-1] )
            except:
                pass

            if(len(RESULTSasHTML) != 0):
                outpoutTOhtml = '<!DOCTYPE html>\n<html lang="de">\n<head>\n<meta charset="utf-8">\n<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">\n<title>Fritz3001 %s</title>\n<meta name="description" content="eaqua ecomparatio gpusearch cts urn document analysis">\n<meta name="author" content="khk">\n<link rel="shortcut icon" href="../pic/favicon.ico">\n<link rel="apple-touch-icon" href="../pic/favicon.ico">\n<script type="text/javascript" src="../js/gpusearch.js"></script>\n<link rel="stylesheet" href="../styles/gpusearch.css" type="text/css">\n</head>\n<body onload="shapeit()">\n<div id="sahne"></div><div id="ninav">\n<span class="gpusearchnav" onclick="openhtml(%s)">Zur&uuml;ck (%s)</span>\n<span class="gpusearchnav">Hier (%s)</span>\n<span class="gpusearchnav" onclick="openhtml(%s)">Vor (%s)</span>\n</div>\n<div id="searchresu">\n%s</div>\n<div id="showINfrag"></div><div id="showINantw"></div></body>\n</html>' % (dies, str(cou-1), zurueck,  dies, str(cou+1), vor, "\n".join(RESULTSasHTML))
                ofh = open( outdir+"/"+str(cou)+".html", "w" )
                ofh.write( outpoutTOhtml )
                ofh.close( )
                print("witten", cou, ".html", len(RESULTSasHTML))
            ctsurnAOld = ctsurnA
            ctsurnA = tempCTSURNA
            cou+=1
            RESULTSasHTML = []
        word = augustintext[aWI1]
        
        aWI1corr = 1
        if(aWI1 != 0):
            aWI1corr = aWI1
        
        
        wonoch = []
        try:
            fk = wi1TOfk[aWI1corr]
            wonoch = fkTOwi1[fk]
        except:
            pass
        woinbtl = []
        try:
            woinbtl = gefunden[fk]
        except:
            pass
        u1out = []
        for i in wonoch:
            #get cts path convert to urn
            try:
                u1out.append( "URN"+":".join( wi1TOcts[i][1].split("http/CTS")[1].split("/")[0:-1] ) )
            except:
                u1out.append( "Fuck" )
        UUlout = []
        UUlout2 = []
        for i in woinbtl:
            #get cts path convert to urn
            try:
                if( i[2] != 0 ):
                    UUlout.append( "URN"+":".join( tiwi2TOcts[str(i[4])+"-"+str(i[1])][1].split("http/CTS")[1].split("/")[0:-1] )+",,"+str(i[2])+",,"+str(i[3])+",,"+str(i[5]) )
                if( i[5] != 0 ):
                    UUlout2.append( "URN"+":".join( tiwi2TOcts[str(i[4])+"-"+str(i[1])][1].split("http/CTS")[1].split("/")[0:-1] )+",,"+str(i[2])+",,"+str(i[3])+",,"+str(i[5]) )
            except:
                UUlout.append( "Fuck" )
        if( len(woinbtl) != 0 ):
            if( len(UUlout) != 0 and len(UUlout2) != 0 ):
                RESULTSasHTML.append( '<div onmouseenter="showFRRA(this)" onmouseout="hideFRRA(this)" id="'+str(aWI1)+'"><span class="w">'+word+'</span><span class="iFr" onclick="showURNofthis(this)" name="'+";;".join(u1out)+'"> Noch: '+str(len(wonoch))+'</span><span class="iAn" onclick="showURNofGef(this)" name="'+";;".join(UUlout)+'"> Gef1: '+str(len(UUlout))+'</span><span class="iAn2" onclick="showURNofGef2(this)" name="'+";;".join(UUlout2)+'"> Gef2: '+str(len(UUlout2))+'</span></div>')
            elif(len(UUlout) != 0 and len(UUlout2) == 0):
                RESULTSasHTML.append( '<div onmouseenter="showFRRA(this)" onmouseout="hideFRRA(this)" id="'+str(aWI1)+'"><span class="w">'+word+'</span><span class="iFr" onclick="showURNofthis(this)" name="'+";;".join(u1out)+'"> Noch: '+str(len(wonoch))+'</span><span class="iAn" onclick="showURNofGef(this)" name="'+";;".join(UUlout)+'"> Gef1: '+str(len(UUlout))+'</span></div>')
            else:
                RESULTSasHTML.append( '<div onmouseenter="showFRRA(this)" onmouseout="hideFRRA(this)" id="'+str(aWI1)+'"><span class="w">'+word+'</span><span class="iFr" onclick="showURNofthis(this)" name="'+";;".join(u1out)+'"> Noch: '+str(len(wonoch))+'</span><span class="iAn2" onclick="showURNofGef2(this)" name="'+";;".join(UUlout2)+'"> Gef2: '+str(len(UUlout2))+'</span></div>')
        else:
            RESULTSasHTML.append( '<div onmouseenter="showFRRA(this)" onmouseout="hideFRRA(this)" id="'+str(aWI1)+'"><span class="w">'+word+'</span><span class="iFr" onclick="showURNofthis(this)" name="'+";;".join(u1out)+'"> Noch: '+str(len(wonoch))+'</span><span></span></div>')
        #print(ctsurnA, word, "in Augustin", wonoch, "in BTL", woinbtl)
        #ergebnisse einfüllen
    enddate = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
    print("END HTML", startdate, "(start date)", enddate, "(now)")
