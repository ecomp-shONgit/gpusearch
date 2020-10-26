#! /usr/bin/env python
# -*- coding: utf8 -*-

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from ctypes import *
#OpenGL.arrays.ctypesparameters
import time, numpy, array, pickle, sys, os, math


#groasze des suchtextes / bildes
global w
global h
#w = 5120
#h = 2590
#w = 3722
#h = 3562
#w = 1024
#h = 1024
w = 2000#1600
h = 1200#1000


# so instead of saying: ESCAPE = 27, we use the following.
ESCAPE = '\033'
# Number of the glut window.
window = 0
texture = 0

PRO1 = None

colloc = [] #pixclor array from text
frageindex = 0 #which frage is computed in shader
fragen = {}
fragenalsfarben = []
global globaltime
globaltime = time.time( )
results = []
outerTEXindex = None
pathtotexture = None

##CPU space data reading, das muß wegen der ziffern codierung als RGBA werte raus, dann sollte genug platz sein!!!
def convertwdstocolors( fromdata, todata, s ):
    count = 0
    countborder =  s

    for wd in fromdata:
        wsplit = reversed( list( str(wd) ))
        r = ''
        g = ''
        b = ''
        ziff = ''
        ccontroll = 1
        #EXTREM WICHTIG _ VON HINTEN müssen die Zahlen auch hinten aufgefüllt werden rgb falsch bgr richtig
        for z in wsplit:
            try:
                int(z)
            except ValueError:
                z = ''
            tempziffer = z + ziff
            if(int(tempziffer) < 256):
                ziff = tempziffer
                if(len(ziff) == 3):
                    if(ccontroll == 1):
                        b = ziff
                        ziff = ''
                        ccontroll+=1
                    elif(ccontroll == 2):
                        g = ziff
                        ziff = ''
                        ccontroll+=1
                    elif(ccontroll == 3):
                        r = ziff
                        ziff = ''
                        ccontroll+=1
                    else:
                        raise Exception('wortzahl zu farbe extremer Fehler - ziifern zu groß', wb)
            else:
                if(ccontroll == 1):
                    b = ziff
                    ziff = ''
                    ccontroll+=1
                elif(ccontroll == 2):
                    g = ziff
                    ziff = ''
                    ccontroll+=1
                elif(ccontroll == 3):
                    r = ziff
                    ziff = ''
                    ccontroll+=1
                else:
                    raise Exception('wortzahl zu farbe extremer Fehler - ziifern zu groß', wb)
                ziff = z
        if(ziff != ''):#letztes
            if(ccontroll == 1):
                b = ziff
            elif(ccontroll == 2):
                g = ziff
                    
            elif(ccontroll == 3):
                r = ziff
        #print(wd, "zu", r, g, b)

        if( r == '' ):
            r = '0'
        if( g == ''):
            g = '0'
        if( b == '' ):
            b = '0'
            #print r
        #print(wd, wsplit, r, g, b)
        if( count < countborder ):
            todata.append( int( r ) )
            todata.append( int( g ) )
            todata.append( int( b ) )
        else:
            #print(todata)
            break
        count +=1
    while(count < countborder):
        todata.append( 0 )
        todata.append( 0 )
        todata.append( 0 )
        count +=1

def readCPUfragen( inpath, fra, fraalsfarben ):
    print("Fragen ", inpath)
    try:
        fra = pickle.load( open( inpath, "rb" ) )
    except IOError:
        print( "could not read enc fragen " + inpath )
        return
    print("readed fragen 5 worte")
    #fru = {}
    frucount = 0
    for frifra in fra:
        #if(frucount < 1000):
        #    fru[frifra] = fra[frifra]
        frucount+=1
        f = frifra.split(" ")
        ascolors = []
        convertwdstocolors(f, ascolors, len(f))
        fraalsfarben.append( ascolors )
    print(frucount, "Anzahl der Fragen")
    #pickle.dump( fru, open( "alleFragen/allefragenklein.txt", "wb" ) )
    print( "conved fragen, Anzahl: ", frucount )
    
