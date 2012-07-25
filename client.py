# Basic OBJ file viewer. needs objloader from:
#  http://www.pygame.org/wiki/OBJFileLoader
# LMB + move: rotate
# RMB + move: pan
# Scroll wheel: zoom in/out
import sys, pygame
from pygame.locals import *
from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GLU import *

# IMPORT OBJECT LOADER
from objloader import *

import select, socket

port = 6005  # where do you expect to get a msg?
bufferSize = 1024 # whatever you need

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind(('10.10.1.255', port))
s.setblocking(0)

pygame.init()
viewport = (800,600)
hx = viewport[0]/2
hy = viewport[1]/2
srf = pygame.display.set_mode(viewport, OPENGL | DOUBLEBUF)

glLightfv(GL_LIGHT0, GL_POSITION,  (600, 600, 600, 0.0))
glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.8, 1.0))
glEnable(GL_LIGHT0)
glEnable(GL_LIGHTING)
glEnable(GL_COLOR_MATERIAL)
glEnable(GL_DEPTH_TEST)
glShadeModel(GL_SMOOTH)           # most obj files expect to be smooth-shaded

# LOAD OBJECT AFTER PYGAME INIT
obj = OBJ(sys.argv[1], swapyz=False)

clock = pygame.time.Clock()

glMatrixMode(GL_PROJECTION)
glLoadIdentity()
width, height = viewport
gluPerspective(90.0, width/float(height), 1, 100.0)
glEnable(GL_DEPTH_TEST)
glMatrixMode(GL_MODELVIEW)


rx, ry = (0,0)
tx, ty = (0,0)
zpos = 7
rotate = move = False
while 1:
    clock.tick(30)
    for e in pygame.event.get():
        if e.type == QUIT:
            sys.exit()
        elif e.type == KEYDOWN and e.key == K_ESCAPE:
            sys.exit()
#        elif e.type == MOUSEBUTTONDOWN:
#            if e.button == 4: zpos = max(1, zpos-1)
#            elif e.button == 5: zpos += 1
#            elif e.button == 1: rotate = True
#            elif e.button == 3: move = True
#        elif e.type == MOUSEBUTTONUP:
#            if e.button == 1: rotate = False
#            elif e.button == 3: move = False
#        elif e.type == MOUSEMOTION:
#            i, j = e.rel
#            if rotate:
#                rx += i
#                ry += j
#            if move:
#                tx += i
#                ty -= j
    result = select.select([s],[],[])
    if s in result[0]:
        msg = result[0][0].recv(bufferSize)[:-1]
        coords = msg.split(',')
        rx, ry, tx, ty = [int(i) for i in coords]
        print msg


    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # RENDER OBJECT
    glTranslate(tx/20., ty/20., - zpos)
    glRotate(ry, 1, 0, 0)
    glRotate(rx, 0, 1, 0)
    glCallList(obj.gl_list)

    pygame.display.flip()
