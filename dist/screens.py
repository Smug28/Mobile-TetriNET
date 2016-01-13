# -*- coding: utf-8 -*-
"""
Created on Tue Feb 26 17:02:31 2013

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

from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.properties import ListProperty, StringProperty, NumericProperty
from tetriwidgets import GestureListener
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
import kivy.utils as utils
from kivy.animation import Animation
from kivy.uix.boxlayout import BoxLayout
from tetriwidgets import Toast
if utils.platform() == "android":
    import android
from kivy.uix.dropdown import DropDown
from languages import LANGUAGES
from tetriwidgets import Bookmark, DelButton
from kivy.clock import Clock

# Řetězce se styly pro obrazovku výběru jazyka
screensStr = """
<LanguageScreen>:
    FloatLayoutBG:
        BoxLayout:
            orientation: 'vertical'
            pos_hint: {'center_x': .5, 'top': 1}
            size_hint: (1, .1)
            FloatLayout:
                size: (root.size[0], root.size[1]-4)
                pos_hint: {'top':.9}
                Label:
                    text: 'Choose your language'
                    font_name: "font/Roboto-Thin.ttf"
                    size_hint: (1, .9)
                    height: self.texture_size[1] + 16
                    text_size: self.width - 16, None
                    pos_hint: {'x': .1, 'top':.9}
                    font_size: "36dp" if root.size[1]+24 < self.size[1] else "24dp"
            Widget:
                size_hint_y: None
                height: 4
                canvas:
                    Color:
                        rgba: root.separator_color
                    Rectangle:
                        pos: self.x, self.y + root.separator_height / 2.
                        size: self.width, root.separator_height