def readCPUdata( inpath, todata, vecSize ):
    print("Suchbildddd ", inpath)
    #c = 1
    #for b in range(vecSize):
    #    if(b < 10000):
    #        todata.append(c)
    #        todata.append(0)
    #        todata.append(0)
    #        c+=1
    #        if(c == 256):
    #            c=1

    #    else:
    #        todata.append(0)
    #        todata.append(0)
    #        todata.append(0)
    wds = []
    try:
        wds = pickle.load( open( inpath, "rb" ) )
    except IOError:
        print( "could not read enc file " + inpath )
        return
    print("text as pixel readed")
    convertwdstocolors( wds, todata, vecSize )
    print("conved words as colors, Anzahl (Worte):", len(todata)/3)




# Vertex shader grüst
VS = """
#version 120
varying vec2 tex_coord;
void main()
{
   //tex_coord = gl_MultiTexCoord0.st;//1d
   tex_coord = gl_MultiTexCoord0.xy;//2d
   gl_Position = gl_ProjectionMatrix * gl_ModelViewMatrix * gl_Vertex;
}
"""

# Fragment shader
FS = """
#version 120
uniform sampler2D tex2d;//zum lesen der Textur
uniform float texwidth;//Eingabe de Gesamtmaße
uniform float texheight;

uniform int fragecol[15];


//varying vec2 tex_coord;
void main()
{
    //gl_FragColor = texture1D(tex, tex_coord.s); //1d
    //!!!!!!!!!!!!
    vec4 wcolor = texture2D(tex2d, vec2(((gl_FragCoord.x)/texwidth), ((gl_FragCoord.y)/texheight)));
//die texure2D Funktion nimmt normalerweise Texturcoordinaten ( die UV Koordinaten sind, also 0,1 (z) und -1,1 normisierte Werte (x,y). Die Fragment Coodinaten bewegen sich aber in den tatsäcklichen Ausdehnungen der GLUT Fenster. Daher muß die UV Umrechnung selbst gemacht werden. Anschließend wird ein Verctor der Länge 2 (Funktion vec2) erstellt und der Texturfunktion übergeben. Ein Farbvector (Typ: Vec4) ist das Ergebnise und entspricht dem Farbwert des Pixels der Textur.
    //extrem wichtig funktioniert nur wenn text size = w*h window
    //!!!!!!!!!!!

   vec4 ergcolor = vec4( 0, 0, 0, 255 );
   int colorindexoffound[5] = int[5](-1, -1, -1, -1 ,-1);
   int localabstand[5] = int[5](-1, -1, -1, -1 ,-1);
    for(int t = 0; t < 5; t++){//für alle Wörter der Frage wird kontrolliert --
        int ti = t*3;//Farbarray index berechnen aus index des Wortarrays
        if( fragecol[ti] == int(floor((wcolor[0]*255.0) +0.5)) &&
            fragecol[ti+1] == int(floor((wcolor[1]*255.0)+0.5)) &&
            fragecol[ti+2] == int(floor((wcolor[2]*255.0)+0.5))){ //-- OB das Pixel in dem der Shader ausgeführt wird (wcolor) eine identische Farbe hat (identische Wortform) - wenn dem nicht so ist, dann bleibt ercolor schwarz (Wert: 0,0,0,255 ) - wenn dem so ist dann wird gesucht
            int founcount = 1;
            int founcountshortdist = 1;
            int oldindex = 0;
            colorindexoffound[t] = 0; //hier wird in einem array aufgeschrieben, ob der Farbwert schon vorkam und zwar in dem man die Entfernung zum ersten Fund aufschreibt, also 0 für das erste gefundene Wort 
            localabstand[t] = 0;
            float ax = gl_FragCoord.x;
            float ay = gl_FragCoord.y;
            for(int j = 0; j < 101; j++){
                //Berechnung der Koordinaten unter berücksichtigung der Ausdehnung und das es 2D Koordinaten sind, und am horizontalen Ende umgekehrt werden muß
                if( ax < (texwidth-1.5) ){ //das Itterations kriterium, ist hier mit Textbreite minus 1.5 angegeben, weil die Pixelkoordinaten bei bei halben Pixeln gebildet werden, das erste Pixel liegt also nicht bei 0, sondern bei 0.5, sofern ich also noch 1 Addieren kann, ohne die Textbreite zu erreichen kann ich weiter machen. Anders verließe man den ordinal möglichen Bereich, weil man eine kardinale Grenze einließt. Man kann von 0.5 bis 10.5 (Schrittweite 1) und hat 11 Werte eingelesen. 
                        ax = ax + (1.0);
                    } else {
                        ax = 0.5;
                        if( ay < (texheight-1.5) ){
                            ay = ay + (1.0);
                        } else {
                            break;
                        }
                    }
                    vec4 cecolor = texture2D( tex2d, vec2((ax/texwidth), (ay/texheight)) );
                for(int tt = 0; tt < 5; tt++){//Kontrolle, ob dieser Farbwert eine Identität zu einem der Fragefarbwerte hat und dieser noch nicht als gefunden im  colorindexoffound Array vermerkt ist. 
                    int tti = tt*3;
                    if(colorindexoffound[tt] == -1){
                        if( fragecol[tti] == int(floor((cecolor[0]*255.0)+0.5)) &&
                            fragecol[tti+1] == int(floor((cecolor[1]*255.0)+0.5)) &&
                            fragecol[tti+2] == int(floor((cecolor[2]*255.0)+0.5))){
                                //short distance count
                                if( j < 10 ){
                                    founcountshortdist++;
                                }
                                founcount++;
                                colorindexoffound[tt] = j;
                                localabstand[tt] = j - oldindex;
                                oldindex = j;
                        }
                    }
                }
                if(founcount > 4){ //wenn alle Farbwerte der Frage gefunden wurden, dann kann man mit der Suche abschließen, sonst endet diese nach 200 Wörtern
                    //ergcolor = vec4( 255, 0, 0, 255 );
                    //Durchschnittswerte der Abstände als Maße speichern
                    int sumitup = 0;
                    int sumitup2 = 0;
                    for(int susu = 0; susu < 5; susu++){
                        sumitup += colorindexoffound[susu];
                        sumitup2 += localabstand[susu];
                    }
                    ergcolor[0] = (sumitup/4)/255.0; //es müssen Float Farbwerte im Array stehen!!!
                    ergcolor[1] = (sumitup2/4)/255.0; //es müssen Float Farbwerte im Array stehen!!!
                    break;
                }
            }
            

            if(founcountshortdist > 2){ //min 3 aus 5 in 10 abstand 
                ergcolor[2] = founcountshortdist/255.0;
            }
            break;
        }
    }
   //set result as color - to get it from buffer
   gl_FragColor = ergcolor;
   //gl_FragColor =  wcolor; //for testing if returend texture ist equal with the original texture


}
"""

