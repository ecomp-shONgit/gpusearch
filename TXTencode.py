#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, codecs, unicodedata, time, hashlib, pickle

'''
KHK 2017 reads TXT build from CTS -- encodes it in int for gpu search
'''


if __name__ == "__main__":
    print("Loosss!!!!")
    INfage = "TXTBTL/BTL.txt"#"TXT15JH/15JH.txt"
    INantwort = "TXTBTL/BTL.txt"
    INantwBase = "TXTBTL"
    INconcon = "AFconcon"
    OUTenc = "OUTenc"
    alleFragen = "alleFragen"
    #lesen
    afh1 = open( INfage, "r" )
    F = afh1.read().split(" ")
    afh1.close()

    afh2 = open( INantwort, "r" )
    A = afh2.read().split(" ")
    afh2.close()  

   
    codebook = {}
    try:
        os.mkdir( INconcon )
        #ditinct wordlists
        print("Frahen Worte ", len(F), "Antwort Worte ", len(A))
        
        aslist = list(set(F).union(set(A)))
        #countgreek = 0
        ii = 1
        for i in range(len(aslist)):
            #if("greek" in aslist[i]):
            #    countgreek+=1
            while "0" in str(ii):
                ii += 1
            codebook[aslist[i]] = ii
            ii += 1
        print("Codebook max ziffer", ii,"codebooklength",len(codebook), "vorher", len(aslist))        
        
    
        #write codebook
        pickle.dump( codebook, open( INconcon+"/codebook.txt", "wb" ) )
        #print("Greek", (len(aslist)/countgreek)*100, countgreek, len(aslist))
    except Exception as e:
        print(e)
        #read codebook
        codebook = pickle.load( open( INconcon+"/codebook.txt", "rb" ) )
        
        
        pass
    
    
    #encode using the codebook
    try:
        os.mkdir( OUTenc )
    except:
        pass
    #Frage
    encF = []

    for w in F:
        encF.append( str(codebook[w]) )
    pickle.dump( encF, open( OUTenc+"/encF.txt", "wb" ) )
    print("enc F fertig")
    #Antwort
    encA = []

    for w in A:
        encA.append( codebook[w] )

    pickle.dump( encA, open( OUTenc+"/encA.txt", "wb" ) )

    #care for the broken textures
    bropath = INantwBase+"/brokentextures"
    try:
        os.mkdir( OUTenc+"/brokentextures/" )
    except:
        pass
    fifafiles = os.listdir( bropath )
    for name in fifafiles:
        p = "%s/%s" % ( bropath,name )
        print("encode broken textures ", p)
        bef = open( p, "r" )
        cA = bef.read().split(" ")
        bef.close()  
        encBEF = []
        for w in cA:
            encBEF.append( codebook[w] )
        pickle.dump( encBEF, open( OUTenc+"/brokentextures/"+name, "wb" ) )
    
    
    try:
        os.mkdir( alleFragen )
    except:
        pass


    lenencAfortexturecalc = len(encA)
    print("enc A fertig, Buffersize needed: ", lenencAfortexturecalc)
    maxtexwidth = 2000#1600
    while( lenencAfortexturecalc % maxtexwidth  != 0 and maxtexwidth != 0):
        #print(lenencAfortexturecalc % maxtexwidth, maxtexwidth) 
        maxtexwidth-=1
    print("Texture size width", maxtexwidth, "height", lenencAfortexturecalc/maxtexwidth )

    allefragen = {}
    for wi in range(1, (len(encF)-5)):
        currfra = " ".join( encF[wi:wi+5] )
        try:
            allefragen[ currfra ].append( wi )
        except Exception as e:
            allefragen[ currfra ] = [ wi ]

    pickle.dump( allefragen, open( alleFragen+"/allefragen.txt", "wb" ) )

    print("Ähnde")
    