"""
langStr = """
        BoxLayout:
            size_hint: (.7, None)
            height: 70
            pos_hint: {{'center_x': .5, 'top': {2}}}
            orientation: 'horizontal'
            Image:
                size: (140,70)
                size_hint: (None, None)
                allow_stretch: True
                keep_ratio: False
                source: "./crop/languages/{0}.png"
            Button:
                background_color: (0,0,0,0)
                font_name: "font/Roboto-Thin.ttf"
                font_size: "36dp"
                text: '{1}'
                on_press: root.setLang('{0}')"""

# 'Boční' obrazovka (na obou stranách naslouchá gesta)
class SideScreen(Screen):
    separator_color = ListProperty([47 / 255., 167 / 255., 212 / 255., 1.])
    separator_height = NumericProperty('2dp')
    text = StringProperty("")
    def __init__(self, **kwargs):   # inicializace
        self.root = kwargs['root']
        super(SideScreen, self).__init__(**kwargs)
        self.add_widget(GestureListener(root=self.root, pos_hint={'x': .875}))
        self.add_widget(GestureListener(root=self.root, pos_hint={'x': 0}))

# Obrazovka Partyline (chat)
class PartylineScreen(SideScreen):
    def __init__(self, **kwargs):   # inicializace
        super(PartylineScreen, self).__init__(**kwargs)
        self.root.insertStrings.append((self, "STR_PARTYLINE"))
        self.input = TextInput(size_hint=(.8, .07), pos_hint={'x':.08, 'y':.024})
        self.output = Label(markup=True, font_name='font/Roboto-Regular.ttf', font_size='16dp', size_hint_y = None)
        self.SLayout = GridLayout(size_hint_y = None, cols=1, spacing=0)
        self.SLayout.bind(minimum_height=self.SLayout.setter('height'))
        self.scroll = ScrollView(size_hint=(1,.9), pos_hint={'center_x': .58, 'y': .125}, scroll_timeout=10000)
        self.scroll.do_scroll_x = False
        self.scroll.add_widget(self.SLayout)
        self.SLayout.add_widget(self.output)
        self.layout = RelativeLayout(size_hint=(.75, .83), pos_hint={'center_x': .437, 'y': .02})
        self.send = DelButton(color=(1,1,1,0), text='SEND', size_hint=(None, .1), pos_hint={'x':.88, 'y':.022}, background_normal='crop/icons/send.png', background_down='crop/icons/send.png')
        self.send.bind(on_press=self.sendMsg)
        self.input.bind(focus=self.on_focus)
        self.layout.content.add_widget(self.scroll)
        self.layout.content.add_widget(self.input)
        self.layout.content.add_widget(self.send)
        self.add_widget(self.layout)
        if self.root.onAndroid():
            self.LayouFocusOn = Animation(size_hint_y=.5, pos_hint={'center_x': .437, 'y': .38}, duration=.2)
            self.LayouFocusOut = Animation(size_hint_y=.83, pos_hint={'center_x': .437, 'y': .02}, duration=.2)
    
    def on_pre_enter(self, *args):
        # Voláno těsně před zobrazením obrazovky
        self.output.text_size = (self.root.root.size[0]*0.75, None)
        
    def sendMsg(self, instance):
        # Odeslat zprávu do chatu
        if len(self.input.text) > 0:
            out = "pline "+str(self.root.id)+" "+self.input.text.replace("\n", " ")
            self.root.send_message(out)
            self.root.print_message("{0}\xff".format(out))
            self.input.text = ""
    def on_focus(self, instance, value):
        # Při označení vstupního pole
        if self.root.onAndroid():
            if value:
                self.LayouFocusOn.start(self.layout)
            else:
                self.LayouFocusOut.start(self.layout)
    
    def prev(self):
        # Metoda pro návrat na předchozí obrazovku
        if self.input.focus:
            self.input.focus = False
        self.root.sm.transition = SlideTransition(direction="left")
        self.root.sm.current = 'GameScreen'

# Obrazovka se statistikami ze serveru
class StatsScreen(SideScreen):
    def __init__(self, **kwargs):   # inicializace
        super(StatsScreen, self).__init__(**kwargs)
        self.root.insertStrings.append((self, "STR_STATS"))
        self.stats = BoxLayout(orientation='vertical', size_hint=(.77, .83), pos_hint={'center_x': .5, 'center_y': .49})
        self.title = BoxLayout(orientation='horizontal')
        self.title.add_widget(Label(font_name='font/Roboto-Bold.ttf', text=''))
        self.title.add_widget(Label(font_name='font/Roboto-Bold.ttf', text=''))
        self.title.add_widget(Label(font_name='font/Roboto-Bold.ttf', text=''))
        self.stats.add_widget(self.title)
        self.add_widget(self.stats)
        self.root.insertStrings.append((self.title.children[2], "STR_TYPE"))
        self.root.insertStrings.append((self.title.children[1], "STR_NAME"))
        self.root.insertStrings.append((self.title.children[0], "STR_SCORE"))
    
    def prev(self):
        # Metoda pro návrat na předchozí obrazovku
        self.root.sm.transition = SlideTransition(direction="left")
        self.root.sm.current = 'PartylineScreen'

# Obrázek v 'Action baru' (ikona aplikace nahoře)
class ActionBarImg(Image):
    def __init__(self, **kwargs):
        self.register_event_type('on_press')
        super(ActionBarImg, self).__init__(**kwargs)
    
    def on_touch_down(self, touch):
        # Při stisku na obrázek vytvoří událost
        if self.collide_point(touch.x, touch.y):
            self.dispatch('on_press')
    
    def on_press(self):
        # Událost on_press
        pass

# Obrazovka s výběrem jazyka
class LanguageScreen(Screen):
    separator_color = ListProperty([47 / 255., 167 / 255., 212 / 255., 1.])
    separator_height = NumericProperty('2dp')
    def __init__(self, **kwargs):   # inicializace
        super(LanguageScreen, self).__init__(**kwargs)
        self.root = kwargs['root']
    
    def setLang(self, lang):
        # Voláno po kliknutí na příslušný jazyk, import řetězců
        if self.root.Cfg:
            self.root.sm.transition = SlideTransition(direction="right")
        self.root.makeCfg(lang)
        self.root.doStrInsert()
        self.manager.current = self.manager.next()
    
    def prev(self):
        pass

# Obrazovka hlavního menu
class MainMenuScreen(Screen):
    STR_CONNECT = StringProperty('')
    STR_BOOKMARKS = StringProperty('')
    STR_SETTINGS = StringProperty('')
    STR_DONATE = StringProperty('')
    STR_TUTORIAL = StringProperty('')
    def __init__(self, **kwargs): # inicializace
        super(MainMenuScreen, self).__init__(**kwargs)
        self.root = kwargs['root']
        self.root.insertStrings.append((self, ))
    
    def connect(self):
        # Přesun na obrazovku připojení k serveru
        self.root.sm.transition = SlideTransition(direction="left")
        self.root.sm.current = 'ConnectScreen'
        
    def bookmarks(self):
        # přesun na obrazovku se záložkami
        self.root.sm.transition = SlideTransition(direction="left")
        self.root.sm.current = 'BookmarksScreen'
    
    def settings(self):
        # přesun na obrazovku s nastavením
        self.root.sm.transition = SlideTransition(direction="left")
        self.root.sm.current = 'SettingsScreen'
        
    def donate(self):
        # Stisk tlačítka podpořit vývojáře
        # Na Androidu otevře webový prohlížeč s URL
        # Na jiných platformách vytiskne odkaz do konzole
        if self.root.Cfg[0] == "cs":
            lc = "CZ"
            cur = "CZK"
        else:
            lc = "US"
            cur = "USD"
        if self.root.onAndroid():
            android.open_url("https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=6XKAJN3DGBGUW&lc={0}&item_name=Mobile%20TetriNET&currency_code={1}&bn=PP%2dDonationsBF%3abtn_donate_LG%2egif%3aNonHosted".format(lc, cur))
        print "https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=6XKAJN3DGBGUW&lc={0}&item_name=Mobile%20TetriNET&currency_code={1}&bn=PP%2dDonationsBF%3abtn_donate_LG%2egif%3aNonHosted".format(lc, cur)
    
    def prev(self):
        pass
    
    def tutorial(self):
        # Přesun na obrazovku s tutorialem
        self.root.sm.transition = SlideTransition(direction="left")
        self.root.sm.current = 'TutorialMove'

# Obrazovka s 'Action barem'
class ActionBarScreen(Screen):
    separator_color = ListProperty([47 / 255., 167 / 255., 212 / 255., 1.])
    separator_height = NumericProperty('2dp')
    titleText = StringProperty('')
    
    def prev(self):
        # Metoda pro návrat na předchozí obrazovku
        self.root.sm.transition = SlideTransition(direction="right")
        self.root.sm.current = 'MainMenuScreen'

# Obrazovka s připojením k serveru
class ConnectScreen(ActionBarScreen):
    STR_SERVER = StringProperty()
    STR_TETRIFAST = StringProperty()
    STR_ORIGINAL = StringProperty()
    STR_CONNECTPOPUP = StringProperty()
    STR_CONNECT = StringProperty()
    STR_NICKNAME = StringProperty()
    STR_TEAM = StringProperty()
    STR_ADD_TO_BOOKMARKS = StringProperty()
    server = ListProperty(['', '', ''])
    nickname = StringProperty()
    team = StringProperty()
    def __init__(self, **kwargs):   # inicializace
        self.root = kwargs['root']
        self.root.insertStrings.append((self, ))
        super(ConnectScreen, self).__init__(**kwargs)
    
    def on_pre_enter(self, *args):
        # Před vstupem na obrazovku načte data z konfiguračního souboru
        cfg = list(self.root.Cfg[3])
        if len(cfg) == 3:
            self.server = cfg
        self.root.addBookmark = False
    
    def connect(self, nameInput, teamInput, serverInput, original, tetrifast):
        # Připojuje k serveru, kontrola vstupů
        if (len(nameInput.text) > 0) and (len(serverInput.text) > 0):
            self.root.nickname = nameInput.text.strip()
            self.root.team = teamInput.text.strip()
            self.root.server = serverInput.text.strip()
            self.root.tetrifast = tetrifast.active
            if self.root.onAndroid():
                android.hide_keyboard()
                self.root.vibrate(0.05)
            self.root.Cfg[1] = self.root.nickname
            self.root.Cfg[2] = self.root.team
            if self.bookmark.active:
                self.root.addBookmark = True
            self.root.refreshCfg()
            self.root.connect_to_server()
            self.root.overlay.setSize()
            self.root.sm.current = 'GameScreen'
            self.root.sm.transition = SlideTransition(direction="left")
        else:
            Toast(text='Name or server missing', timeout=2).open()
    
    def keyboardShow(self):
        # Zobraz klávesnici na Androidu
        if self.root.onAndroid():
            android.show_keyboard()

# Obrazovka s nastavením
class SettingsScreen(ActionBarScreen):
    STR_SETTINGS = StringProperty()
    STR_RESET_DEFAULTS = StringProperty()
    STR_RESET_DEFAULTS_HELP = StringProperty()
    STR_RESET = StringProperty()
    STR_LANGUAGE_CHANGE = StringProperty()
    def __init__(self, **kwargs):   # inicializace
        self.root = kwargs['root']
        self.root.insertStrings.append((self, ))
        super(SettingsScreen, self).__init__(**kwargs)
        self.dropdown = DropDown()
        for index in LANGUAGES.itervalues():
            btn = Button(text=index, size_hint_y=None, height=44, font_size='24dp', font_name="font/Roboto-Regular.ttf")
            btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
            self.dropdown.add_widget(btn)
        self.language.bind(on_release=self.dropdown.open)
        self.dropdown.bind(on_select=lambda instance, x: setattr(self.language, 'text', x))
        self.language.bind(text=self.change)
    
    def reset_defaults(self, *args):
        # Výmaz konfiguračního souboru po stisku tlačítka reset
        self.root.Cfg = ['' for y in range(4)]
        self.root.refreshCfg()
    
    def on_pre_enter(self, *args):
        # Před vstupem na obrazovku načte jazyky
        self.language.text = LANGUAGES.get(self.root.Cfg[0])
    
    def change(self, *args):
        # Změní jazyk, znovu načte řetězce
        self.root.Cfg[0] = [y[0] for y in LANGUAGES.items() if y[1] == self.language.text][0]
        self.root.refreshCfg()
        self.root.doStrInsert()

# Obrazovka oblíbených serverů
class BookmarksScreen(ActionBarScreen):
    STR_BOOKMARKS = StringProperty()
    STR_NO_BOOKMARKS = StringProperty()
    STR_MOD = StringProperty()
    STR_VERSION = StringProperty()
    STR_SERVER = StringProperty()
    def __init__(self, **kwargs):   # inicializace
        self.root = kwargs['root']
        self.root.insertStrings.append((self, ))
        super(BookmarksScreen, self).__init__(**kwargs)
        self.layout = GridLayout(cols=1, size_hint_y=None, size_hint_x = 1, spacing=10)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.scrollview.add_widget(self.layout)
    
    def on_pre_enter(self, *args):
        # Před vstupem na obrazovku načte seznam oblíbených serverů
        if len(self.layout.children) == 0:
            bookmarks = self.root.Cfg[-1]
            if len(bookmarks) == 0:
                self.layout.add_widget(Label(text=self.STR_NO_BOOKMARKS, font_name='font/Roboto-Regular.ttf', font_size='18dp', size_hint_y = None, text_size=(self.width*3, None)))
            else:
                head = BoxLayout(size_hint=(1,None), height=50)
                head.add_widget(Label(text=self.STR_SERVER, font_name='font/Roboto-Bold.ttf', size_hint=(None,1), font_size="20dp", width = self.width*1.9, text_size=(self.width*1.9, None)))
                head.add_widget(Label(text=self.STR_MOD, font_name='font/Roboto-Bold.ttf', size_hint=(1,1), font_size="15dp", width = self.width, text_size=(self.width, None)))
                head.add_widget(DelButton(opacity=0, size_hint=(None, 1)))
                self.layout.add_widget(head)
                for y, server in enumerate(bookmarks):
                    srvr = Bookmark(size_hint=(1,None), height = 50)
                    for i, cell in enumerate(server):
                        if i == 0:
                            lbl = Label(text="[ref={0}]{1}[/ref]".format(y,cell), markup=True, font_name='font/Roboto-Regular.ttf', size_hint=(None,1), font_size="20dp", text_size=(None, None))
                            lbl.bind(on_ref_press=self.connectBookmark)
                            srvr.add_widget(lbl)
                        elif i == 1:
                            pass
                        elif i == 2:
                            lbl = Label(text="[ref={0}]{1}[/ref]".format(y,cell), markup=True, font_name='font/Roboto-Regular.ttf', size_hint=(1,1), font_size="20dp")
                            lbl.bind(on_ref_press=self.connectBookmark)
                            srvr.add_widget(lbl)
                    btn = DelButton(OBJ=srvr, ID=y, background_normal="crop/delete.png", background_down="crop/delete.png",size_hint=(None, 1))
                    btn.bind(on_press=self.removeBookmark)
                    srvr.add_widget(btn)
                    self.layout.add_widget(srvr)
    
    def removeBookmark(self, *args):
        # Odstranění serveru z oblíbených
        print args[0].ID
        self.layout.remove_widget(args[0].OBJ)
        self.root.Cfg[-1].pop(args[0].ID)
        self.root.refreshCfg()
        
    def connectBookmark(self, instance, value):
        # Připojení k serveru ze záložky
        self.root.server = self.root.Cfg[-1][int(value)][0]
        self.root.version = self.root.Cfg[-1][int(value)][1]
        if self.root.Cfg[-1][int(value)][2] == 'classic':
            self.root.tetrifast = False
        else:
            self.root.tetrifast = True
        self.root.connect_to_server()
        self.root.overlay.setSize()
        self.root.sm.current = "GameScreen"
        if self.root.onAndroid():
            self.root.vibrate(0.05)

# Obrazovka s tutorialem
class TutorialScreen(Screen):
    FRAMES = ListProperty()
    CURRENT_FRAME = NumericProperty(0)
    NAME = StringProperty()
    STR_NEXT = StringProperty()
    STR_PREV = StringProperty()
    def __init__(self, **kwargs):   # inicializace
        self.framesCount = kwargs['frames']
        self.dir = kwargs['directory']
        self.root = kwargs['root']
        for i in range(1, self.framesCount+1):
            self.FRAMES.append(Image(source='crop/tutorial/{0}/{1}.jpg'.format(self.dir, i)).texture)
        super(TutorialScreen, self).__init__(**kwargs)
    
    def nextFrame(self, *args):
        # Přesune na další snímek z tutorialu
        if self.framesCount-1-self.CURRENT_FRAME <= 0:
            self.CURRENT_FRAME = 0
        else:
            self.CURRENT_FRAME += 1

# Tutorial - pohyb bloků
class TutorialMove(TutorialScreen):
    STR_TUTORIAL_MOVE = StringProperty()
    def __init__(self, **kwargs):
        super(TutorialMove, self).__init__(**kwargs)
        self.root.insertStrings.append((self, ))
        self.prev_button.bind(on_press=self.prev)
        self.next_button.bind(on_press=self.nextScreen)
        self.bind(STR_TUTORIAL_MOVE=self.refreshName)
    
    def prev(self, *args):
        # Metoda pro návrat na předchozí obrazovku
        self.root.sm.transition = SlideTransition(direction="right")
        self.root.sm.current = 'MainMenuScreen'
        Clock.unschedule(self.nextFrame)
    
    def nextScreen(self, *args):
        # Přechod na další obrazovku tutorialu
        self.root.sm.transition = SlideTransition(direction="left")
        self.root.sm.current = self.root.sm.next()
        Clock.unschedule(self.nextFrame)
        
    def refreshName(self, *args):
        # Nastavení nadpisu
        self.NAME = self.STR_TUTORIAL_MOVE
    
    def on_pre_enter(self, *args):
        # Spuštění obrázkové prezentace
        Clock.schedule_interval(self.nextFrame, 1)

# Tutorial - spuštění bloku
class TutorialDrop(TutorialScreen):
    STR_TUTORIAL_DROP = StringProperty()
    def __init__(self, **kwargs):
        super(TutorialDrop, self).__init__(**kwargs)
        self.root.insertStrings.append((self, ))
        self.prev_button.bind(on_press=self.prev)
        self.next_button.bind(on_press=self.nextScreen)
        self.bind(STR_TUTORIAL_DROP=self.refreshName)
    
    def prev(self, *args):
        self.root.sm.transition = SlideTransition(direction="right")
        self.root.sm.current = 'TutorialMove'
        Clock.unschedule(self.nextFrame)
    
    def nextScreen(self, *args):
        self.root.sm.transition = SlideTransition(direction="left")
        self.root.sm.current = self.root.sm.next()
        Clock.unschedule(self.nextFrame)
    
    def refreshName(self, *args):
        self.NAME = self.STR_TUTORIAL_DROP
    
    def on_pre_enter(self, *args):
        Clock.schedule_interval(self.nextFrame, 1)

# Tutorial - speciální kostky
class TutorialSpecial(TutorialScreen):
    STR_TUTORIAL_SPECIAL = StringProperty()
    def __init__(self, **kwargs):
        super(TutorialSpecial, self).__init__(**kwargs)
        self.root.insertStrings.append((self, ))
        self.prev_button.bind(on_press=self.prev)
        self.next_button.bind(on_press=self.nextScreen)
        self.bind(STR_TUTORIAL_SPECIAL=self.refreshName)
        self.nameLabel.font_size = "26dp"
    
    def prev(self, *args):
        self.root.sm.transition = SlideTransition(direction="right")
        self.root.sm.current = 'TutorialDrop'
        Clock.unschedule(self.nextFrame)
    
    def nextScreen(self, *args):
        self.root.sm.transition = SlideTransition(direction="left")
        self.root.sm.current = self.root.sm.next()
        Clock.unschedule(self.nextFrame)
    
    def refreshName(self, *args):
        self.NAME = self.STR_TUTORIAL_SPECIAL
        
    def on_pre_enter(self, *args):
        Clock.schedule_interval(self.nextFrame, 1)

# Tutorial - ovládání
class TutorialNavigate(TutorialScreen):
    STR_TUTORIAL_NAVIGATE = StringProperty()
    def __init__(self, **kwargs):
        super(TutorialNavigate, self).__init__(**kwargs)
        self.root.insertStrings.append((self, ))
        self.prev_button.bind(on_press=self.prev)
        self.next_button.bind(on_press=self.nextScreen)
        self.bind(STR_TUTORIAL_NAVIGATE=self.refreshName)
    
    def prev(self, *args):
        self.root.sm.transition = SlideTransition(direction="right")
        self.root.sm.current = 'TutorialSpecial'
        Clock.unschedule(self.nextFrame)
    
    def nextScreen(self, *args):
        self.root.sm.transition = SlideTransition(direction="left")
        self.root.sm.current = self.root.sm.next()
        Clock.unschedule(self.nextFrame)
    
    def refreshName(self, *args):
        self.NAME = self.STR_TUTORIAL_NAVIGATE

    def on_pre_enter(self, *args):
        Clock.schedule_interval(self.nextFrame, 1)

# Tutorial - zobrazení hráčů
class TutorialPlayers(TutorialScreen):
    STR_TUTORIAL_PLAYERS = StringProperty()
    def __init__(self, **kwargs):
        super(TutorialPlayers, self).__init__(**kwargs)
        self.root.insertStrings.append((self, ))
        self.prev_button.bind(on_press=self.prev)
        self.next_button.bind(on_press=self.nextScreen)
        self.bind(STR_TUTORIAL_PLAYERS=self.refreshName)
    
    def prev(self, *args):
        self.root.sm.transition = SlideTransition(direction="right")
        self.root.sm.current = 'TutorialNavigate'
        Clock.unschedule(self.nextFrame)
    
    def nextScreen(self, *args):
        self.root.sm.transition = SlideTransition(direction="left")
        self.root.sm.current = 'MainMenuScreen'
        Clock.unschedule(self.nextFrame)
    
    def refreshName(self, *args):
        self.NAME = self.STR_TUTORIAL_PLAYERS

    def on_pre_enter(self, *args):
        Clock.schedule_interval(self.nextFrame, 1)