def compile_vertex_shader(source):
	"""Compile a vertex shader from source."""
	vertex_shader = glCreateShader(GL_VERTEX_SHADER)
	glShaderSource(vertex_shader, source)
	glCompileShader(vertex_shader)
	# check compilation error
	result = glGetShaderiv(vertex_shader, GL_COMPILE_STATUS)
	if not(result):
		raise RuntimeError(glGetShaderInfoLog(vertex_shader))
	return vertex_shader

def compile_fragment_shader(source):
	"""Compile a fragment shader from source."""
	fragment_shader = glCreateShader( GL_FRAGMENT_SHADER )
	glShaderSource(fragment_shader, source)
	glCompileShader(fragment_shader)
	# check compilation error
	result = glGetShaderiv(fragment_shader, GL_COMPILE_STATUS)
	if not(result):
		raise RuntimeError(glGetShaderInfoLog(fragment_shader))
	return fragment_shader

def link_shader_program(vertex_shader, fragment_shader):
    """Create a shader program with from compiled shaders."""
    program = glCreateProgram()
    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)
    glLinkProgram(program)
    # check linking error
    result = glGetProgramiv(program, GL_LINK_STATUS)
    if not(result):
        raise RuntimeError(glGetProgramInfoLog(program))


    return program

def init_shader_program():
    #versionString = glGetString(GL_VERSION).split(" ")
    #openglVersionString = versionString[0]
    #openglVersionNums = map(int, openglVersionString.split("."))
    #if openglVersionNums[0] < 3 or (openglVersionNums[0] == 3 and openglVersionNums[1] < 3):
	#    exit("Requires opengl 3.3 or better, you have {0}".format(openglVersionString))

    # background color
    glClearColor(0, 0, 0, 0)
    # create a Vertex Buffer Object with the specified data

    vertex_shader = compile_vertex_shader( VS )
    fragment_shader = compile_fragment_shader( FS )	

    program = link_shader_program(vertex_shader, fragment_shader)

    return program

