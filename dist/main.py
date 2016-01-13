#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 30 23:40:10 2012

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
import kivy
kivy.require('1.6.0')
import kivy.utils as utils
from kivy.support import install_twisted_reactor
from kivy.support import install_android
install_twisted_reactor()
install_android()
PLATFORM = utils.platform()
if PLATFORM == "android":
    import android
    android.init()
from twisted.internet import reactor, protocol
from kivy.clock import Clock
from re import findall
from random import randint
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from box import GameMatrix
from kivy.app import App
from kivy.lang import Builder
from languages import Strings, LANGUAGES
from tetriwidgets import Overlay, Dock
from collections import namedtuple
from tetriwidgets import FloatLayoutBG, GestureListener, Toast, Notification, NextPiece
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.uix.image import Image
from screens import screensStr, langStr, PartylineScreen, StatsScreen, ConnectScreen, LanguageScreen, MainMenuScreen, SettingsScreen, BookmarksScreen, TutorialMove, TutorialDrop, TutorialSpecial, TutorialNavigate, TutorialPlayers

# Přednastavení stylů pro výběr jazyka
for j, i in enumerate(LANGUAGES.items()):
    screensStr += langStr.format(i[0], i[1], 0.8-(j*0.2))

# Načtení stylů
Builder.load_file("box.kv")
Builder.load_file('players.kv')
Builder.load_file('screens.kv')
Builder.load_string(screensStr)

ServerConf = namedtuple('ServerConf', 'startHeight, startLvl, linesLvl, lvlInc, linesSpecial, specialsAdded, specialCapacity, blockFreq, specialFreq, avgLvl, classic, seed')

# Přednastavení pro kódování barev, souřadnic, speciálních kostek
COLORS = {
'"':[0,.6,.8,1],
'#':[1,.7333333,.2,1],
'$':[.6,.8,0,1],
'%':[.666666667,.4,.8,1],
'&':[1,.266666667,.266666667,1]
}

SPECIALS_F = [chr(c) for c in range(39,48)]
SPECIALS = ["a", "c", "n", "r", "s", "b", "g", "q", "o"]
COORDS_X = [chr (x) for x in range(51,63)]
COORDS_Y = [chr(y) for y in range(51,73)]

# Komunikace se sítí
class EchoClient(protocol.Protocol):
    def connectionMade(self):   # spojení navázáno
        self.factory.app.on_connection(self.transport)

    def dataReceived(self, data):   # příjem dat
        self.factory.app.print_message(data)
        

class EchoFactory(protocol.ClientFactory):
    protocol = EchoClient
    def __init__(self, app):    # inicializace
        self.app = app

    def clientConnectionLost(self, conn, reason):   # spojení ztraceno
        if self.app.disconnect == False:
            if self.app.version == '1.13':
                self.app.version = '1.14'
            elif self.app.version == '1.14':
                self.app.version = '1.13'
            self.app.connect_to_server()
        else:
            self.app.sm.current = "ConnectScreen"
            Toast(text=self.app.L.STR_CONNECTION_FAILED, timeout=3).open()
        print reason

    def clientConnectionFailed(self, conn, reason): # spojení selhalo
        self.app.sm.current = "ConnectScreen"
        Toast(text=self.app.L.STR_CONNECTION_FAILED, timeout=3).open()
        print reason

