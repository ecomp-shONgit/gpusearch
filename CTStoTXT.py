#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, codecs, unicodedata, time, hashlib, cPickle, glob, re

'''
Prof. Charlotte Schubert, Alte Geschichte Leipzig 2017 

The script split CTS like folder structure / any folder structure into a TXT AND INDEXLIST of contained textes, perform text nomalization.

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
# files / pathes
namespace = "15JH"
inp1 = "/xx/xx/xx/xx/15JH"
outpp = "TXT15JH"
    
namespace2 = "BTL"
inp2 = "/xx/xx/xx/xx/BTL"
outpp2 = "TXTBTL"

#screen resolution
w = 1600
h = 1000
texsize = w*h

#norm config
doUVlatin = 1


###
def sameuninorm( aword, wichnorm ):
    return unicodedata.normalize( wichnorm, aword ) 

def normword( aword ):
    return ''.join( map( lambda x: x.lower() if (unicodedata.category(x) in 'Mn Cc Cf Cn Co Cs Mc Me Nd No Pc Pl Pd Pf Pi Po Sc Sk Sm So Zl Zs') == False else '' , list( unicodedata.normalize( 'NFD', aword ) ) ) )

def nodiakinword( aword ):
    spt = list( unicodedata.normalize( 'NFD', aword.replace(u"’", "").replace(u"'", "").replace(u"᾽", "").replace(u"´", "") )  )
    
    for l in range(len(spt)):
        if(unicodedata.category(spt[l]) == "Mn"):
            #ersetze iota subscritum mit iota adscriptum
            if("YPOGEGRAMMENI" in unicodedata.name( spt[l] ) ):
                spt[l] = u"ι"
            else:
                spt[l] = ""
        
    t = "".join(spt)
    #print(t)
    return t
def delall( text ):
    delledtext = text
    if( doUVlatin == 1 ):
        delledtext = deluv( delklammern( sigmaistgleich( delgrkl( delumbrbine( delligaturen( delinterp( deldiak(  text))))))))
    else:
        delledtext = delklammern( sigmaistgleich( delgrkl( delumbrbine( delligaturen( delinterp( deldiak(  text  ) ) ) ) ) ) )
    return delledtext
        
def delligaturen( text ):
    ct = text
    newstring = ct.replace(u"ϛ", u"στ").replace(u"Ȣ", u"ου").replace(u"ꙋ", u"ου").replace(u"ϗ", u"καὶ").replace( u"\u0223", "\u039F\u03C5" ).replace( u"\u0222", "\u03BF\u03C5" ).replace( u"\u03DA", "\u03A3\u03C4" ).replace( u"\u03DB", "\u03C3\u03C4" )
    return newstring

def deldiak( text ):
    ct = text 
    spt = ct.split( " " )
    for wi in range( len(spt) ):
        nw = spt[ wi ] 
        spt[ wi ] = nodiakinword( nw )
    return  " ".join( spt )
    
def delinterp( text ):
    return text.replace(u":", "").replace(u".", "").replace(u",", "").replace(u";", "").replace(u"·", "").replace(u"·", "").replace(u"!", "").replace(u"?", "").replace(u"“", "").replace(u"„", "").replace(u"”", "").replace(u"\"", "").replace(u"'", "").replace("~", "")

def delumbrbine( text ):
    return text.replace("<br/>", "").replace("<br>", "")

def delumbrbinemitleer( text ):
    return text.replace("\n", " ").replace("-<br/>", "").replace("-\n", "").replace("-\n ", "").replace("- <br/>", "").replace("- \n", "").replace("<br/>", " ").replace("<br>", " ")

def delgrkl( text ):
    ct = text.lower()
    return ct

def sigmaistgleich( text ):
    return text.replace(u"ς", u"σ")

def delklammern( text ):
    return text.replace("(", "").replace(")", "").replace("{", "").replace("}","").replace("]","").replace("[","").replace(">","").replace("<","").replace(u"⌈","").replace(u"⌉","").replace("[","").replace("]","")

def deluv( text ):
    return text.replace( "u", "v" )
def normatext( text, wichnorm ):
    spt = text.split(" ")
    for w in range( len( spt ) ):
        nw = sameuninorm( spt[ w ], wichnorm )
        spt[ w ] = nw
    return " ".join( spt )

def replaceOPENINGandCLOSING( astopen, astclose, strstr):
    no = strstr.split( astclose )
    NO = ""
    for n in no:
        NO += n.split( astopen )[0]
    return NO

def replaceWordsfromarray( arr, strstr ):
    for a in arr:
        strstr = strstr.replace(arr[a], "")
    return strstr

def cleanFROMTAGSandmore( stringggg ):
    #processing=man processing=man
    stringggg = stringggg.replace('<foreign xml:lang="greek">', "").replace("</foreign>", "").replace('<s processing="manual">', '').replace("</s>", "").replace('<named-content content-type="non-latin-word" specific-use="greek">', '').replace('<named-content content-type="non-latin-word" specific-use="german">', '').replace('</citn>','').replace('<citn>','').replace('</l>','').replace('<l>','').replace('<hi rend="italic">', '').replace('</hi>', '').replace('</p>','').replace('</div1>','').replace('</div2>','').replace('<line>', '').replace('</line>', '').replace('<named-content content-type="excl">', '').replace('</named-content>', '').replace('&lt;', '').replace('&gt;', '').replace(';', '').replace(':', '').replace(',', '').replace('.', '').replace('?', '').replace('!', '').replace("|", "").replace("\\\\", "").replace("+", "")
    ws = stringggg.replace("\n", " <br/>").replace("\r", " <br/>").replace(u"—",u" — ").split(" ") #keep konvention with newlines
    ca = []
    halfw = ""
    secondhalf = ""
    for w in range( len( ws ) ):
        if( "-" in ws[w] ):
            h = ws[w].split("-")
            halfw = h[0].replace(" ", "")
            secondhalf = h[1].replace(" ", "")
            if( "]" in secondhalf ): 
                hh = h[1].split("]")
                if( len( hh[1] ) > 1 ):
                    ca.append( halfw + hh[1] + " " + hh[0] + "]<br/>" )
                    halfw = ""
                    secondhalf = ""
            #print( ws[w], ws[w].split("-"))
        elif ( "<br/>" != ws[w] and ws[w] != "" and ws[w] != " " and halfw != "" ):
            if("]" in ws[w]):
            
                secondhalf = ws[w].replace(" ", "")
            else:
                ca.append( halfw + ws[w].replace("<br/>", "") + " " + secondhalf + "<br/>" ) 
                halfw = ""
                secondhalf = ""
        else:
            
            if( ws[w] != "" ): 
                ca.append( ws[w] )
    c = delumbrbine( " ".join( ca ) )
    cc = c.split(" ") 
    goon = True
    l = 0
    while(goon): 
        if( len(cc[l]) < 1 or cc[l] == " " ):
            cc.pop(l)
        if(len(cc)-1 <= l):
            goon = False
        else:
            l = l + 1
    stringggg = " ".join( cc ).replace("-", "").replace("'", "").replace('"', "").replace("<br/>", " ").replace("\n", " ").replace("\t", " ").replace(u"‧","").replace(u"·", "")
    
    #here is some addiional replacing needed
    stringggg = re.sub( r'\(([A-Za-z0-9\.\:\; ]+|([0-9\.\:\; ]+))\)', '', stringggg ) 
    stringggg = re.sub( r'\[([0-9\.\:\; ]+)\]', '', stringggg)

    stringggg = replaceOPENINGandCLOSING( '<NOTE', '</NOTE>', stringggg)
    stringggg = replaceOPENINGandCLOSING( '<HEAD', '</HEAD>', stringggg)#?

    stringggg = delall( stringggg )
    return stringggg


def sort_nicely( l ):
    """ Sort the given list in the way that humans expect. - extreamly important
    """
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    l.sort( key=alphanum_key )


def  CTStoTXT( NS, inparray, outp ): #
    indexTOctsurn = {}
    ALLTXT = []
    bigI = 0
    
    for inpa in inparray:
        allroots = []
        oldr = ""
        for root, dirs, files in os.walk( inpa ):
            if(root != oldr):
                allroots.append(root)
            oldr = root
        sort_nicely( allroots )
        #so important to get the right sorting --- extrem
        for rr in allroots:
            fifafiles = os.listdir( rr )
            for name in fifafiles:
                if name.endswith(".xml"):
                    #print(rr, name)
                    p = "%s/%s" % ( rr,name )
                    
                    afh = codecs.open( p, encoding='utf-8')
                    aDaa = normatext(  cleanFROMTAGSandmore( afh.read().lower() ), "NFC" )
                    afh.close() 
                    aDaaA = aDaa.split(" ")
                    for aw in aDaaA:
                        cleanedword = aw.encode( "utf-8" )
                        if( cleanedword != "" and cleanedword != " " ):
                            ALLTXT.append( cleanedword )
                            quiqua = [bigI, p]
                            indexTOctsurn[bigI] = quiqua 
                            bigI += 1
                    print(p)   
    try:
        os.mkdir( outp )
    except:
        pass  
    ofh = open( outp+"/"+NS+".txt", "w" )
    ofh.write( " ".join( ALLTXT ) )
    ofh.close( )
    o2fh = open( outp+"/"+NS+".index", "wb" )
    cPickle.dump( indexTOctsurn, o2fh )
    o2fh.close( )

                
def  CTStoTXTbrokentextures( NS, inparray, outp ): #
    indexTOctsurn = {}
    ALLTXT = []
    bigI = 0
    #index for broken textures
    textreI = 0
    intratexI = 0
    brokenTXT = []
    bropath = outp+"/brokentextures"
    #direktory for broken textures
    try:
        os.mkdir( outp )
    except:
        pass  
    try:
        os.mkdir( bropath )
    except:
        pass 


    for inpa in inparray:
        allroots = []
        oldr = ""
        for root, dirs, files in os.walk( inpa ):
            if(root != oldr):
                allroots.append(root)
            oldr = root
        sort_nicely( allroots )
        #so important to get the right sorting --- extrem
        for rr in allroots:
            fifafiles = os.listdir( rr )
            for name in fifafiles:
                if name.endswith(".xml"):
                    p = "%s/%s" % ( rr,name )
                    
                    afh = codecs.open( p, encoding='utf-8')
                    aDaa = cleanFROMTAGSandmore( normatext( afh.read(), "NFC" ) )
                    afh.close() 
                    aDaaA = aDaa.split(" ")
                    
                   
                    for aw in aDaaA:
                        cleanedword = aw.encode( "utf-8" )
                        if( cleanedword != "" and cleanedword != " " ):
                            ALLTXT.append( cleanedword )
                            brokenTXT.append( cleanedword )
                            #care for the broken textures
                            if( len(brokenTXT) == texsize ):
                                #write
                                bfh = open( bropath+"/"+str(textreI)+"-"+str(intratexI)+".txt", "w" )
                                bfh.write( " ".join( brokenTXT ) )
                                bfh.close( )
                                print("Bokentexture as text written", textreI, intratexI)
                                #reset the index and array
                                brokenTXT = brokenTXT[-199:] 
                                intratexI = len(brokenTXT) #(overlap)
                                textreI += 1
                            quiqua = [bigI, p, textreI, intratexI]
                            indexTOctsurn[str(textreI)+"-"+str(intratexI)] = quiqua
                            bigI += 1
                            intratexI += 1
                    print(p)
                    
    if(len(brokenTXT) != 0):
        bfh = open( bropath+"/"+str(textreI)+"-"+str(intratexI)+".txt", "w" )
        bfh.write( " ".join( brokenTXT ) )
        bfh.close( )
        print("(last) Bokentexture as text written ", textreI, intratexI)
   
    
    ofh = open( outp+"/"+NS+".txt", "w" )
    ofh.write( " ".join( ALLTXT ) )
    ofh.close( )
    o2fh = open( outp+"/"+NS+".index", "wb" )
    cPickle.dump( indexTOctsurn, o2fh )
    o2fh.close( )
if __name__ == "__main__":

    print("Loosss!!!!")

    
    CTStoTXT( namespace, [inp1], outpp )

    CTStoTXTbrokentextures( namespace2, [inp2], outpp2 )
    
    print("Ennddd!!!!")