def LoadTextures():
    #global texture
    global pathtotexture
    readCPUdata( pathtotexture, colloc, w*h )
    readCPUfragen( "alleFragen/allefragen.txt", fragen, fragenalsfarben )
    #readCPUfragen( "alleFragen/allefragenklein.txt", fragen, fragenalsfarben )
    #readCPUdata( "OUTenc/encA.txt", colloc, 5000 )#alles - größe ist????
    #print(len(colloc))

    # Create Texture

    #glBindTexture(GL_TEXTURE_1D, glGenTextures(1))   # 1d texture (x size)
    glBindTexture(GL_TEXTURE_2D, glGenTextures(1)) # 2 d texture (x y sized)

    glPixelStorei(GL_UNPACK_ALIGNMENT,1)
    #print(w,h,"sssss", colloc[0:10])
    #glTexImage1D(GL_TEXTURE_1D, 0, GL_RGB8, 100, 0, GL_RGB, GL_UNSIGNED_BYTE, colloc)# 1d texture
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, w, h, 0, GL_RGB, GL_UNSIGNED_BYTE, colloc)# 2d texture, musz RGBA sein!!!!

    #2d texture
    #glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    #glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    #glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    #glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    #glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP);
    #glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP);

    #glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, 0);
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    #glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

    # 1d texture
    #glTexParameterf(GL_TEXTURE_1D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    #glTexParameterf(GL_TEXTURE_1D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)


# A general OpenGL initialization function.  Sets all of the initial parameters.
def InitGL():                # We call this right after our OpenGL window is created.
    print("OpenGL Version: ", glGetString ( GL_VERSION ))
    print("Shading Language Version: ", glGetString( GL_SHADING_LANGUAGE_VERSION ))
    glmaxtexsize = glGetIntegerv(GL_MAX_TEXTURE_SIZE)
    print("Sys max texture size: ", glmaxtexsize, "x", glmaxtexsize, " (",glmaxtexsize*glmaxtexsize,") " , " needed size: ", w, "x", h, " (", w*h, ")")

    LoadTextures()
    glEnable(GL_BLEND);

    #glEnable(GL_TEXTURE_1D) #1d texture
    glEnable(GL_TEXTURE_2D) #2d texture
    glClearColor(0.0, 0.0, 0.0, 0.0)    # This Will Clear The Background Color To Black
    #glClearDepth(1.0)                    # Enables Clearing Of The Depth Buffer
    #glDepthFunc(GL_LESS)                # The Type Of Depth Test To Do
    #glEnable(GL_DEPTH_TEST)                # Enables Depth Testing
    #glShadeModel(GL_FLAT)                # Enables Smooth Color Shading

    #glMatrixMode(GL_PROJECTION)
    #glLoadIdentity()                    # Reset The Projection Matrix
                                        # Calculate The Aspect Ratio Of The Window
    #gluPerspective(45.0, float(w)/float(h), 0.1, 100.0)
    #gluPerspective(90.0, float(w)/float(h), 1.0, 100.0);
    #glMatrixMode(GL_MODELVIEW)
    glMatrixMode(GL_PROJECTION);
    #glPushMatrix();
    glLoadIdentity();
    #glOrtho(0.0, float(w), float(h), 0.0, 0.0, 1.0); #(left, right, bottom, top, near, far)
    glOrtho(0.0, float(w), 0.0, float(h), 0.0, 1.0);
    glMatrixMode(GL_MODELVIEW);
    global PRO1
    PRO1 = init_shader_program()
    glUseProgram( PRO1 )

    #glPushMatrix();
# The function called when our window is resized (which shouldn't happen if you enable fullscreen, below)
def ReSizeGLScene( nw, nh ):
    if( nh == 0):                        # Prevent A Divide By Zero If The Window Is Too Small
        nh = 1

    glViewport(0, 0, nw, nh)        # Reset The Current Viewport And Perspective Transformation
    #...