# Hlavní třída programu
class TetriNET(App):
    connection = None
    def __init__(self, **kwargs):   # inicializace
        super(TetriNET, self).__init__(**kwargs)
        self.id = False
        self.team = ''
        self.nickname = ''
        self.players = {1:list(), 2:list(), 3:list(), 4:list()}
        self.tetrifast = False
        self.serverIP = None
        self.version = "1.14"
        self.transform = [5,4,3,2,1,0]
        self.serverConf = None
        self.paused = False
        self.linesCleared = 0
        self.lvl = 0
        self.connLost = 0
        self.L = None
        self.insertStrings = []
        self.disconnect = False
        self.addBookmark = False

    def on_pause(self, *args): # režim pozastavení pro OS Android
        return True

    # Import jazyků do proměnných (většinou widgetů)
    def doStrInsert(self):
        self.L = Strings(self.Cfg[0])
        self.nickname = self.Cfg[1]
        self.team = self.Cfg[2]
        for string in self.insertStrings:
            try:
                replace = eval("self.L.{0}".format(string[1]))
                if string[1] != "STR_CONNECTPOPUP":
                    if string[1] in ("STR_PAUSE", "STR_START", "STR_STOP"):
                        string[0].text = "[color=#333333]{0}[/color]".format(replace)
                    else:
                        string[0].text = replace
                else:
                    string[0].title = replace
            except IndexError:
                strings = []
                for y in dir(string[0]):
                    if y.startswith("STR_"):
                        strings.append(y)
                for i in strings:
                    exec("string[0].{0} = self.L.{0}".format(i))
    
    def build(self):    # voláno automaticky při spuštění
        if self.onAndroid():
            self.bind(on_start = self.post_build_init)
        root = self.setup_gui()
        self.Cfg = self.getConfig()
        if (self.Cfg != False) and (len(self.Cfg) == 5):
            print self.Cfg
            self.doStrInsert()
            self.nickname = self.Cfg[1]
            self.team = self.Cfg[2]
            self.sm.current = self.sm.next()
            connectScr = self.sm.get_screen('ConnectScreen')
            if len(self.Cfg[3]) == 3:
                connectScr.server = [y for y in self.Cfg[3]]
            print self.Cfg[3]
            connectScr.team = self.team
            connectScr.nickname = self.nickname
        else:
            print LANGUAGES.keys()
            print self.Cfg
        return root
    
    def setup_gui(self):    # vytváří grafické rozhraní
        self.sm = ScreenManager(transition=SlideTransition(direction="left"))
        self.gameScreen = Screen(name='GameScreen')
        self.layout = FloatLayoutBG(size_hint=(1,1))
        self.sOverlay = FloatLayout(size_hint=(1,1))
        self.field = GameMatrix(self, cols=12, rows=22, size_hint=(0.75, 0.83), pos_hint={'center_x':0.5, 'center_y':0.5}, master=self.layout, spacing=1)
        self.id_label = Label(font_name='font/Roboto-Thin.ttf', text=u'', pos_hint={'top':1, 'right':0.125}, size_hint=(0.125,0.085), font_size='48dp')
        self.overlay = Overlay(self, size_hint=(.1,1), pos_hint={"right":1})
        self.dock = Dock(self, size_hint=(0.75,0.0845), pos_hint={'center_x':0.5}, opacity=1)
        self.layout.add_widget(self.field, index=0)
        self.layout.add_widget(self.id_label, index=0)
        self.nicknameLabel = Label(font_name='font/Roboto-Regular.ttf', text=self.nickname, pos_hint={'top':1, 'center_x':0.5}, font_size='26dp', size_hint=(0.75,0.085))
        self.nextPiece = NextPiece()
        self.layout.add_widget(self.nextPiece)
        self.layout.add_widget(self.nicknameLabel, index=0)
        self.layout.add_widget(self.dock, index=0)
        self.layout.add_widget(self.overlay)
        self.layout.add_widget(self.sOverlay)
        self.layout.add_widget(GestureListener(root=self, pos_hint={'x': 0}))
        self.chat = Notification()
        self.chat.unread.opacity = 0
        self.layout.add_widget(self.chat)
        self.gameScreen.add_widget(self.layout)
        self.sm.add_widget(LanguageScreen(name='LanguageScreen', root=self))
        self.sm.add_widget(MainMenuScreen(name='MainMenuScreen', root=self))
        self.sm.add_widget(ConnectScreen(name='ConnectScreen', root=self))
        self.sm.add_widget(self.gameScreen)
        self.sm.add_widget(PartylineScreen(name="PartylineScreen", root=self))
        self.sm.add_widget(StatsScreen(name="StatsScreen", root=self))
        self.sm.add_widget(SettingsScreen(name="SettingsScreen", root=self))
        self.sm.add_widget(BookmarksScreen(name="BookmarksScreen", root=self))
        self.sm.add_widget(TutorialMove(root=self, name="TutorialMove", directory="moving", frames=5))
        self.sm.add_widget(TutorialDrop(root=self, name="TutorialDrop", directory="drop", frames=3))
        self.sm.add_widget(TutorialSpecial(root=self, name="TutorialSpecial", directory="sendspecial", frames=4))
        self.sm.add_widget(TutorialNavigate(root=self, name="TutorialNavigate", directory="navigation", frames=7))
        self.sm.add_widget(TutorialPlayers(root=self, name="TutorialPlayers", directory="players", frames=4))
        return self.sm
    
    def post_build_init(self, instance):    # voláno po spuštění programu, namapuje systémové klávesy Androidu
        android.map_key(android.KEYCODE_MENU, 1000)
        android.map_key(android.KEYCODE_BACK, 1001)
        android.map_key(android.KEYCODE_HOME, 1002)
        android.map_key(android.KEYCODE_SEARCH, 1003)
        android.map_key(android.KEYCODE_APP_SWITCH, 1004)
        win = self._app_window
        win.bind(on_keyboard=self._key_handler)
    
    def _key_handler(self, instance, KEY, *args):   # Reakce na stisk systémové klávesy OS Android
        print "Key: {0}".format(KEY)
        if KEY == 1001:
            if self.sm.current not in ('MainMenuScreen', 'GameScreen'):
                if self.sm.current == "SettingsScreen":
                    self.sm.get_screen("SettingsScreen").dropdown.dismiss()
                self.sm.current_screen.prev()
            else:
                if self.sm.current == 'MainMenuScreen':
                    text = self.L.STR_POPUP_EXIT
                    title = self.L.STR_POPUP_EXIT_TITLE
                    yes_callback = self.popupStop
                else:
                    text = self.L.STR_POPUP_DISCONNECT
                    title = self.L.STR_POPUP_DISCONNECT_TITLE
                    yes_callback = self.popupDisconnect
                content = BoxLayout(orientation='vertical')
                content.add_widget(Label(text=text, font_name='font/Roboto-Regular.ttf', font_size='14dp'))
                buttons = GridLayout(cols=2, rows=1, spacing=10, size_hint=(1, .3))
                yes = Button(text=self.L.STR_YES)
                yes.bind(on_press=yes_callback)
                no = Button(text=self.L.STR_NO)
                buttons.add_widget(yes)
                buttons.add_widget(no)
                content.add_widget(buttons)
                self.popupExit = Popup(title=title, size_hint=(.7,.3), content=content, auto_dismiss=False)
                no.bind(on_press=self.popupExit.dismiss)
                self.popupExit.open()
        elif KEY == 1002:
            self.dispatch('on_pause')
        elif KEY == 1004:
            self.dispatch('on_pause')
    
    def popupDisconnect(self, instance):
        # Odpojení ze serveru z vyskakovacího okna (po stisku systémové klávesy zpět v herní obrazovce)
        # Pouze pro OS Android
        self.popupExit.dismiss(instance)
        self.print_message("endgame\xff")
        self.startgame(instance)
        Clock.unschedule(self.heartbeat)
        self.sm.get_screen("StatsScreen").stats.clear_widgets()
        self.sm.get_screen("PartylineScreen").SLayout.clear_widgets()
        self.disconnect = True
        self.connection.loseConnection()
        self.connection = None
        self.id = False
        self.field.startgame = False
        self.sm.transition = SlideTransition(direction="right")
        self.sm.current = 'ConnectScreen'
    
    def popupStop(self, instance): 
        # Ukončení aplikace přes vyskakovací okno (po stisku systémové klávesy zpět v hlavním menu)
        # Pouze pro OS Android
        self.popupExit.dismiss(instance)
        self.stop()
    
    def connect_to_server(self):    # Připojení k serveru
        self.disconnect = False
        reactor.connectTCP(self.server, 31457, EchoFactory(self))

    def on_connection(self, connection):    # Voláno při navázání spojení, přihlašování TetriNET
        self.print_message(self.L.STR_CONNECTION_SUCCESS)
        self.connection = connection
        self.serverIP = self.connection.getPeer().host
        self.connection.write(self.loginEncode()+chr(255))
        Clock.schedule_interval(self.heartbeat, 10)

    def send_message(self, msg):    # Odeslání zprávy na server
        if self.connection:
            self.connection.write(str(msg)+chr(255))

    def print_message(self, msg):
        # Tisk serverové zprávy do konzole a zpracování
        if self.id == False:
            if self.tetrifast:
                numRegex = "\\)\\#\\)\\(\\!\\@\\(\\*3\\ \d"
            else:
                numRegex = "playernum (\d)\xff"
            f = findall(numRegex, msg)
            if len(f) == 1:
                if self.tetrifast:
                    self.id = int(f[0][-1])
                else:
                    self.id = int(f[0])
                self.players[self.id] = [self.nickname, None]
                self.id_label.text = str(self.id)
                self.nicknameLabel.text = self.nickname
                Clock.schedule_once(self.team_select, 0.5)
        if self.tetrifast == False:
            newgameRegex = "newgame (.*) (.*) (.*) (.*) (.*) (.*) (.*) (.*) (.*) (.*) (.*) (.*)\xff"
            newgameRegex113 = "newgame (.*) (.*) (.*) (.*) (.*) (.*) (.*) (.*) (.*) (.*) (.*)\xff"
        else:
            newgameRegex = "\\*\\*\\*\\*\\*\\*\\* (.*) (.*) (.*) (.*) (.*) (.*) (.*) (.*) (.*) (.*) (.*) (.*)\xff"
            newgameRegex113 = "\\*\\*\\*\\*\\*\\*\\* (.*) (.*) (.*) (.*) (.*) (.*) (.*) (.*) (.*) (.*) (.*)\xff"
        if self.id != False:
            newgame = findall(newgameRegex, msg)
            print newgame
            new = False
            if len(newgame)==1:
                self.serverConf = ServerConf._make(newgame[0][:-1]+(int(newgame[0][-1], 16), ))
                print newgame[0][-1]
                new = True
                print "mam seed"
            else:
                newgame113 = findall(newgameRegex113, msg)
                if len(newgame113) == 1:
                    self.serverConf = ServerConf._make(newgame113[0]+(randint(0,0xFFFFFF),))
                    new = True
                    print "nemam seed"
            if new:
                self.field.seed = self.serverConf.seed
                print self.serverConf
                self.btnStart.text = "[color=#333333]{0}[/color]".format(self.L.STR_STOP)
                self.btnStart.bind(on_press=self.startgame)
                self.field.spectate = False
                self.field._build()
                self.lvl = int(self.serverConf.startLvl)
                for p in range(6):
                        self.overlay.children[0].children[p].matrix.clear_widgets()
        playerjoin = findall("playerjoin (.*?) (.*?)\xff", msg)
        if len(playerjoin)>=1:
            for player in playerjoin:
                pid = int(player[0])
                name = player[1]
                print pid, name
                self.players[pid] = [name, None]
                print self.players
                print (pid, name)
                child = self.transform[pid-1]
                insert = self.overlay.children[0].children[child].children[0]
                insert.label.text = u"[font=font/Roboto-Bold.ttf]{0}[/font] {1}".format(pid, name)
                insert.label.font_size = insert.size[1]-9
                print insert.size
                insert.label.text_size = (self.layout.size[1]*.13, None)
                self.overlay.children[0].children[child].opacity = 1
        stats = findall(r"(t|p)(.*?);(\d+)", msg)
        if len(stats) >= 1:
            self.sm.get_screen("StatsScreen").stats.clear_widgets()
            for row in stats:
                add = BoxLayout(orientation='horizontal')
                for cell in row:
                    trim = ""
                    for i in [y for y in cell if ord(y) in range(0,128)]:
                        trim += i
                    if trim not in ('t', 'p'):
                        add.add_widget(Label(font_name='font/Roboto-Regular.ttf', text=trim))
                    else:
                        if trim == 'p':
                            source = 'crop/icons/player.png'
                        elif trim == 't':
                            source = 'crop/icons/team.png'
                        add.add_widget(Image(source=source))
                self.sm.get_screen("StatsScreen").stats.add_widget(add)
        if self.field.startgame or self.field.spectate:
            field = findall("f (.*?) (.*?)\xff", msg)
            if len(field) == 1:
                pid = int(field[0][0])
                print field, type(field)
                print self.players
                print pid
                self.players[pid][1] = field[0][1]
                print self.players
                matrix = field[0][1]
                if len(matrix) < 264:
                    color = None
                    child = self.transform[pid-1]
                    coords = ""
                    for i in range(len(matrix)):
                        if matrix[i] in self.field.tnetColors:
                            color = matrix[i]
                        else:
                            if len(coords) == 0:
                                coords += matrix[i]
                            elif len(coords) == 1:
                                coords += matrix[i]
                            else:
                                coords = matrix[i]
                        if len(coords) == 2:
                            x = COORDS_X.index(coords[0])
                            y = COORDS_Y.index(coords[1])
                            box = self.overlay.children[0].children[child].matrix.coords[y][x]
                            if color == "!":
                                if type(box) != type(None):
                                    self.overlay.children[0].children[child].matrix.drop((x,y))
                                    self.overlay.children[0].children[child].matrix.coords[y][x] = None
                            elif color in SPECIALS_F:
                                if type(box) == type(None):
                                    self.overlay.children[0].children[child].matrix.mark((x,y), [.1372,.1372,.1372,1], SPECIALS[SPECIALS_F.index(color)])
                                else:
                                    box.texture = False
                                    box.colored = [.1372,.1372,.1372,1]
                                    box.special(SPECIALS[SPECIALS_F.index(color)], True)
                            else:
                                if type(box) == type(None):
                                    self.overlay.children[0].children[child].matrix.mark((x,y), COLORS[color])
                                else:
                                    box.texture = False
                                    box.colored = COLORS[color]
                            coords = ""
            if self.field.startgame:
                specUsed = findall("sb (.*?) (.*?) (.*?)\xff", msg)
                if len(specUsed) >= 1:
                    for sb in specUsed:
                        print sb
                        targetnum = int(sb[0])
                        sendernum = int(sb[2])
                        stype = sb[1]
                        if targetnum == self.id:
                            if stype == 'a':
                                self.field.addLine()
                            if stype == 'c':
                                self.field.clearLine()
                            if stype == 'n':
                                self.field.nuke()
                            if stype == 'r':
                                self.field.randomClear()
                            if stype == 's':
                                if sendernum != targetnum:
                                    child = self.transform[sendernum-1]
                                    self.field.switchField(child)
                            if stype == 'b':
                                self.field.clearSpecials()
                            if stype == 'g':
                                self.field.gravity()
                            if stype == 'q':
                                self.field.quake()
                            if stype == 'o':
                                self.field.blockBomb()
                        else:
                            if stype == 's':
                                if sendernum != targetnum:
                                    child = self.transform[targetnum-1]
                                    self.field.switchField(child)
                        if len(stype) == 1:
                            print self.L.STR_SPECIALSENT.format(self.players[sendernum][0], eval("self.L.STR_BLOCK_{0}".format(stype.upper())), self.players[targetnum][0])
                        else:
                            if (targetnum == 0) and (sendernum != self.id):
                                for i in range(int(stype[2:])):
                                    self.field.addLine()
        pause = findall("pause (.*?)\xff", msg)
        if len(pause) >= 1:
            if pause[0][0] == '1':
                Clock.unschedule(self.field.fall)
                self.paused = True
            else:
                Clock.schedule_interval(self.field.fall, 1)
                self.paused = False
        endgame = findall("endgame\xff", msg)
        if len(endgame) == 1:
            Clock.unschedule(self.field.fall)
            self.field.startgame = False
            self.field.spectate = False
            self.btnStart.text = "[color=#333333]{0}[/color]".format(self.L.STR_START)
            for y in range(22):
                for x in range(12):
                    self.field.drop((x,y))
                    for p in range(6):
                        if type(self.overlay.children[0].children[p].matrix.coords[y][x]) != type(None):
                            self.overlay.children[0].children[p].matrix.drop((x,y))
                        self.overlay.children[0].children[p].matrix.coords[y][x] = None
            self.field.colored = set()
            self.field.specials = set()
            self.field.fUpdate = 12*22*"0"
            self.dock.layout.clear_widgets()
            Animation(opacity=0).start(self.nextPiece)
        playerleave = findall("playerleave (.*?)\xff", msg)
        if len(playerleave) >= 1:
            for player in playerleave:
                print playerleave
                pid = self.transform[int(player)-1]
                self.overlay.children[0].children[pid].opacity = 0
                self.players[int(player)] = []
                if len(self.players) == 1:
                    self.print_message("endgame\xff")
        playerlost = findall("playerlost (.*?)\xff", msg)
        if len(playerlost) >= 1:
            for player in playerlost:
                if int(player) == self.id:
                    self.field.spectate = True
                    self.dock.layout.clear_widgets()
                    Animation(opacity=0).start(self.nextPiece)
        playerwon = findall("playerwon (.*?)\xff", msg)
        if len(playerwon) >= 1:
            self.print_message('endgame\xff')
        ingame = findall("ingame\xff", msg)
        if len(ingame) == 1:
            self.field.spectate = True
        pline = findall("pline (.*?) (.*?)\xff", msg)
        if len(pline) >= 1:
            print pline
            for msg in pline:
                pid = int(msg[0])
                if pid == 0:
                    formStr = "[font=font/Roboto-Bold.ttf][color=ff0000]<SERVER>[/color][/font] {0}"
                else:
                    formStr = "[font=font/Roboto-Bold.ttf]<{0}>[/font] {{0}}".format(self.players[pid][0])
                    try:
                        i = int(self.chat.text)
                    except:
                        i = 0
                    self.chat.text = str(i+1)
                    self.chat.unread.opacity = 1
                scr = self.sm.get_screen('PartylineScreen')
                scr.SLayout.add_widget(Label(font_name='font/Roboto-Regular.ttf', text_size=(self.layout.width*.75, None), markup=True, text=formStr.format(msg[1]), size_hint=(None,None)))
                scr.scroll.scroll_y = 0
        
    def loginEncode(self):
        # Algoritmus přihlášení k TetriNET serveru (zašifrování zprávy)
        if self.tetrifast == True:
            tetris = "tetrifaster"
        else:
            tetris = "tetrisstart"
        msg = "{0} {1} {2}".format(tetris, self.nickname, self.version)
        h = [int(y) for y in self.serverIP.split(".")]
        h = str(54*h[0] + 41*h[1] + 29*h[2] + 17*h[3])
        dec = randint(0, 255)
        encodedStr = "{0:02X}".format(dec)
        for i in range(len(msg)):
            dec = ((dec + ord(msg[i]))%255) ^ ord(h[i % len(h)])
            encodedStr += "{0:02X}".format(dec)
        print encodedStr.upper()
        return encodedStr.upper()
    
    def heartbeat(self, dt):
        # Udržení spojení, posílá znak FF hex na server
        if self.connection != None:
            self.connection.write(chr(255))
    
    def team_select(self, dt):
        # Výběr týmu, odesláno hned po přihlášení k serveru
        if self.connection != None:
            self.connection.write("team {0} {1}\xff".format(self.id, self.team))
            self.print_message("playerjoin {0} {1}\xff".format(self.id, self.nickname))
    
    def startgame(self, instance):
        # Start hry po stisku tlačítka START v herní obrazovce
        if self.onAndroid():
            self.vibrate(0.05)
        if self.connection != None:
            state = 0
            if self.field.startgame == False:
                state = 1
            self.connection.write("startgame {0} {1}\xff".format(state, self.id))
            self.Cfg[3] = (self.server, self.version, 'classic' if self.tetrifast == False else 'tetrifast')
            if self.addBookmark:
                serv = (self.server, self.version, 'classic' if self.tetrifast == False else 'tetrifast')
                if serv not in self.Cfg[-1]:
                    self.Cfg[-1].append(serv)
            self.refreshCfg()
    
    def pausegame(self, instance):
        # Pozastavení hry tlačítkem POZASTAVIT v herní obrazovce
        if self.onAndroid():
            self.vibrate(0.05)
        if self.paused == True:
            state = 0
        else:
            state = 1
        self.send_message("pause {0} {1}".format(state, self.id))
    
    def onAndroid(self):
        # Pomocná funkce pro Android
        if PLATFORM == "android":
            return True
        else:
            return False
    
    def vibrate(self, t):
        # Vibrace Android telefonu
        android.vibrate(t)
    
    def getConfig(self):
        # Čte konfigurační soubor config.ini
        try:
            f = open("config.ini", "r")
            cfg = [y.strip() for y in f.readlines()]
            f.close()
            cfg[-2] = eval(cfg[-2])
            cfg[-1] = eval(cfg[-1])
            print cfg
            return cfg
        except:
            return False
    
    def makeCfg(self, lang):
        # Vytváří konfiguraci
        if self.Cfg:
            self.Cfg[0] = lang
        else:
            self.Cfg = [lang, '', '', tuple(), list()]
        self.refreshCfg()
        self.doStrInsert()
    
    def refreshCfg(self):
        # Zapíše změny do konfiguračního souboru
        f = open("config.ini", "w")
        f.writelines([str(y)+"\n" for y in self.Cfg])
        f.close()
    
    def on_swipe_right(self):
        # Vyvoláno při tažení prstu doprava na obrazovkách obsahující
        # GestureListener
        self.sm.transition = SlideTransition(direction="right")
        if self.sm.current_screen.name == "GameScreen":
            self.sm.current = "PartylineScreen"
            self.chat.text = ""
            self.chat.unread.opacity = 0
        else:
            try:
                if self.sm.current_screen.input.focus:
                        self.sm.current_screen.input.focus = False
            except:
                pass
            self.sm.current = "StatsScreen"
        print "< swipe right >"
    
    def on_swipe_left(self):
        # Vyvoláno při tažení prstu doleva na obrazovkách obsahující
        # GestureListener
        self.sm.transition = SlideTransition(direction="left")
        if self.sm.current_screen.name == "StatsScreen":
            self.sm.current = "PartylineScreen"
        elif self.sm.current_screen.name == "PartylineScreen":
            if self.sm.current_screen.input.focus:
                    self.sm.current_screen.input.focus = False
            self.chat.unread.opacity = 0
            self.chat.text = ""
            self.sm.current = "GameScreen"
        print "< swipe left >"

if __name__ == '__main__':
    TetriNET().run()