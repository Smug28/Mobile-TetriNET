# -*- coding: utf-8 -*-
"""
Created on Sat Oct 20 20:28:58 2012

Mobile TetriNET - TetriNET Client for Android
Copyright (C) 2012-2013  Jiří 'Smuggler' Vaculík

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from random import randint, choice
from copy import deepcopy
from kivy.properties import ListProperty
from kivy.properties import ObjectProperty
from kivy.core.image import Image
from kivy.animation import Animation
from kivy.gesture import Gesture, GestureDatabase
from kivy.graphics import Line

# Definice herních bloků
PIECES = {
1:[[[5,0],[5,1],[5,2],[5,3]], [[3,0],[4,0],[5,0],[6,0]]],
2:[[[5,0],[6,0],[5,1],[6,1]]],
3:[[[4,0],[4,1],[5,1],[6,1]], [[5,0],[5,1],[4,2],[5,2]], [[4,0],[5,0],[6,0],[6,1]], [[4,0],[5,0],[4,1],[4,2]]],
4:[[[4,0],[5,0],[6,0],[4,1]], [[4,0],[4,1],[4,2],[5,2]], [[6,0],[4,1],[5,1],[6,1]], [[4,0],[5,0],[5,1],[5,2]]],
5:[[[5,0],[6,0],[4,1],[5,1]], [[4,0],[4,1],[5,1],[5,2]]],
6:[[[4,0],[5,0],[5,1],[6,1]], [[6,0],[5,1],[6,1],[5,2]]],
7:[[[5,0],[4,1],[5,1],[6,1]], [[5,0],[4,1],[5,1],[5,2]], [[4,0],[5,0],[6,0],[5,1]], [[4,0],[4,1],[5,1],[4,2]]]
}

# Definice barev pro každý blok
COLORS = {
1:[0,.6,.8,1],
2:[1,.7333333,.2,1],
3:[.6,.8,0,1],
4:[.666666667,.4,.8,1],
5:[0,.6,.8,1],
6:[1,.266666667,.266666667,1],
7:[1,.7333333,.2,1]
}

# Značení speciálních kostek
SPECIALS = ("a", "c", "n", "r", "s", "b", "g", "q", "o")

# Třída reprezentující jednu kostku v herním poli
class Box(Widget):
    colored = ListProperty([.1372,.1372,.1372,1])
    texture = ObjectProperty(False)
    def __init__(self, **kwargs):   # inicializace
        super(Box, self).__init__(**kwargs)
        self.coords = (0, 0)
        self.active = False
        self.sb = False
        
    def special(self, sType, small=False):
        # Z obyčejné kostky vytváří speciální
        if sType in SPECIALS:
            if small == False:
                img = Image('crop/icons/{0}.png'.format(sType))
            else:
                img = Image('crop/icons/{0}_s.png'.format(sType))
            self.texture = img.texture
            self.sb = sType

# Třída herního pole
class GameMatrix(GridLayout):
    def __init__(self, app, **kwargs):  # inicializace pole
        self.app = app
        super(GameMatrix, self).__init__(**kwargs)
        self.coords = []
        self.dpos = (0,0)
        self.colors = []
        self.shape = None
        self.active_color = [.1372,.1372,.1372,1]
        self.inactive_color = [.1372,.1372,.1372,1]
        self.fUpdate = 12*22*"0"
        self.tnetCoords2 = []
        for y in range(51,73):
            for x in range(51,63):
                self.tnetCoords2.append(chr(x)+chr(y))
        self.tnetCoords = []
        for x in range(51,63):
            col = []
            for y in range(51,73):
                col.append((chr(x), chr(y)))
            self.tnetCoords.append(col)
        self.tnetColors = []
        for c in range(33, 48):
            self.tnetColors.append(chr(c))
        self.move = False
        self.orientation = 0
        self.colored = set()
        self.colors = [deepcopy(self.inactive_color), [0,.6,.8,1], [1,.7333333,.2,1], [.6,.8,0,1], [.666666667,.4,.8,1], [1,.266666667,.266666667,1]]
        self.COORDS_SET = set()
        for y in range(int(self.rows)):
            line = []
            for x in range(int(self.cols)):
                box = Box()
                box.coords = (x, y)
                box.colored = deepcopy(self.inactive_color)
                self.add_widget(box)
                line.append(box)
                self.COORDS_SET.add((x, y))
            self.coords.append(line)
        self.b = 0
        self.startgame = False
        self.seed = randint(0,0xFFFFFF)
        self.specials = set()
        self.buildNext = False
        self.mLR = False
        self.gdb = GestureDatabase()
        self.GSTR_DROP = \
        self.gdb.str_to_gesture('eNq1l82O2jAQgO9+Ebg08ng8M/YL0GslHqBKIQK0W4iSbHf37WtPIjZS/6Si4WIYez4P+Yyxt5eny4/35tSN08vQuc9L23u3Pfbg9ptr+73buD6Ut6VBN+434zTcnrqxfIxu+9yT2/4WstdhrueKkpLf3y7Xqaalmpb/kPaljnI9zBXUEt5LCgS3803EKCmwT5yJCXKt5q32Yu31HsETZe85AIAQsBu/tX+fJuo05E7zDEEEBDOg17k8ufH0AF2/O4gRPSk929CDCghgRA9KRyO6Wg13qx7viyaUaRLyY3jVGsQKr15DNsKjikWwwqtZRCu8qkUrtahq0Uotqlpc1H7yDaT1jhbKY3sEH1VtBCu8qo1ohVe1kazwqjaKFV7VRiu1pGrJSi2pWvpQG0Ne/9k+SFezREZ0FUtiRFevlG3orFoZjOhqlY2sslplI6usVtnIKqtV/rC6bPDLCSTBQi89HhIjUvQogcWXn+C/4KJSBWzg6lTQBq5Khf4XXm8Hh6HrrvezvnA97Iu47Q4FG+92UUJppl6Sa38N5nUwogaTXwUxpzkI6yAtwbAOQmnWL64jUEdwriNCWtKia+fqz93ldJ7qHYXcrmyxpbtEXy/H6VyDXIqaQ9PtuRva66FejpLUZQg1vDzWr/1wO74cFJRKJQ2Vs4OUK0sMwEF0gTY/AXq8jUg=')
        self.gdb.add_gesture(self.GSTR_DROP)
        self.dropAnimation2 = Animation(colored=self.inactive_color, d=.03)
        self.dropAnimation = Animation(colored=self.inactive_color, d=.1)
        self.spectate = False
    
    def simplegesture(self, name, point_list):
        # Pomocná funkce pro rozpoznávání gest
        g = Gesture()
        g.add_stroke(point_list)
        g.normalize()
        g.name = name
        return g
    
    def generate(self):
        # Algoritmus pseudonáhodného generování herních bloků
        a = 0x08088405
        c = 1
        M = 2**32
        self.seed = (a*self.seed + c) % M
        block = int(self.seed*100./M)
        self.seed = (a*self.seed + c) % M
        orientation = int(self.seed*4./M)
        return (block,orientation)
    
    def build(self, dt):
        # Pomocná funkce pro automatické volání
        self._build()
    
    def _build(self):
        # Přidá do pole nový herní blok
        if self.startgame == False:
            self.stack = [self.generate() for y in range(5)]
        st = self.stack.pop(0)
        piece = int(self.app.serverConf.blockFreq[st[0]])
        nextPC = int(self.app.serverConf.blockFreq[self.stack[0][0]])
        self.app.nextPiece.showNext(nextPC)
        orientation = st[1]
        if piece in (1,5,6):
            if orientation % 2 == 0:
                self.orientation = 0
            else:
                self.orientation = 1
        elif piece == 2:
            self.orientation = 0
        self.shape = deepcopy(PIECES[piece])
        self.active_color = deepcopy(COLORS[piece])
        self.stack.append(self.generate())
        full = False
        for box in self.shape[self.orientation]:
            if tuple(box) in self.colored:
                full = True
                break
        if full == False:
            for box in self.shape[self.orientation]:
                self.drop(box)
            for box in self.shape[self.orientation]:
                self.mark(box)
            if self.app.tetrifast:
                self._fall()
            Clock.schedule_interval(self.fall, (1005 - (self.app.lvl * 10))/1000.)
            self.app.send_message("f "+str(self.app.id)+" "+self.fUpdate)
            self.startgame = True
        else:
            self.startgame = False
            self.spectate = True
            self.app.send_message("playerlost {0}".format(self.app.id))
            for i in range(22):
                self.addLine()
        self.buildNext = False
        self.blockRotation = False
            
    def get(self, x, y):
        # Vrátí objekt Box - 1 kostku z pole
        return self.coords[y][x]
    
    def getMinMax(self, shape):
        # Vrací minimální a maximální souřadnice bloku
        x = []
        y = []
        for box in shape:
            x.append(box[0])
            y.append(box[1])
        return {'x':(min(x), max(x)), 'y':(min(y), max(y))}
    
    def drop(self, coords, anim=0):
        # Přebarví kostku na šedou (barva pole)
        box = self.get(coords[0], coords[1])
        box.colored = deepcopy(self.inactive_color)
        box.active = False
        box.texture = False
        box.sb = False
    
    def mark(self, coords, random=False, anim=0):
        # Přebarví kostku na barevnou
        box = self.get(coords[0], coords[1])
        box.colored = self.active_color if random == False else choice(deepcopy(COLORS))
        box.active = True
    
    def fall(self, dt):
        # Pomocná funkce pro automatické volání
        print self.colored
        self._fall()
    
    def _fall(self, animate=1):
        # Slouží ke spadení bloku o jedno dolů (každou cca 1 s)
        if (self.buildNext == False) and self.startgame and (self.app.paused == False):
            anim = []
            unschedule = False
            next_pos = deepcopy(self.shape[self.orientation])
            for box in next_pos:
                box[1] += 1
            if self.shape[self.orientation][-1][1] >= 21:
                unschedule = True
                print "< fall unschedule >"
            elif len(self.colored.intersection(set(tuple(y) for y in next_pos))) != 0:
                unschedule = True
            else:
                for box in self.shape[self.orientation]:
                    self.drop(box, anim=animate)
                for i in self.shape:
                    for box in i:
                        box[1] += 1
                for box in self.shape[self.orientation]:
                    self.mark(box, anim=animate)
                unschedule = False
            if unschedule == True:
                self.blockRotation = True
                print "Current: "+str(self.shape[self.orientation])
                print "Next: "+str(next_pos)
                Clock.unschedule(self.fall)
                for i in self.shape[self.orientation]:
                    try:
                        g = self.get(i[0], i[1])
                        if g.colored != [.1372,.1372,.1372,1]:
                            anim.append(g)
                            self.colored.add(tuple(i))
                    except:
                        pass
                self.orientation = 0
                self.tetris(anim)
                del(anim)
                self.buildNext = True
                if self.app.tetrifast == False:
                    Clock.schedule_once(self.build, 1)
                else:
                    self._build()
                unschedule = False
    
    def on_touch_down(self, touch):
        # Uživatel se dotkl pole
        if self.collide_point(touch.x, touch.y) and self.startgame and (self.app.paused == False):
            touch.grab(self)
            touch.ud["line"] = Line(points=(touch.x, touch.y))

    def on_touch_move(self, touch):
        # Uživatel pohybuje s prstem po poli
        if (touch.grab_current is self) and self.startgame and (self.app.paused == False) and (self.blockRotation == False):
            touch.ud["line"].points += [touch.x, touch.y]
            self.box_size = self.get(0,0).size[0]
            self.dpos = (touch.dpos[0]+self.dpos[0], touch.dpos[1]+self.dpos[1])
            if abs(self.dpos[0]) >= self.box_size:
                next_pos = deepcopy(self.shape[self.orientation])
                for box in next_pos:
                    box[0] += int(round((0.5*self.dpos[0])/self.box_size,0))
                minmax = self.getMinMax(next_pos)
                if minmax['x'][0] < 0 or minmax['x'][1] > 11:
                    pass
                elif len(self.colored.intersection(set(tuple(y) for y in next_pos))) != 0:
                    pass
                else:
                    for box in self.shape[self.orientation]:
                        self.drop(box, anim=1)
                    for i in self.shape:
                        for box in i:
                            box[0] += int(round((0.5*self.dpos[0])/self.box_size,0))
                    for box in self.shape[self.orientation]:
                        self.mark(box, anim=1)
                    self.move = True
                    self.mLR = True
                self.dpos = (0, self.dpos[1])
            if -1*(self.dpos[1]) >= 1.05*self.box_size:
                for i in range(abs(int(round(self.dpos[1]/self.box_size,0)*1))):
                    self._fall()
                self.move = True
                self.dpos = (self.dpos[0], 0)
    
    def on_touch_up(self, touch):
        # Uživatel zvedl prst z obrazovky
        if touch.grab_current is self:
            g = self.simplegesture('', zip(touch.ud['line'].points[::2], touch.ud['line'].points[1::2]))
            g2 = self.gdb.find(g, minscore=0.80)
            if g2 and (self.mLR == False) and (self.blockRotation == False):
                if g2[1] == self.GSTR_DROP:
                    print "< GESTURE: Drop >"
                    for i in range(21-self.shape[self.orientation][-1][1]):
                        self._fall(animate=2)
                    self.mLR = False
            else:
                if (self.mLR == False) and (self.move == False) and (self.blockRotation == False):
                    if touch.x <= self.parent.size[0]/2.:
                        self.rotate(False)   #left
                    else:
                        self.rotate(True)  #right
                self.mLR = False
            if self.move == True:
                self.move = False
            touch.ungrab(self)
            
    def dropAnim(self, fall):
        # Animace padání bloku
        if fall:
            d = .1
        else:
            d= .2
        boxes = []
        for box in self.shape[self.orientation]:
            if ((box[0] >= 0) and (box[0] <= 11)) and ((box[1] >= 0) and (box[1] <= 21)):
                cur = self.get(box[0], box[1])
                a = Box()
                a.size = cur.size
                a.pos = cur.pos
                a.colored = cur.colored
                a.size_hint = (None, None)
                boxes.append(a)
                self.app.sOverlay.add_widget(a)
        if len(boxes) != 0:
            anims = [Animation(y=p.y-p.size[1], opacity=0., t='linear', d=d) for p in boxes]
            for i in range(len(boxes)):
                anims[i].start(boxes[i])
            Clock.schedule_once(self.clearAnimation, d)
    
    def fellAnim(self, widgets):
        # Animace po spadení bloku (změna barvy)
        color1 = widgets[0].colored
        color2 = [y+.3 for i, y in enumerate(color1) if i < 3] + [color1[-1],]
        anim = Animation(colored=color2, duration=.2) + Animation(colored=color1, duration=.2)
        for i in widgets:
            anim.start(i)
    
    def clearAnimation(self, dt):
        # Odstraní widgety vytvořené animací
        self.app.sOverlay.clear_widgets()
        print "< widgets cleared >"
    
    def rotate(self, direction):
        # Otáčení s blokem
        maximum = len(self.shape)
        now = deepcopy(self.orientation)
        if direction:   #left
            self.orientation -= 1
            if self.orientation < 0:
                self.orientation = maximum-1
        else:           #right
            self.orientation += 1
            if self.orientation > maximum-1:
                self.orientation = 0
        if now != self.orientation:
            for box in self.shape[now]:
                self.drop(box)
            coords = self.getMinMax(self.shape[self.orientation])
            if coords['y'][1] > 21:
                print "posunout nahoru o {0}".format(coords['y'][1] - 21)
            if coords['x'][0] < 0:
                print "posunout doprava o {0}".format(abs(coords['x'][0]))
                for s in self.shape:
                    for box in s:
                        box[0] += abs(coords['x'][0])
            if coords['x'][1] > 11:
                print "posunout doleva o {0}".format(coords['x'][1] - 11)
                for s in self.shape:
                    for box in s:
                        box[0] -= coords['x'][1] - 11
            if len(self.colored.intersection(set(tuple(y) for y in self.shape[self.orientation]))) != 0:
                self.orientation = now
            for box in self.shape[self.orientation]:
                self.mark(box)
        print self.orientation
    
    def tetris(self, anim):
        # Rozhoduje o tom, zda byl vyplněn řádek (voláno po spadení bloku)
        full = []
        for i in self.colored:
            full.append(i[1])
        lines = []
        for i in range(22):
            if full.count(i) == 12:
                lines.append(i)
        if len(lines) != 0:
            if self.app.onAndroid():
                self.app.vibrate(0.05)
            self.app.linesCleared += len(lines)
            if self.app.linesCleared % int(self.app.serverConf.linesLvl) == 0:
                self.app.lvl += int(self.app.serverConf.lvlInc)
            print "Lines cleared: "+str(self.app.linesCleared)
            print "Level: "+str(self.app.lvl)
            for i in range(len(lines)):
                for j in range(12):
                    self.colored.remove((j, lines[i]))
                    self.specials.discard((j, lines[i]))
                    box = self.get(j, lines[i]).sb
                    if box != False:
                        self.app.dock.addSpecial(box)
                    self.drop((j, lines[i]))
            lns = deepcopy(lines)
            lns.sort()
            print lns
            for num, ln in enumerate(lns):
                colored = list(self.colored)
                colored.sort(cmp=lambda x,y: cmp(x[1],y[1]))
                colored.reverse()
                for coord in colored:
                    if coord[1] < ln:
                        new = (coord[0], coord[1]+1)
                        box = self.get(coord[0], coord[1])
                        newColor = box.colored
                        sType = box.sb
                        self.drop(coord)
                        self.colored.discard(coord)
                        if sType != False:
                            self.specials.discard(coord)
                        box = self.get(new[0], new[1])
                        box.colored = newColor
                        self.colored.add(new)
                        if sType != False:
                            box.special(sType)
                            self.specials.add(new)
            if self.app.serverConf[-2] == '1':
                if len(lines) >= 2 and len(lines) <= 3:
                    self.app.send_message("sb 0 cs{0} {1}".format(len(lines)-1, self.app.id))
                    print "add id:"+str(self.app.id)
                elif len(lines) == 4:
                    print "Tetris!"
                    if self.app.serverConf[-2] == '1':
                        self.app.send_message("sb 0 cs{0} {1}".format(4, self.app.id))
                    print "add id:"+str(self.app.id)
            else:
                print "< tetris() >"
            if self.app.linesCleared % int(self.app.serverConf.linesSpecial) == 0:
                self.addSpecial()
        else:
            self.fellAnim(anim)
        self.fieldUpdate()
        
    def addSpecial(self):
        # Přidá novou speciální kostku do pole
        if len(self.colored) - len(self.specials) > 0:
            special = choice(list(self.colored.difference(self.specials)))
            self.specials.add(special)
            self.drop(special)
            box = self.get(special[0], special[1])
            sType = SPECIALS[int(self.app.serverConf.specialFreq[randint(0,99)])-1]
            box.special(sType)
            print sType
            print special
        else:
            for i in range(20):
                col = randint(0,11)
                empty = True
                for c in self.colored:
                    if c[0] == col:
                        empty = False
                        break
                if empty == True:
                    self.colored.add((col, 21))
                    self.specials.add((col, 21))
                    self.drop((col, 21))
                    box = self.get(col, 21)
                    sType = SPECIALS[int(self.app.serverConf.specialFreq[randint(0,99)])-1]
                    box.special(sType)
                    print sType
                    print (col, 21)
                    print "< Add special >"
                    break
    
    def addLine(self, update=True):
        # Přidání náhodného řádku do pole (speciální kostkou)
        garbage = [randint(0,7) for i in range(12)]
        garbage[randint(0,11)] = 0
        move = list(self.colored)
        move.sort(cmp=lambda x,y: cmp(x[1],y[1]))
        for coord in move:
            if coord[1] <= 21 and coord[1] >=1:
                new = (coord[0], coord[1]-1)
                box = self.get(coord[0], coord[1])
                newColor = box.colored
                sType = box.sb
                self.drop(coord)
                self.colored.remove(coord)
                if sType != False:
                    self.specials.discard(coord)
                box = self.get(new[0], new[1])
                box.colored = newColor
                self.colored.add(new)
                if sType != False:
                    box.special(sType)
                    self.specials.add(new)
        for i, cell in enumerate(garbage):
            box = self.get(i, 21)
            box.texture = False
            if cell > 0:
                box.colored = COLORS[cell]
                self.colored.add((i, 21))
            else:
                box.colored = self.inactive_color
                self.colored.discard((i, 21))
        if update:
            self.fieldUpdate()
        for i, b in enumerate(self.shape):
            drop = False
            if i == self.orientation:
                drop = True
            for box in self.shape[i]:
                box = [box[0], box[1]+1]
            if drop:
                for box in self.shape[i]:
                    self.drop(box)
                for box in self.shape[i]:
                    self.mark(box)

    def fieldUpdate(self, *args):
        # Vytvoření řetězce pro aktualizaci pole a odeslání aktualizace
        fupdate = ""
        for y in range(22):
            for x in range(12):
                s = set()
                s.add((x,y))
                if self.colored.issuperset(s):
                    box = self.get(x, y)
                    if box.sb == False:
                        fupdate += str(self.colors.index(box.colored))
                    else:
                        fupdate += box.sb
                else:
                    fupdate += '0'
        print fupdate
        d = []
        prev = False
        for i in range(len(self.fUpdate)):
            if self.fUpdate[i] != fupdate[i]:
                try:
                    color = int(fupdate[i])
                except:
                    color = self.tnetColors.index(chr(39)) + SPECIALS.index(fupdate[i])
                if prev == False:
                    d.append(self.tnetColors[color])
                    prev = fupdate[i]
                else:
                    if prev != fupdate[i]:
                        d.append(self.tnetColors[color])
                        prev = fupdate[i]
                d.append(self.tnetCoords2[i])
        self.fUpdate = fupdate
        dstr = "f "+str(self.app.id)+" "
        for i in d:
            dstr+=i
        self.app.send_message(dstr)
        self.app.print_message(dstr+"\xff")
    
    def clearLine(self):
        # Odstraní řádek od konce (speciální kostkou)
        for j in range(12):
            self.colored.discard((j, 21))
            self.specials.discard((j, 21))
            self.drop((j, 21))
        colored = list(self.colored)
        colored.sort(cmp=lambda x,y: cmp(x[1],y[1]))
        colored.reverse()
        print colored
        for coord in colored:
            if coord[1] < 21:
                new = (coord[0], coord[1]+1)
                box = self.get(coord[0], coord[1])
                newColor = box.colored
                sType = box.sb
                self.drop(coord)
                self.colored.remove(coord)
                if sType != False:
                    self.specials.discard(coord)
                box = self.get(new[0], new[1])
                box.colored = newColor
                self.colored.add(new)
                if sType != False:
                    box.special(sType)
                    self.specials.add(new)
        self.fieldUpdate()

    def nuke(self):
        # Vyprázdnění pole (speciální kostkou)
        for box in self.colored:
            self.drop(box)
        self.colored = set()
        self.specials = set()
        self.fieldUpdate()
    
    def randomClear(self):
        # Náhodné odstranění několika kostek (speciální kostkou)
        cells = []
        for i in range(10):
            cells.append((randint(0,11), randint(0,21)))
        for coord in cells:
            self.colored.discard(coord)
            self.specials.discard(coord)
            self.drop(coord)
        self.fieldUpdate()
    
    def clearSpecials(self):
        # Odstraní všechny speciální kostky (speciální kostkou)
        coords = list(self.specials)
        for coord in coords:
            self.specials.discard(coord)
            self.drop(coord)
            self.mark(coord, True)
        self.fieldUpdate()
    
    def quake(self):
        # Náhodně posune řádky o 3 doleva/doprava (speciální kostkou)
        colored = list(self.colored)
        colored.sort(cmp=lambda x,y: cmp(x[1],y[1]))
        cells = [[y[0], y[1]] for y in colored]
        prev = None
        rnd = 0
        for cell in cells:
            if prev != cell[1]:
                prev = cell[1]
                rnd = choice(range(-3,4))
            cell[0] += rnd
            if cell[0] > 11:
                cell[0] -= 11
            elif cell[0] < 0:
                cell[0] = 12+cell[0]
        print cells
        for i in range(len(colored)):
            new = (cells[i][0], cells[i][1])
            box = self.get(colored[i][0], colored[i][1])
            newColor = box.colored
            sType = box.sb
            self.drop(colored[i])
            self.colored.discard(colored[i])
            if sType != False:
                self.specials.discard(colored[i])
            box = self.get(new[0], new[1])
            box.colored = newColor
            self.colored.add(new)
            if sType != False:
                box.special(sType)
                self.specials.add(new)
        self.fieldUpdate()
    
    def switchField(self, pid):
        # Vymění si pole s protivníkem (speciální kostkou)
        for y in range(22):
            for x in range(12):
                sender = self.app.overlay.children[0].children[pid].matrix.coords[y][x]
                if type(sender) == type(None):
                    self.drop((x, y))
                    self.colored.discard((x, y))
                    self.specials.discard((x, y))
                else:
                    newColor = sender.colored
                    newStype = sender.sb
                    box = self.get(x, y)
                    box.colored = newColor
                    self.colored.add((x, y))
                    if sender.sb != False:
                        box.special(newStype)
                        self.specials.add((x, y))
        self.fieldUpdate()
    
    def gravity(self):
        # Spadení kostek, vyplnění mezer (speciální kostkou)
        colored = list(self.colored)
        colored.sort(cmp=lambda x,y: cmp(x[1],y[1]))
        colored.reverse()
        color = [colored, ]
        i = 0
        while True:
            color.append([])
            for b in color[i]:
                if b[1] < 21:
                    if (b[0], b[1]+1) not in color[i]:
                        color[i+1].append((b[0], b[1]+1))
                    else:
                        color[i+1].append(b)
                else:
                    color[i+1].append(b)
            if color[i] == color[i-1]:
                break
            i += 1
        color = color[-1]
        for j, b in enumerate(colored):
            if b != color[j]:
                old = self.get(b[0], b[1])
                new = self.get(color[j][0], color[j][1])
                new.colored = old.colored
                new.sb = old.sb
                new.texture = old.texture
                self.drop(b)
                self.colored.remove(b)
                self.colored.add(color[j])
                if new.sb != False:
                    self.specials.remove(b)
                    self.specials.add(color[j])
        self.fieldUpdate()
    
    def blockBomb(self):
        # Odstranění kostek blockbomb a vystřelení okolních do pole
        # (speciální kostkou)
        bombs = []
        colored_remove = []
        s = range(-1,2)
        s.reverse()
        for bomb in self.specials:
            box = self.get(bomb[0], bomb[1])
            if box.sb == 'o':
                bombs.append(bomb)
        for bomb in bombs:
            self.specials.remove(bomb)
            for i in range(-1,2):
                for j in s:
                    b = (bomb[0]+i, bomb[1]+j)
                    if b in self.colored:
                        colored_remove.append(b)
                        new = choice(list(self.COORDS_SET.difference(self.colored.union(set([tuple(a) for a in self.shape[self.orientation]])))))
                        self.colored.add(new)
                        new = self.get(new[0], new[1])
                        old = self.get(b[0], b[1])
                        new.colored = old.colored
        for bomb in bombs+colored_remove:
            self.colored.discard(bomb)
            self.drop(bomb)
        self.fieldUpdate()