# The main drawing function.
def DrawGLScene():

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)    # Clear The Screen And The Depth Buffer
    glLoadIdentity()                    # Reset The View

    glClearColor(0.0,0.0,0.0,0.0)

    #glDisable(GL_LIGHTING);
    #pass frage to shader
    #print(PRO1)

    global frageindex
    if(frageindex > len(fragenalsfarben)-1):
        sys.exit()

    #print("frageindex",frageindex)
    lo = glGetUniformLocation( PRO1, "fragecol" )
    currfrage = fragenalsfarben[frageindex]
    glUniform1iv( lo, 15,  currfrage)
    lolo = glGetUniformLocation( PRO1, "texwidth" )
    glUniform1f( lolo,  float(w) )
    lololo = glGetUniformLocation( PRO1, "texheight" )
    glUniform1f( lololo, float(h) )
    #lololow = glGetUniformLocation( PRO1, "fifi" )

    #glUniform1i( lololow, fragenalsfarben[frageindex][0] )


    #glTranslatef(0.0,0.0,-15.0)            # Move Into The Screen


    # Note there does not seem to be support for this call.
    #glBindTexture(GL_TEXTURE_2D,texture)    # Rotate The Pyramid On It's Y Axis

    glBegin(GL_QUADS)                # Start Drawing The Cube

    #textured quad
    #glTexCoord2f(0.0, 0.0); glVertex3i(0, 0, 0);
    #glTexCoord2f(1.0, 0.0); glVertex3i(w, 0, 0);
    #glTexCoord2f(1.0, 1.0); glVertex3i(w, h, 0);
    #glTexCoord2f(0.0, 1.0); glVertex3i(0, h, 0);

    #glTexCoord2f(0.0, 0.0); glVertex3i(0, 0, 0);
    #glTexCoord2f(0.0, 1.0); glVertex3i(0, h, 0);

    #glTexCoord2f(1.0, 1.0); glVertex3i(w, h, 0);
    #glTexCoord2f(1.0, 0.0); glVertex3i(w, 0, 0);


    #blanc quad
    glVertex3i(0, 0, 0);
    glVertex3i(w, 0, 0);
    glVertex3i(w, h, 0);
    glVertex3i(0, h, 0);
    glEnd();

    #
    #xrot  = xrot + 0.2                # X rotation
    #yrot = yrot + 0.2                 # Y rotation
    #zrot = zrot + 0.2                 # Z rotation
    #
    #  since this is double buffered, swap the buffers to display what just got drawn.
    glutSwapBuffers()

    #get back the data
    #glPixelStorei(GL_PACK_ALIGNMENT,1)
    # das lag daran, das hier ein string aus hex werten zurück gegeben wurde und zwar ist die obere linke ecke des fensters der letzte wert
    # im array, dann muß man einfach in der Reihenfolge BGR die Fraben ausgeben und alles umdrehen, dann hat man die texture zurück
    #backdata = list(reversed(map(ord, list(glReadPixels(0, 0, w, h, GL_BGR, GL_UNSIGNED_BYTE)))))

    backdata = ( GLubyte * (3*w*h) )(0)
    glReadPixels(0, 0, w, h, GL_RGB, GL_UNSIGNED_BYTE, backdata)

    #shit = 0
    #for b in range(0, len(colloc)/3):
    #    d = b*3
    #    if(backdata[d] != colloc[d] or
    #       backdata[d+1] != colloc[d+1] or
    #       backdata[d+2] != colloc[d+2] ):
            #print(b, backdata[b],colloc[b], backdata[b+1],colloc[b+1], backdata[b+2], colloc[b+2])
        #if(backdata[b] != 0 and backdata[b] != 255):
    #        shit+=1
    #problem shcon mla - col hat zu große zahlen - da muß auf die zifferen nicht die stellen geachtet werden bei der Zerlegung!!!

    #print(backdata[0:10], colloc[0:10], "shit: ", shit, len(colloc)/3, len(backdata)/3, w*h)

    #print("equal", (colloc==backdata))
    noshit = 0
    fI1 = []
    global results
    currfragekey = " ".join(str(wn) for wn in currfrage)
    #indexfrage indexfund und abstand fund muß geschrieben werden in einem Thread
    for b in range(0, math.floor(len(backdata)/3)):
        #if( backdata[b*3] != 0 or backdata[(b*3)+2] != 0):
        if( backdata[b*3] or backdata[(b*3)+2] ):
            #noshit += 1
            #results.append([frageindex, b, backdata[(b*3)+1], backdata[(b*3)+2], currfragekey])
            results.append( str(frageindex)+","+ str(b)+","+str(backdata[b*3])+","+str(backdata[(b*3)+1])+","+ str(currfragekey)+","+str(backdata[(b*3)+2]))
            #print(currfragekey)
            #fI1.append(backdata[(b*3)+1])
            #fI1.append(backdata[(b*3)+2])
            #fI1.append("--")

    if(len(results) > 10000):
        #print(results[0:10])
        ofh = open( "gefunden/"+str(outerTEXindex)+"/"+str(frageindex)+".txt", "a" )#append if exits
        ofh.write( ";".join( results ) )
        ofh.close( )
        #pickle.dump( results, open( "gefunden/"+str(frageindex)+".txt", "wb" ) )#append!!!
        results = []
        print( frageindex, " Zeit je Frame (10000 Erg.): ", time.time() - globaltime)
    #print(fragenalsfarben[frageindex])
    #print(" found count:", noshit)
    '''
    countgood = 0
    fI2 = []

    for b in range(0, len(colloc)/3):
        bi = b*3
        for c in range(len(fragenalsfarben[frageindex])/3):
            ci = c*3
            if( colloc[bi] == fragenalsfarben[frageindex][ci] and
                colloc[bi+1] == fragenalsfarben[frageindex][ci+1] and
                colloc[bi+2] == fragenalsfarben[frageindex][ci+2] ):
                resultfillinindex = [-1, -1, -1, -1, -1]
                fc = 1
                resultfillinindex[c] = c
                for s in range(1, 201):
                    si = s*3
                    for cc in range(len(fragenalsfarben[frageindex])/3):
                        cci = cc*3
                        if(si+bi+2 < len(colloc) and resultfillinindex[cc] == -1):
                            if( colloc[si+bi] == fragenalsfarben[frageindex][cci] and
                                colloc[si+bi+1] == fragenalsfarben[frageindex][cci+1] and
                                colloc[si+bi+2] == fragenalsfarben[frageindex][cci+2] ):
                                fc+=1
                                resultfillinindex[cc] = cc

                if(fc > 4):
                    countgood+=1
                    fI2.append(b)
                break

    intersection = list(set(fI2).intersection(fI1))
    print("checked", countgood, " found count:", noshit, "diff ", abs(countgood-noshit), len(intersection), fI1[0:10], fI2[0:10])
    '''
    #print("fffoouunndd", noshit, fI1[0:22])
    #print("fffoouunndd", noshit, currfragekey, frageindex)
    frageindex+=1

