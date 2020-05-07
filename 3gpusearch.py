#! /usr/bin/env python
# -*- coding: utf8 -*-

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from ctypes import *
#OpenGL.arrays.ctypesparameters
import time, numpy, array, cPickle, sys, os

'''
Prof. Charlotte Schubert, Alte Geschichte Leipzig 2017 

Script performs gpu search.

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

#GLOBALS
#groasze des suchtextes / bildes
global w
global h

w = 1600
h = 1000


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
        fi = open( inpath, "rb" )
        fra = cPickle.load( fi )
    except IOError:
        print( "could not read enc fragen " + inpath )
        return
    print("readed fragen 5 worte")
    #fru = {}
    frucount = 0
    for frifra in fra:
        frucount+=1
        f = frifra.split(" ")
        ascolors = []
        convertwdstocolors(f, ascolors, len(f))
        fraalsfarben.append( ascolors )
    print(frucount, "Anzahl der Fragen")
    print( "conved fragen, Anzahl: ", frucount )

def readCPUdata( inpath, todata, vecSize ):
    print("Suchbildddd ", inpath)
    wds = []
    try:
        fi = open( inpath, "rb" )
        wds = cPickle.load( fi )
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
    //!!!!!!!!!!!

   vec4 ergcolor = vec4( 0, 0, 0, 255 );
   int colorindexoffound[5] = int[5](-1, -1, -1, -1 ,-1);
   int localabstand[5] = int[5](-1, -1, -1, -1 ,-1);
    for(int t = 0; t < 5; t++){//für alle Wörter der Frage wird kontrolliert --
        int ti = t*3;//Farbarray index berechnen aus index des Wortarrays
        if( fragecol[ti] == int(floor((wcolor[0]*255.0) +0.5)) &&
            fragecol[ti+1] == int(floor((wcolor[1]*255.0)+0.5)) &&
            fragecol[ti+2] == int(floor((wcolor[2]*255.0)+0.5))){ 
            int founcount = 1;
            int founcountshortdist = 1;
            int oldindex = 0;
            colorindexoffound[t] = 0; 
            localabstand[t] = 0;
            float ax = gl_FragCoord.x;
            float ay = gl_FragCoord.y;
            for(int j = 0; j < 101; j++){
                if( ax < (texwidth-1.5) ){ 
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
                for(int tt = 0; tt < 5; tt++){
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
                if(founcount > 4){
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
   gl_FragColor = ergcolor;


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

    # Create Texture

    glBindTexture(GL_TEXTURE_2D, glGenTextures(1)) # 2 d texture (x y sized)

    glPixelStorei(GL_UNPACK_ALIGNMENT,1)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, w, h, 0, GL_RGB, GL_UNSIGNED_BYTE, colloc)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)


# A general OpenGL initialization function.  Sets all of the initial parameters.
def InitGL():                # We call this right after our OpenGL window is created.
    print("OpenGL Version: ", glGetString ( GL_VERSION ))
    print("Shading Language Version: ", glGetString( GL_SHADING_LANGUAGE_VERSION ))
    glmaxtexsize = glGetIntegerv(GL_MAX_TEXTURE_SIZE)
    print("Sys max texture size: ", glmaxtexsize, "x", glmaxtexsize, " (",glmaxtexsize*glmaxtexsize,") " , " needed size: ", w, "x", h, " (", w*h, ")")

    LoadTextures()
    glEnable(GL_BLEND);

    glEnable(GL_TEXTURE_2D) #2d texture
    glClearColor(0.0, 0.0, 0.0, 0.0)    # This Will Clear The Background Color To Black
    
    glMatrixMode(GL_PROJECTION);
    
    glLoadIdentity();
    glOrtho(0.0, float(w), 0.0, float(h), 0.0, 1.0);
    glMatrixMode(GL_MODELVIEW);
    global PRO1
    PRO1 = init_shader_program()
    glUseProgram( PRO1 )

    
# The function called when our window is resized (which shouldn't happen if you enable fullscreen, below)
def ReSizeGLScene( nw, nh ):
    if( nh == 0):                   # Prevent A Divide By Zero If The Window Is Too Small
        nh = 1

    glViewport(0, 0, nw, nh)        # Reset The Current Viewport And Perspective Transformation
    #...

# The main drawing function.
def DrawGLScene():

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)    # Clear The Screen And The Depth Buffer
    glLoadIdentity()                    # Reset The View

    glClearColor(0.0,0.0,0.0,0.0)

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
    
    glBegin(GL_QUADS)                # Start Drawing The Cube

    #blanc quad
    glVertex3i(0, 0, 0);
    glVertex3i(w, 0, 0);
    glVertex3i(w, h, 0);
    glVertex3i(0, h, 0);
    glEnd();
    
    glutSwapBuffers()

    backdata = ( GLubyte * (3*w*h) )(0)
    glReadPixels(0, 0, w, h, GL_RGB, GL_UNSIGNED_BYTE, backdata)
  
    noshit = 0
    fI1 = []
    global results
    currfragekey = " ".join(str(wn) for wn in currfrage)
    #indexfrage indexfund und abstand fund muß geschrieben werden in einem Thread
    for b in range(0, len(backdata)/3):
        if( backdata[b*3] != 0 or backdata[(b*3)+2] != 0):
            noshit += 1
            results.append( str(frageindex)+","+ str(b)+","+str(backdata[b*3])+","+str(backdata[(b*3)+1])+","+ str(currfragekey)+","+str(backdata[(b*3)+2]))

    if(len(results) > 1000):
        #print(results[0:10])
        ofh = open( "gefunden/"+str(outerTEXindex)+"/"+str(frageindex)+".txt", "a" )#append if exits
        ofh.write( ";".join( results ) )
        ofh.close( )
        #cPickle.dump( results, open( "gefunden/"+str(frageindex)+".txt", "wb" ) )#append!!!
        results = []
    
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

    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)

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
