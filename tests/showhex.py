import pygame
from pygame.locals import *
from math import sin, cos, radians, ceil
"""Mostly from http://www.gamedev.net/reference/articles/article1800.asp"""

def roof(num):
    #return num
    return int(ceil(num))
'''
def F(n):
    return ((1+sqrt(5))**n-(1-sqrt(5))**n)/(2**n*sqrt(5))
'''
def make_nshex(side):
    """Given the length of a hexagon side, return the pointslist and
       bounding rectangle of hexagon"""
    s = side
    hexh = roof(sin(radians(30))*s)
    r    = roof(cos(radians(30))*s)
    rech = s + (2*hexh)
    recw = 2*r
    size = [roof(recw), roof(rech)]
    pl = [(0, hexh), (.5*recw,0), (recw,hexh), (recw, rech-hexh), (.5*recw, rech), (0, rech - hexh)]
    pl2 = [(1, 1+hexh), (.5*recw,2), (recw-2,hexh+1), (recw-2, rech-hexh-1), (.5*recw, rech-2), (2, rech - hexh-1)]
    return (pl, pl2, size)
    
def make_ewhex(side):
    """Given the length of a hexagon side, return the pointslist and
       bounding rectangle of hexagon"""
    s = side
    hexh = roof(sin(radians(30))*s)
    r    = roof(cos(radians(30))*s)
    rech = s + (2*hexh)
    recw = 2*r
    size = [roof(rech), roof(recw)]
    pl = [(0,.5*recw), (hexh, 0), (rech - hexh, 0), (rech, .5*recw), (rech-hexh, recw), (hexh, recw)]
    pl2 = [(2, .5*recw), (hexh+1, 2), (rech - hexh, 2), (rech - 2 , .5*recw), (rech-hexh-1 , recw- 2), (hexh + 1 , recw -2)]
    return (pl, pl2, size)

def draw_nshex(side):
    """returns a rect a tile of size containing a hexagon made with side"""
    pl, pl2, size = make_nshex(side)
    
    s = side
    hexh = roof(sin(radians(30))*s)
    r    = roof(cos(radians(30))*s)
    rech = s + (2*hexh)
    recw = 2*r
    rowh = rech - hexh
        
    hexa = pygame.Surface(size)
    hexa.fill([0,0,0])
    hexa.set_colorkey([0,0,0])
    pygame.draw.polygon(hexa, [255,0,0], pl,)
    pygame.draw.polygon(hexa, [120,120,120], pl2,)

    for x in range(4):
        for y in range(4):
            if y&1:
                screen.blit(hexa,(.5*size[0]+size[0]*x,rowh*y))
            else:
                screen.blit(hexa,(size[0]*x,rowh*y))
    
    rec = pygame.Surface(size)
    rec.fill([0,0,0])
    rec.set_colorkey([0,0,0])
    pygame.draw.rect(rec, [0,255,255], (0, 0, recw, hexh + s), 1)
    for x in range(5):
        for y in range(5):
            screen.blit(rec, (recw*x, y*(hexh + s)))
    '''wrong.
    for x in range(16):
        for y in range(16):
            if y&1:
                screen.blit(hexa,(recw*x+.5*size[0], y*(hexh +s)))
            else:
                screen.blit(hexa,(recw*x, y*(hexh +s)))
    '''
    pygame.display.update()

def draw_ewhex(side):
    """returns a rect a tile of size containing a hexagon made with side"""
    pl, pl2, size = make_ewhex(side)
    image = pygame.Surface(size)
    #image.fill([0, 255, 0])
    pygame.draw.polygon(image, [255,0,0], pl,)
    pygame.draw.polygon(image, [120,120,120], pl2,)
    #ugly:
    #pygame.draw.polygon(image, [120,120,120], [(x[0]+1, x[1]+1) for x in make_nshex(side-2)[0]])
    screen.blit(image, (0,0))
    pygame.display.update()    

def clear():
    screen.fill([0,0,0])
    image.fill([0,255,0])
    screen.blit(image, image.get_rect())
    pygame.display.update()

pygame.init()
s = 48
hexh = roof(sin(radians(30))*s)
r    = roof(cos(radians(30))*s)
rech = s + (2*hexh)
recw = 2*r
rowh = rech - hexh
screen = pygame.display.set_mode([r+(recw*5), hexh+(rowh*5)])
draw_nshex(s)
while pygame.event.poll().type != KEYDOWN:
    for event in pygame.event.get():
        if event.type == MOUSEMOTION:
            pixelx, pixely = event.pos
            
            recx = pixelx / recw
            recy = pixely / (hexh + s)
            
            sectpixelx = (pixelx - recx) % recw 
            sectpixely = (pixely - recy) % (hexh +s)
            m = hexh / float(r)
            if (recy & 1) == 0:
                #section: A
                print 'a'
                if sectpixely < (hexh - sectpixelx * m):
                    print "left edge?"
                    hexx = recx - 1
                    hexy = recy - 1
                elif sectpixely < (- hexh + sectpixelx * m):
                    print "right edge?"
                    hexx = recx 
                    hexy = recy - 1
                else:
                    print "in the middle?"
                    hexx = recx
                    hexy = recy

            else:
                #section: B
                print 'b'
                if sectpixelx >= r:
                    print "right side"
                    if sectpixely < (2* hexh - sectpixelx * m):
                        print "top?"
                        hexx = recx
                        hexy = recy - 1
                    else:
                        hexx = recx
                        hexy = recy
                else:
                    print "left side"
                    if sectpixely < (sectpixelx * m):
                        print "top?"
                        hexx = recx
                        hexy = recy - 1
                    else:
                        hexx = recx - 1
                        hexy = recy
            print "hex: (%s, %s)" %(hexx,hexy)
            print "rec: (%s, %s)" %(recx,recy)
            

    #pygame.time.delay(10)