# The function called whenever a key is pressed. Note the use of Python tuples to pass in: (key, x, y)
def keyPressed(*args):
    # If escape is pressed, kill everything.
    if( args[0] == ESCAPE ):
        sys.exit()

def main():

    global window

    global outerTEXindex
    outerTEXindex = sys.argv[1] #
    try:
        os.mkdir( "gefunden/"+str(outerTEXindex) )
    except:
        pass
    global pathtotexture
    pathtotexture = sys.argv[3] #

    glutInit(sys.argv)



    # Select type of Display mode:
    #  Double buffer
    #  RGBA color
    # Alpha components supported
    # Depth buffer
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)

    # get a 640 x 480 window

    glutInitWindowSize( w, h )

    # the window starts at the upper left corner of the screen
    glutInitWindowPosition(0, 0)

    window = glutCreateWindow("CTS TO GPUSEARCH, textureindex = "+str(outerTEXindex))

       # Register the drawing function with glut, BUT in Python land, at least using PyOpenGL, we need to
    # set the function pointer and invoke a function to actually register the callback, otherwise it
    # would be very much like the C version of the code.
    glutDisplayFunc(DrawGLScene)

    # Uncomment this line to get full screen.
    #glutFullScreen()

    # When we are doing nothing, redraw the scene.
    glutIdleFunc(DrawGLScene)

    # Register the function called when our window is resized.
    glutReshapeFunc(ReSizeGLScene)

    # Register the function called when the keyboard is pressed.
    glutKeyboardFunc(keyPressed)

    # Initialize our window.
    InitGL()


    # Start Event Processing Engine
    glutMainLoop()

# Print message to console, and kick off the main to get it rolling.
if __name__ == "__main__":
    #get called by a python programm that starts this 
    #get input of texture index and start the programm, care for overlap
    print( "Hit ESC key to quit." )
    try:
        os.mkdir( "gefunden" )
    except:
        pass
    
    main()
    nowis = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
    print( "ENDE GPU SEARCH ", nowis )
