# -*- coding: utf-8 -*-
"""
Created on Tue Jan  1 23:49:04 2013

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
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.image import Image
from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.uix.scrollview import ScrollView
from box import Box
from kivy.properties import ObjectProperty
from kivy.animation import Animation
from kivy.gesture import Gesture, GestureDatabase
from kivy.graphics import Line
from kivy.uix.modalview import ModalView
from kivy.clock import Clock
from kivy.uix.relativelayout import RelativeLayout

class DelButton(Button):
    # Tlačítko křížku u oblíbeného serveru
    OBJ = ObjectProperty()
    ID = NumericProperty()
    pass

class Bookmark(BoxLayout):
    # Řádek s oblíbeným serverem v záložkách
    pass

# Widget dalšího herního bloku (vpravo nahoře)
class NextPiece(Widget):
    texture = ObjectProperty(None)
    def __init__(self, **kwargs):   # inicializace, načtení textur
        self.PIECES = [Image('crop/pieces/{0}.png'.format(y)).texture for y in range(1,8)]
        self.opacity = 0
        super(NextPiece, self).__init__(**kwargs)
    
    def showNext(self, piece):
        # Ukáže další blok, spustí animaci
        self.piece = piece
        print self.size
        self.delCurrent()
    
    def delCurrent(self):
        # Vymaže současný blok - animace spadnutí
        self.myPos = self.y
        anim = Animation(pos_hint={'top':.5}, opacity=0, d=.3)+Animation(pos_hint={'top':1.5}, d=0.001)
        anim.bind(on_complete=self.show)
        anim.start(self)
    
    def show(self, *args):
        # Ukáže další blok po skončení přechozí animace
        print "PCS: {0}, PC: {1}".format(len(self.PIECES), self.piece)
        self.texture = self.PIECES[self.piece-1]
        anim = Animation(pos_hint={'top': 1}, opacity=1, d=.3)
        anim.start(self)

# Ikona notifikace v herní obrazovce
class Notification(RelativeLayout):
    text = StringProperty("")
    def __init__(self, **kwargs):
        super(Notification, self).__init__(**kwargs)

class Unread(Label):
    # Číslo udávající počet nepřečtených zpráv v chatu
    pass

# Tzv. Toast - kontextová notifikace (např. při odpojení ze serveru)
class Toast(ModalView):
    _container = ObjectProperty(None)
    content = ObjectProperty(None)
    def __init__(self, **kwargs):   # inicializace
        super(Toast, self).__init__(**kwargs)
        try:
            timeout = kwargs['timeout']
        except:
            timeout = .5
        text = kwargs['text']
        self.content = Label(text=text, font_name="font/Roboto-Regular.ttf")
        Clock.schedule_once(self.dismiss, timeout=timeout)
        
    def add_widget(self, widget):
        if self._container:
            self.content = widget
        else:
            super(Toast, self).add_widget(widget)

    def on_content(self, instance, value):
        if not hasattr(value, 'toast'):
            value.create_property('toast')
        value.popup = self
        if self._container:
            self._container.clear_widgets()
            self._container.add_widget(value)

    def on__container(self, instance, value):
        if value is None or self.content is None:
            return
        self._container.clear_widgets()
        self._container.add_widget(self.content)

# Zaznamenávání gest
class GestureListener(Widget):
    def __init__(self, **kwargs):   # inicializace
        self.app = kwargs['root']
        self.register_event_type('on_swipe_right')
        self.register_event_type('on_swipe_left')
        super(GestureListener, self).__init__(**kwargs)
        self.gdb = GestureDatabase()
        self.GSTR_SWIPE_LEFT = \
        self.gdb.str_to_gesture('eNqtls2O2jAURvd+EdgU+f7bL0C3lXiAikIEaKYQQabtvH3tC0ITQZtZeJXkU3ycfEdK7vzwcvj1vth1l+Ht3IWvt2Mfw3zbQ1jNjuuf3Sz0WE7LgcJlNbsM59NLdymXHOavvYT5U8jKbwu9VpSV9f3pcBzqslSX5X8s+1bvCj1cn6A+wntZAhiWcRHr9n/qJdVL0pQNjZUIkAzC5cf6/1B2qITdnbe7oRBSxEwSIXJCmkb5a4E9olDEVCBnUGAUsmlWclZuwULvDeGRVSr62BfjNAudRU1YXj1KE5Z3j9aE5d3jQ/dfyikrIEgmzMCRTSZh5OUTtIF5+0RtYF4/SRuY90/WBuYCqI0AdgH8TAAmyBaVc8oCZvkTMBfA1AbmAljawFwAWxuYC+DcBCYuQNoIEBcgbQSIC5BnAjjFmCiJMSOxpemvv7gAsTYwFyC5CUxdgEIbmAtQagNzAdpGgLoAbSNAXYA+E6AEEa38eVWTaflNTLHM+zdowvL6jZqwvH2TT7LqmLc5d93xPrSZ1qnNLMyXlqSsXxLnchh6S2H9GOZrGD+GKXpoNArBQ8mjED1kGIXkIego5BpqHu2exEMbMzWsr6+27w67/VAnUbuPlb8P22FfoxSWEPUaDqfX7rw+buoInLJPGDW+Vfy9P5+2b5sKymUfXmA0SGqmkAG0Dh+Lv5QfIpE=')
        self.GSTR_SWIPE_RIGHT = \
        self.gdb.str_to_gesture('eNq1l82O2jAQgO9+Ebhs5Pm3X4C9VuIBKgoRi3YLEWTb7tvXnmzbjVQKquRcDJOZb4Z8KLKXh+fDt7du31/G13MfHt/XIYblboCwXhw3X/tFGLB8LAuFy3pxGc+n5/5SvnJYvgwSln+FrD0tDFpRVuqH0+E41rJUy/KVsk81KwwwTVBHeCslgGEVuxhZWRNH4KQ55eTz/Kj3KaweYkcZDJMiCwmBhsuXzb+7sHeRsL/eYP+LzQaQsmSIlqLqHXT/6WAT/aHi0VKCyDFlhMyW9A8fwWI0Js7MSJZv45PjcyM8ugGEVnh0PLXCu1mU+/CRAIgSppwVE0q6LRddLlq7Bq4Xc7MG5IIJ2jVwxUTtGrhkaieZXDLdI7n8R9nUVCxnFJUot+lumHIbOrtehkZ0d8vUiO5iWRrR3So3sspulRtZFbcqjayKW5VGVsWtyn1WBYSIxZBztKh8m+5WxRrR3arkNnR1qwqN6G5VqRHdrWojq+pWtZFVdavayKq5VWtk1dyq3WdVY0IDMpn2t7fhLtXkf+H1mLA99/3x96bftO76zcJyBdrFsCIqy8dLwzhYCpuSkK4n5JqAaX4n8pX0FGu60sTjspQYeA/ALs+uDxk4TZFmZeSdNc6CPI0js6CEzfQMnvrD/mmsRx4NK5yPV95UJeP7YTc+1QQrCZpLfQmOp5f+vDlu68krpfqIoYbfVX0ezqfd69axZWjuQKJC3dYgkGp9D3c/Ab86orc=')
        self.gdb.add_gesture(self.GSTR_SWIPE_LEFT)
        self.gdb.add_gesture(self.GSTR_SWIPE_RIGHT)
        
    def simplegesture(self, name, point_list):
        # Pomocná funkce pro rozpoznávání gesta
        g = Gesture()
        g.add_stroke(point_list)
        g.normalize()
        g.name = name
        return g
        
    def on_touch_down(self, touch):
        # Při doteku, spustí zaznamenávání
        if self.collide_point(touch.x, touch.y):
            touch.ud["line"] = Line(points=(touch.x, touch.y))
            touch.grab(self)
            print "< grabbed >"
            
    def on_touch_move(self, touch):
        # Při pohybu prstu, zaznamenává pohyb
        if (touch.grab_current is self):
            touch.ud["line"].points += [touch.x, touch.y]
    
    def on_touch_up(self, touch):
        # Při zvednutí prstu, porovnává s gestem v databázi
        if (touch.grab_current is self):
            g = self.simplegesture('', zip(touch.ud['line'].points[::2], touch.ud['line'].points[1::2]))
            g2 = self.gdb.find(g, minscore=0.80)
            if g2:
                if g2[1] == self.GSTR_SWIPE_LEFT:
                    self.dispatch('on_swipe_left')
                if g2[1] == self.GSTR_SWIPE_RIGHT:
                    self.dispatch('on_swipe_right')
            touch.ungrab(self)
    
    def on_swipe_left(self, *args):
        # Událost přejetí prstu doleva
        self.app.on_swipe_left()
    
    def on_swipe_right(self, *args):
        # Událost přejetí prstu doprava
        self.app.on_swipe_right()

# Barevný přechod na pozadí všech obrazovek
class FloatLayoutBG(FloatLayout):
    def __init__(self, **kwargs):
        img = Image("crop/bg.png")
        img.texture.wrap = "repeat"
        self.texture = img.texture
        self.gestures = False
        super(FloatLayoutBG, self).__init__(**kwargs)

# Šipka, za kterou se tahá při zobrazení ostatních hráčů
class Arrow(Widget):
    def __init__(self, **kwargs):
        img = Image('crop/arrow.png')
        self.texture = img.texture
        self.texture_size = self.texture.size
        super(Arrow, self).__init__(**kwargs)

# Protihráč a jeho jméno, pole
class Player(FloatLayout):
    def __init__(self, pid, name, **kwargs):
        self.opacity = 0
        super(Player, self).__init__(**kwargs)
        self.matrix = PlayerMatrix(cols=12, rows=22, size_hint=(0.95, 0.92), pos_hint={"center_x":1, "top":0})
        self.add_widget(self.matrix)
        self.add_widget(PlayerName(pid, name, size_hint=(1,0.08), pos_hint={"center_x":1, "top":0.08}))
    
    def on_touch_move(self, touch):
        # Označení hráče při pohybu prstu se speciální kostkou
        if self.children[0].collide_point(touch.x, touch.y) or self.children[1].collide_point(touch.x, touch.y):
            self.children[0].state = 'mark'
            self.children[1].state = 'mark'
        else:
            self.children[0].state = 'normal'
            self.children[1].state = 'normal'
    
    def on_touch_up(self, touch):
        # Po upuštění speciální kostky na hráče se aplikuje
        if self.children[0].collide_point(touch.x, touch.y) or self.children[1].collide_point(touch.x, touch.y):
            self.children[0].state = 'normal'
            self.children[1].state = 'normal'
            return True
        else:
            return False

# Seznam hráčů
class Players(FloatLayout):
    def __init__(self, **kwargs):
        super(Players, self).__init__(**kwargs)
        self.add_widget(Player(1, "None", size_hint=(0.4, 0.3), pos_hint={"right":0.275, "y":0.95}))
        self.add_widget(Player(2, "None", size_hint=(0.4, 0.3), pos_hint={"right":0.725, "y":0.95}))
        self.add_widget(Player(3, "None", size_hint=(0.4, 0.3), pos_hint={"right":0.275, "y":0.625}))
        self.add_widget(Player(4, "None", size_hint=(0.4, 0.3), pos_hint={"right":0.725, "y": 0.625}))
        self.add_widget(Player(5, "None", size_hint=(0.4, 0.3), pos_hint={"right":0.275, "y":0.295}))
        self.add_widget(Player(6, "None", size_hint=(0.4, 0.3), pos_hint={"right":0.725, "y":0.295}))

# Text se jménem hráče
class PlayerName(BoxLayout):
    colored = ListProperty([0.,.6,.8,1])
    text = StringProperty()
    state = StringProperty("normal")
    def __init__(self, pid, name, **kwargs):
        super(PlayerName, self).__init__(**kwargs)
        self.text = u"[font=font/Roboto-Bold.ttf]{0}[/font] {1}".format(pid, name)
        self.label = Label(font_name='font/Roboto-Medium.ttf', text=self.text, markup=True, font_size='9dp', valign="middle", text_size=self.size)
        self.add_widget(self.label)
        self.label.texture_size = self.label.text_size

# Celá vytahovací roletka s hráči
class Overlay(FloatLayout):
    def __init__(self, app, **kwargs):
        img = Image('crop/overlay_gradient_POT.png')
        img.texture.wrap = "repeat"
        self.texture = img.texture
        self.app = app
        super(Overlay, self).__init__(**kwargs)
        self.app.btnStart = Button(text='', size_hint=(.4,.07), pos_hint={"right":.57, "y":.02}, opacity=0, markup=True, background_color=(1,1,1, .3))
        self.app.insertStrings.append((self.app.btnStart, 'STR_START'))
        self.app.btnPause = Button(text='', size_hint=(.4,.07),pos_hint={"right":.99, "y":.02}, opacity=0, markup=True, background_color=(1,1,1, .3))
        self.app.insertStrings.append((self.app.btnPause, 'STR_PAUSE'))
        self.app.btnStart.bind(on_press=self.app.startgame)
        self.app.btnPause.bind(on_press=self.app.pausegame)
        self.add_widget(self.app.btnStart)
        self.add_widget(self.app.btnPause)
        self.add_widget(Arrow(size=(47,97), pos_hint={"center_y":0.98, "x":0}))
        self.add_widget(Players(size_hint_x=0.85, pos_hint=self.pos_hint, opacity=0))
        self.dposStorage = [0, ]
        self.trueSizeHint = 0
    
    def setSize(self):
        # Mění velikost
        self.trueSizeHint = 47./self.app.root.size[0]
        self.size_hint_x = self.trueSizeHint
    
    def on_touch_down(self, touch):
        # Stažení roletky nebo stisk tlačítek
        if self.children[1].collide_point(touch.x, touch.y):
            touch.grab(self)
        elif self.app.btnStart.collide_point(touch.x, touch.y):
            self.app.btnStart.dispatch('on_press')
        elif self.app.btnPause.collide_point(touch.x, touch.y):
            self.app.btnPause.dispatch('on_press')
        
    def on_touch_move(self, touch):
        # Pohyb prstem, změna velikosti roletky, vytahování
        ref = self.parent.size[0]*0.45
        ref2 = self.parent.size[0]*0.3
        if (touch.grab_current is self) and (touch.x > ref2):
            dpos = (touch.dpos[0]/self.parent.size[0])
            if not((self.size_hint_x > 0.7 and dpos <= 0) or (self.size_hint_x < self.trueSizeHint and dpos >= 0)):
                self.size_hint_x -= dpos
            size = self.children[0].size[0]
            maxsize = self.parent.size[0]*0.7*self.children[0].size_hint_x
            if size < ref:
                self.children[0].opacity = 0
                self.app.btnStart.opacity = 0
                self.app.btnPause.opacity = 0
            else:
                if (size-ref)/(maxsize-ref) <= 1:
                    self.children[0].opacity = (size-ref)/(maxsize-ref)
                    self.app.btnStart.opacity = self.children[0].opacity
                    self.app.btnPause.opacity = self.children[0].opacity
            self.dposStorage.append(touch.dpos[0])
                    
    def on_touch_up(self, touch):
        # Zvednutí prstu, vytažení nebo zatažení roletky
        if touch.grab_current is self:
            widgets = [self, self.children[0], self.app.btnStart, self.app.btnPause]
            anims1 = [Animation(size_hint_x=.7, t='linear', d=.05), Animation(opacity=1, t='linear', d=.05)]
            anims2 = [Animation(size_hint_x=self.trueSizeHint, t='linear', d=.05), Animation(opacity=0, t='linear', d=.05)]
            if (touch.dpos[0] < 0) or (self.prumer() < 0):
                for i, w in enumerate(widgets):
                    if i == 0:
                        anims1[0].start(w)
                    else:
                        anims1[1].start(w)
            elif (touch.dpos[0] > 0) or (self.prumer() > 0):
                for i, w in enumerate(widgets):
                    if i == 0:
                        anims2[0].start(w)
                    else:
                        anims2[1].start(w)
            else:
                pass
            self.dposStorage = [0, ]
            touch.ungrab(self)
    
    def prumer(self):
        # Pomocná funkce pro průměr
        soucet = 0
        for i in self.dposStorage:
            soucet += i
        return float(soucet)/len(self.dposStorage)

# Inventář speciálních kostek (dole)
class Dock(ScrollView):
    def __init__(self, app, **kwargs):
        self.app = app
        self.bar_color = [.071, .729, .973, .9]
        self.bar_width = '3dp'
        self.scroll_timeout = 100
        img = Image('crop/dock_POT.png')
        img.texture.wrap = "repeat"
        self.texture = img.texture
        self.texture_size = self.texture.size
        self.sOverlay = app.sOverlay
        self.players = app.overlay
        super(Dock, self).__init__(**kwargs)
        self.bar_margin = self.texture_size[1]*0.1645
        self.do_scroll_y = False
        self.do_scroll_x = True
        self.layout = BoxLayout(size_hint_x=None, width=0)
        self.add_widget(self.layout)
    
    def addSpecial(self, sType):
        # Přidá speciální kostku do inventáře
        if self.app.field.startgame and (self.app.paused == False):
            special = Special(sType, self.app, pos_hint={'top':1}, size_hint=(None,0.767), opacity=.8)
            children = []
            for i in self.layout.children:
                children.append(i)
            for i in children:
                self.layout.remove_widget(i)
            children.append(special)
            children.reverse()
            for i in children:
                i.opacity = .4
                self.layout.add_widget(i)
            self.layout.children[-1].opacity = 0.8
            self.layout.width = self.layout.children[0].size[1]*(len(self.layout.children)/1.9)

# Speciální kostka (v inventáři)
class Special(Widget):
    texture = ObjectProperty(None)
    def __init__(self, sType, app, **kwargs):
        self.sType = sType.lower()
        self.name = None
        self.app = app
        self.sOverlay = self.app.sOverlay
        self.players = self.app.overlay
        if self.sType in ("a", "c", "n", "r", "s", "b", "g", "q", "o"):
            self.texture = Image("crop/icons/{0}.png".format(self.sType)).texture
            self.texture_size = self.texture.size
            self.name = self.app.L.STR_BLOCK_A
        super(Special, self).__init__(**kwargs)
    
    def on_touch_down(self,touch):
        # Při stisku uvolní kostku z inventáře
        if self.collide_point(touch.x, touch.y) and (self.parent.children[-1] == self):
            self.opacity = 0
            over = SpecialOv(self, size=self.size, pos=self.pos, size_hint=(None, None))
            self.sOverlay.add_widget(over)
            touch.grab(over)
            self.previous = self.pos
            self.players.size_hint_x = 0.7
            self.players.children[0].opacity = 1
    
    def drop(self, touch):
        # Upuštění speciální kostky na hráče
        self.players.size_hint_x = self.players.trueSizeHint
        self.players.children[0].opacity = 0
        self.opacity = 0.8
    
    def applySpecial(self, pid):
        # Pošle speciální kostku hráči
        convert = [6,5,4,3,2,1]
        print "got it "+str(convert[pid])
        self.app.send_message("sb {0} {1} {2}".format(convert[pid], self.sType, self.app.id))
        if convert[pid] == self.app.id:
            self.app.print_message("sb {0} {1} {2}\xff".format(convert[pid], self.sType, self.app.id))
        if len(self.parent.children) > 1:
            self.parent.children[-2].opacity = 0.8
        self.parent.size = (self.parent.size[0]-self.size[0], self.parent.size[1])
        self.parent.remove_widget(self)

# Speciální kostka při pohybu mimo inventář
class SpecialOv(Widget):
    def __init__(self, root, **kwargs):
        self.root = root
        self.texture = self.root.texture
        self.opacity = 1
        super(SpecialOv, self).__init__(**kwargs)
    
    def on_touch_move(self, touch):
        # S pohybem prstu se mění poloha kostky
        if touch.grab_current is self:
            self.x += touch.dpos[0]
            self.y += touch.dpos[1]
            self.root.players.children[0].on_touch_move(touch)
    
    def on_touch_up(self, touch):
        # Upuštění na příslušného hráče
        if touch.grab_current is self:
            pid = None
            for i, player in enumerate(self.root.players.children[0].children):
                if player.on_touch_up(touch) and player.opacity == 1:
                    pid = i
            if pid != None:
                self.root.applySpecial(pid)
            touch.ungrab(self)
            self.root.drop(touch)
            self.parent.remove_widget(self)

# Pole protihráče
class PlayerMatrix(FloatLayout):
    state = StringProperty("normal")
    def __init__(self, **kwargs):   # inicializace
        self.rows = kwargs['rows']
        self.cols = kwargs['cols']
        super(PlayerMatrix, self).__init__(**kwargs)
        self.coords = []
        self.inactive_color = [.1372,.1372,.1372,1]
        
        for y in range(int(self.rows)):
            line = []
            for x in range(int(self.cols)):
                box = None
                line.append(box)
            self.coords.append(line)
    
    def drop(self, coords):
        # Vymazání kostky z pole
        self.remove_widget(self.coords[coords[1]][coords[0]])
    
    def mark(self, coords, color, sType=False):
        # Obarvení kostky v poli
        box = Box(size_hint=(None, None))
        box.coords = (coords[0], coords[1])
        box.colored = color
        box.size_hint = (1/12., 1/22.)
        box.pos_hint = {'x':coords[0]*(1/12.), 'y':(21-coords[1])*(1/22.)}
        box.opacity = 1
        self.add_widget(box)
        self.coords[coords[1]][coords[0]] = box
        box.active = True
        if sType != False:
            box.special(sType, True)
