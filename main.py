from kivy.app import App
from kivy.core.window import Window
from kivy.core.image import Image
from kivy.properties import NumericProperty, ReferenceListProperty, StringProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.graphics import Line, Color, texture, Rotate
from kivy.graphics.transformation import Matrix
from random import random, choice
from math import sqrt
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
import os
import sys

class Container(Widget):
    sz = Window.height * 0.17
    containFlask = None
    texture = None

    def __init__(self, **kwargs):
        super(Container, self).__init__(**kwargs)            
        self.texture = Image('wood.jpg').texture

    def on_touch_down(self, touch):
        center = self.center_x, self.center_y
        if max(abs(touch.x - self.center_x), abs(touch.y - self.center_y)) > self.sz / 2:
            return           

        if game.tutor.user_guide_stage < 1 or game.tutor.max_user_guide_stage > game.tutor.user_guide_stage > 6:
            return

        if game.stop:
            return

        if (game.tutor.user_guide_stage == 2 or game.tutor.user_guide_stage == 6) and self.containFlask != None:
            return

        if game.tutor.user_guide_stage == 1:
            game.tutor.user_guide_stage = 2

        if game.mixer.state == 0:
            if len(game.Flasks) == 0:
                return
            dx = self.center_x - game.Flasks[0].center_x
            dy = self.center_y - game.Flasks[0].center_y
            velocity = Window.height * 0.01
            game.Flasks[0].go_to(self, center[0], center[1] - self.sz * 0.3, velocity, self.sz / 4)
            game.FlyingFlasks.append(game.Flasks[0])
            del game.Flasks[0]
        else:
            if self.containFlask != None:
                self.containFlask.go_to(game.mixer, game.mixer.center_x - game.mixer.sz * 0.75 + game.mixer.sz * 1.5 * game.mixer.count, game.mixer.center_y - game.mixer.sz * 0.4, Window.height * 0.015, float("inf"))
                self.containFlask.returnDestination = center[0], center[1] - self.sz * 0.3
                self.containFlask.returnTo = self
                game.mixer.add_flask(self.containFlask)
                game.FlyingFlasks.append(self.containFlask)
                self.containFlask = None				


class Wheel(Widget):
    left_corner_x = NumericProperty(0)
    bottom_height = Window.height * 0.1    
    v = Vector(0, Window.height * 0.05)
    angle = 0

class MyProgressBar(Widget):
    completed_lvl = NumericProperty(0)
    needed_lvl = NumericProperty(0)
    progress = StringProperty("")

class Encyclopaedia:
    Liquids = []
    LiquidsByStage = [["H[sub]2[/sub]", "Cl[sub]2[/sub]"]]
    Colors = {}
    Type = []
    Reactions = {}
    Tutorial = [""]
    Goals = [""]

    stage_requirements_subst = [["HCl"]]
    stage_requirements_cnt = [1]

    max_level = 0

    def preprocess(self, name):        
        res = ""
        for x in name:
            if '0' <= x <= '9':
                res += '[sub]' + x + '[/sub]'
            else:
                res += x        
        return res.strip()

    def init(self):        
        with open(os.path.dirname(os.path.realpath(sys.argv[0])) + "\data\data_substances.txt", "r") as inp:
            data = inp.readlines()
            while len(data) % 3 != 0:
                data.append((1.0, 1.0, 1.0))
            for i in range(0, len(data), 3):
                name = self.preprocess(data[i])
                self.Liquids.append(name)
                self.Colors[name] = map(float, data[i + 1].split())
                self.Type.append(data[i + 2])

        with open(os.path.dirname(os.path.realpath(sys.argv[0])) + "\data\data_reactions.txt", "r") as inp:        
            data = inp.readlines()
            while len(data) % 4 != 0:
                data.append("")
            for i in range(0, len(data), 4):
                name1 = self.preprocess(data[i])
                name2 = self.preprocess(data[i + 1])
                if name1 > name2:
                    name1, name2 = name2, name1
                name_res = map(self.preprocess, data[i + 2].split())
                self.Reactions[name1 + "+" + name2] = name_res

        with open(os.path.dirname(os.path.realpath(sys.argv[0])) + "\data\levels\\goals.txt", "r") as inp:        
            data = inp.readlines()
            self.max_level = len(data)
            for i in range(len(data)):
                self.Goals.append(data[i])

        with open(os.path.dirname(os.path.realpath(sys.argv[0])) + "\data\levels\\tutorials.txt", "r") as inp:        
            data = inp.readlines()
            while len(data) < self.max_level:
                data.append(" ")    
            for i in range(len(data)):
                line = data[i][0]
                for j in range(1, len(data[i])):
                    if data[i][j] == '\\':
                        line += '\n';
                    else:
                        line += data[i][j];
                self.Tutorial.append(self.preprocess(line))

        with open(os.path.dirname(os.path.realpath(sys.argv[0])) + "\data\levels\\substances.txt", "r") as inp:        
            data = inp.readlines()    
            while len(data) < self.max_level:
                data.append(" ")    
            for i in range(len(data)):
                self.LiquidsByStage.append(map(self.preprocess, data[i].split()))

        with open(os.path.dirname(os.path.realpath(sys.argv[0])) + "\data\levels\stage_requirements.txt", "r") as inp:        
            data = inp.readlines()
            while len(data) / 3 < self.max_level:
                data.append("1")
            for i in range(0, len(data), 3):
                self.stage_requirements_cnt.append(int(data[i]))
                self.stage_requirements_subst.append(map(self.preprocess, data[i + 1].split()))

        self.stage_requirements_cnt.append(len(self.Liquids))
        self.stage_requirements_subst.append(self.Liquids)


def sqr(a):
    return a * a

class Flask(Widget):
    angle = NumericProperty(0)
    color_red = NumericProperty(0)
    color_green = NumericProperty(0)
    color_blue = NumericProperty(0)
    liquid_color = ReferenceListProperty(color_red, color_green, color_blue)
    liquid_name = StringProperty("")
    sz = Window.height * 0.15    
    flask_velocity = Window.height * 0.000875 * 1.5;
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)       
    returnDestination = None
    inMixer = False

    def move(self):        
        self.pos = Vector(*self.velocity) + self.pos

    def is_near(self, destination, eps):        
        if sqr(self.center_x - destination[0]) + sqr(self.center_y - destination[1]) < sqr(eps):
            return True
        return False

    def go_to(self, object, x, y, velocity, eps):
        dx = x - self.center_x
        dy = y - self.center_y
        self.velocity_x = (dx / max(1, abs(dx)) * abs(dx / (abs(dx) + abs(dy)))) * velocity
        self.velocity_y = (dy / max(1, abs(dy)) * abs(dy / (abs(dx) + abs(dy)))) * velocity
        self.destination = x, y
        self.eps = eps
        self.approachingTo = object


class Arrow(Widget):
    start_x = NumericProperty(0)
    start_y = NumericProperty(0)
    end_x = NumericProperty(0)
    end_y = NumericProperty(0)
    hor_line = NumericProperty(0)
    text = StringProperty("")
    text_tab = NumericProperty(0)

    def indicate(self, x, y):
        self.end_x = x
        self.end_y = y

    def __init__(self, **kwargs):
        super(Arrow, self).__init__(**kwargs)            
        self.hor_line = Window.width * 0.1           
        self.start_x = Window.width / 2 - Window.width * 0.05
        self.start_y = Window.height / 2    

class Mixer(Widget):
    # state = 1 -> choosing flasks
    state = 0 

    step = 0

    count = 0
    chosen = []
    received = 0
    sentBack = 0
    sz = Window.height * 0.15

    def __init__(self, **kwargs):
        super(Mixer, self).__init__(**kwargs)            
        self.center_x = Window.width * 0.8
        self.center_y = Window.height * 0.6           

    def add_flask(self, flask):
        if self.count == 2:
            return

        self.count += 1
        self.chosen.append(flask)
        
    def on_touch_down(self, touch):
        if game.tutor.user_guide_stage < 3 or game.tutor.max_user_guide_stage > game.tutor.user_guide_stage > 3:
            return

        center = self.center_x, self.center_y
        if abs(touch.x - self.center_x) > self.sz / 2 or abs(touch.y - self.center_y) > self.sz / 2:
            return           

        self.state = 1 - self.state
        if game.tutor.user_guide_stage == 3:
            game.tutor.user_guide_stage += 1

        if game.mix_on == "Mixing mode: Off":
            game.mix_on = "Mixing mode: On"
        else:
            game.mix_on = "Mixing mode: Off"

    def animate_mix(self, arg2):
        self.step += 1
        ANG = 50.0
        self.chosen[0].angle -= ANG * self.sign / game.FPS
        self.chosen[0].center_y += Window.height * 0.0005 * self.sign
        self.chosen[1].angle += ANG * self.sign / game.FPS
        self.chosen[1].center_y += Window.height * 0.0005 * self.sign
        if self.step == game.FPS:
            if self.sign == 1:
                Clock.schedule_once(self.react_part2, 1.0 / game.FPS)
            else:
            	Clock.schedule_once(self.react_part3, 1.0 / game.FPS)
        else:
            Clock.schedule_once(self.animate_mix, 1.0 / game.FPS)

    def react(self):
        self.step = 0
        self.sign = 1
        if game.tutor.user_guide_stage == 4:
            game.tutor.user_guide_stage += 1

        Clock.schedule_once(self.animate_mix, 1.0 / game.FPS)

    def react_part2(self, arg2):
        reagents = "+".join(sorted((self.chosen[0].liquid_name, self.chosen[1].liquid_name)))
        if reagents in Encyclopaedia.Reactions:
            for new_liquid in Encyclopaedia.Reactions[reagents]:
                if new_liquid not in game.received:
                    game.received.append(new_liquid)
                    game.adjust_score(9)
                else:
                    game.adjust_score(3)
                game.flask_appearance(new_liquid)
                if game.tutor.user_guide_stage == 5:
                    game.tutor.user_guide_stage += 1
                game.Flasks = game.Flasks[-1:] + game.Flasks[:-1]
        else:
            game.adjust_score(-3)
        self.step = 0
        self.sign = -1
        Clock.schedule_once(self.animate_mix, 1.0 / game.FPS)

    def react_part3(self, arg2):
        for flask in self.chosen:
            game.FlyingFlasks.append(flask)
            flask.go_to(flask.returnTo, \
                        flask.returnDestination[0], \
                        flask.returnDestination[1], \
                        Window.height * 0.015, \
                        flask.returnTo.sz / 4)
            flask.destination = flask.returnDestination
            flask.inMixer = False
        
        self.sentBack = 0
        self.received = 0
        self.count = 0
        self.chosen = []
        self.state = 0
        game.mix_on = "Mixing mode: Off"

        if game.tutor.game_stage > 0:
            game.tutor.check_stage_completion()


class Tutor(Widget):
    text = StringProperty("")
    next_button_text = StringProperty("")
    x_left = NumericProperty(0)
    y_left = NumericProperty(0)
    wnd_height = NumericProperty(0)
    wnd_width = NumericProperty(0)
    halign = StringProperty("left")
    intro_text = ["Have| you| ever| thought||\nthat studying chemistry|\nmay bring [b]you[/b]||\n[size=72][color=#ff0000]F[/color]|[color=#00ff00]U[/color]|[color=#0000ff]N[/color]|?[/size]|||",
                   "Anyway,\n||you are\n|WELCOME\n|to the app that\n|will\n|help you to learn\n|and\n|will make you [b][i]enjoy[/i][/b] chemistry|||||||",
                   "Best regards,\nIlia Malinovskii\nSaint Petersburg\nMay, 2014||||||"]
    sentence = 0
    word = 0
    shown = True
    arrow_added = False

    user_guide_stage = -2
    max_user_guide_stage = 13

    iterations = 0

    game_stage = -1

    text_size = NumericProperty(24)

    last_sheduled = 0

    state = ""

    def intro(self, second):
        if not self.shown:
            return
        self.word += 1
        if self.sentence == 2:
            self.halign = "right"
        self.next_button_text = "Skip"     
        self.text = "".join(self.intro_text[self.sentence].split("|")[:self.word])
        if self.word == len(self.intro_text[self.sentence].split("|")):
            self.word = 0
            self.sentence += 1
            if self.sentence == len(self.intro_text):
                self.hide()             
                game.into_the_game()                
                self.user_guide_stage += 1
                return
        Clock.schedule_once(self.intro, 0.5)

    def user_guide(self, second):
        if self.user_guide_stage == self.max_user_guide_stage:
            game.remove_widget(game.arrow)           
            self.wnd_width = Window.width * 0.95
            self.x_left = Window.width * 0.05
            self.check_stage_completion() 
            self.user_guide_stage = 100
            return   

        if self.user_guide_stage == -1:
            if len(game.Flasks) and game.Flasks[0].center_x > 0:
                if not self.arrow_added:
                    game.arrow.text = "This is a flask with substance"
                    game.add_widget(game.arrow)
                    self.arrow_added = True
                    game.arrow.text_tab = game.arrow.hor_line / 2
                game.arrow.indicate(game.Flasks[0].center_x, game.Flasks[0].center_y + game.Flasks[0].sz)        
                self.user_guide_stage += 1                        

        if self.user_guide_stage == 0:
            self.iterations += 1
            game.arrow.indicate(game.Flasks[0].center_x, game.Flasks[0].center_y + game.Flasks[0].sz)
            if self.iterations == game.FPS:
                self.iterations = 0
                self.user_guide_stage += 1                        

        if self.user_guide_stage == 1:
            if len(game.Containers):
                game.arrow.text = "Touch the shelf to place the first flask from the conveyor there"
                game.arrow.indicate(game.Containers[0].center_x, game.Containers[0].center_y)        
                game.arrow.text_tab = - game.arrow.hor_line / 2                

        if self.user_guide_stage == 2:
            game.arrow.text = "Great! Now add another flask to another shelf"
            game.arrow.indicate(game.arrow.start_x, game.arrow.start_y)        

        if self.user_guide_stage == 3:
            game.arrow.text = "Excellent! Now tap here to enable the mixing mode"
            game.arrow.indicate(game.mixer.center_x, game.mixer.center_y)        

        if self.user_guide_stage == 4:
            game.arrow.text = "Click on the shelves containing flasks to add these flasks to the mixer"
            for cont in game.Containers:
                if cont.containFlask != None:    
                    game.arrow.indicate(cont.center_x, cont.center_y)        
                    break

        if self.user_guide_stage == 5:
            game.arrow.text = "Reaction begins..."
            game.arrow.indicate(game.mixer.center_x, game.mixer.center_y)        

        if self.user_guide_stage == 6:
            game.arrow.text = "Congratulations! You've just got new substance!\nTap any free shelf to place new flask there"
            game.arrow.indicate(game.mixer.center_x, game.mixer.center_y)                    

        if self.user_guide_stage == 7:
            game.arrow.text = "Some more info..."
            game.arrow.indicate(game.arrow.start_x, game.arrow.start_y)                    
            if self.last_sheduled < self.user_guide_stage:
                Clock.schedule_once(self.user_guide_inc, 1.0)
                self.last_sheduled = self.user_guide_stage

        if self.user_guide_stage == 8:
            game.arrow.text = "This is your current score"
            game.arrow.indicate(game.arrow.start_x, game.arrow.start_y)                    
            game.ScoreSize = 250
            game.ScoreColorRed = 1
            game.ScoreColorGreen = 0
            game.ScoreColorBlue = 0
            if self.last_sheduled < self.user_guide_stage:
                Clock.schedule_once(self.user_guide_inc, 1.0)
                self.last_sheduled = self.user_guide_stage

        if self.user_guide_stage == 9:
            game.arrow.text = "This is your current score"
            game.arrow.indicate(game.arrow.start_x, game.arrow.start_y)                    
            game.ScoreSize = 70
            game.ScoreColorRed = 1
            game.ScoreColorGreen = 1
            game.ScoreColorBlue = 1
            if self.last_sheduled < self.user_guide_stage:
                Clock.schedule_once(self.user_guide_inc, 1.0)
                self.last_sheduled = self.user_guide_stage

        if self.user_guide_stage == 10:
            game.arrow.text = "If you mix two substances\nthat don't react with each other,\nyou will lose 3 points. Just watch"
            if self.last_sheduled < self.user_guide_stage:                
                for cont in game.Containers:
                    if cont.containFlask != None and cont.containFlask.liquid_name == "HCl":    
                        center = cont.center_x, cont.center_y
                        game.arrow.indicate(cont.center_x, cont.center_y)        
                        cont.containFlask.go_to(game.mixer, game.mixer.center_x - game.mixer.sz * 0.75 + game.mixer.sz * 1.5 * game.mixer.count, game.mixer.center_y - game.mixer.sz * 0.4, Window.height * 0.015, float("inf"))
                        cont.containFlask.returnDestination = center[0], center[1] - cont.sz * 0.3
                        cont.containFlask.returnTo = cont        
                        game.mixer.add_flask(cont.containFlask)
                        game.FlyingFlasks.append(cont.containFlask)
                        cont.containFlask = None				
                        break
                for cont in game.Containers:
                    if cont.containFlask != None:    
                        center = cont.center_x, cont.center_y
                        game.arrow.indicate(cont.center_x, cont.center_y)        
                        cont.containFlask.go_to(game.mixer, game.mixer.center_x - game.mixer.sz * 0.75 + game.mixer.sz * 1.5 * game.mixer.count, game.mixer.center_y - game.mixer.sz * 0.4, Window.height * 0.015, float("inf"))
                        cont.containFlask.returnDestination = center[0], center[1] - cont.sz * 0.3
                        cont.containFlask.returnTo = cont        
                        game.mixer.add_flask(cont.containFlask)
                        game.FlyingFlasks.append(cont.containFlask)
                        cont.containFlask = None				
                        break
                self.last_sheduled = 10

        if self.user_guide_stage == 11:
            game.arrow.text = "If you mix two substances\nthat you already have mixed,\nyou will score 3 points. Just watch"
            if self.last_sheduled < self.user_guide_stage:                
                for cont in game.Containers:
                    if cont.containFlask != None and cont.containFlask.liquid_name != "HCl":    
                        center = cont.center_x, cont.center_y
                        game.arrow.indicate(cont.center_x, cont.center_y)        
                        cont.containFlask.go_to(game.mixer, game.mixer.center_x - game.mixer.sz * 0.75 + game.mixer.sz * 1.5 * game.mixer.count, game.mixer.center_y - game.mixer.sz * 0.4, Window.height * 0.015, float("inf"))
                        cont.containFlask.returnDestination = center[0], center[1] - cont.sz * 0.3
                        cont.containFlask.returnTo = cont        
                        game.mixer.add_flask(cont.containFlask)
                        game.FlyingFlasks.append(cont.containFlask)
                        cont.containFlask = None				
                        break
                for cont in game.Containers:
                    if cont.containFlask != None and cont.containFlask.liquid_name != "HCl":    
                        center = cont.center_x, cont.center_y
                        game.arrow.indicate(cont.center_x, cont.center_y)        
                        cont.containFlask.go_to(game.mixer, game.mixer.center_x - game.mixer.sz * 0.75 + game.mixer.sz * 1.5 * game.mixer.count, game.mixer.center_y - game.mixer.sz * 0.4, Window.height * 0.015, float("inf"))
                        cont.containFlask.returnDestination = center[0], center[1] - cont.sz * 0.3
                        cont.containFlask.returnTo = cont        
                        game.mixer.add_flask(cont.containFlask)
                        game.FlyingFlasks.append(cont.containFlask)
                        cont.containFlask = None				
                        break
                self.last_sheduled = 11

        if self.user_guide_stage == 12:
            game.arrow.text = "If you place the flask on the shelf\nthat already contains one\nyou will lose 1 point and 1 flask (previously contained there)"
            if self.last_sheduled < self.user_guide_stage:                
                for cont in game.Containers:
                    if cont.containFlask != None:    
                        dx = cont.center_x - game.Flasks[0].center_x
                        dy = cont.center_y - game.Flasks[0].center_y
                        velocity = Window.height * 0.01
                        game.Flasks[0].go_to(cont, cont.center_x, cont.center_y - cont.sz * 0.3, velocity, cont.sz / 4)
                        game.FlyingFlasks.append(game.Flasks[0])
                        del game.Flasks[0]
                    break
                self.last_sheduled = 12
                

        Clock.schedule_once(self.user_guide, 1.0 / game.FPS)

    def user_guide_inc(self, second):
        self.user_guide_stage += 1
        print self.user_guide_stage

    def check_stage_completion(self):
        if self.game_stage < 0:
            return
        if self.game_stage > game.max_level:
            return
        cnt = 0
        for x in game.enc.stage_requirements_subst[self.game_stage]:
            if x in game.received:
                cnt += 1
        game.progress_bar.completed_lvl = cnt
        game.progress_bar.needed_lvl = game.enc.stage_requirements_cnt[self.game_stage]
        game.progress_bar.progress = str(game.progress_bar.completed_lvl) + "/" + str(game.progress_bar.needed_lvl)        
        
        if cnt >= game.enc.stage_requirements_cnt[self.game_stage]:
            self.congratulations()
        
    def congratulations(self):
        game.start_stop()
        game.fly_upwards()
        self.game_stage += 1        	    
        self.state = "congratulations"
        self.shown = True
        game.add_widget(self)
        self.text = "Congratulations!!!\nYou have passed level " + str(self.game_stage)
        if self.game_stage <= game.max_level:
            self.next_button_text = "Read theory background\nfor the next stage"
        else:
            self.next_button_text = "Next"

    def theory_block(self):
        self.halign = "left"
        self.text_size = 14
        self.state = "theory"
        self.next_button_text = "Next stage..."
        if self.game_stage <= game.max_level:
            self.text = game.enc.Tutorial[self.game_stage]	    
        else:
            self.text_size = 16
            self.text = "You have passed all levels.\nFeel free to add your owns.\nJust consult [i]readme.txt[/i] to know how to do it.\nOr you may\ncontinue playing as long as you want\nand try to get all possible substances!"	                

    def next_stage(self):
        self.halign = "center"
        self.text_size = 24
        self.state = "next stage"
        self.next_button_text = "Resume practicing"
        self.text = game.enc.Goals[self.game_stage]	    
        game.progress_bar.completed_lvl = 0
        game.progress_bar.needed_lvl = game.enc.stage_requirements_cnt[self.game_stage]
        print game.progress_bar.needed_lvl
        game.progress_bar.progress = str(game.progress_bar.completed_lvl) + "/" + str(game.progress_bar.needed_lvl)


    def on_touch_down(self, touch):
        if not self.shown:
            return
        center = self.x_left + self.wnd_width / 2, self.y_left + self.wnd_height * 1.15
        if abs(touch.x - center[0]) > self.wnd_width / 4 or abs(touch.y - center[1]) > self.height * 0.2:
            return           
        
        if self.user_guide_stage == -2:
            game.into_the_game()
            self.hide()
            self.user_guide_stage += 1
        else:
            if self.state == "congratulations":
                self.theory_block()
            elif self.state == "theory":
                if self.game_stage <= game.max_level:
                    self.next_stage()
                else:
                    self.hide()
                    self.state = ""
                    game.start_stop()
            elif self.state == "next stage":
                self.hide()
                self.state = ""
                game.start_stop()

    def hide(self):                
        self.parent.remove_widget(self)        
        self.shown = False

    def __init__(self, **kwargs):
        super(Tutor, self).__init__(**kwargs)            
        self.wnd_width = Window.width * 0.6
        self.wnd_height = Window.height * 0.6
        self.x_left = Window.width * 0.2
        self.y_left = Window.height * 0.2
        self.text = ""
        self.halign = "center"
        Clock.schedule_once(self.intro, 0.01)

class ChemistryWithFunGame(Widget):

    Flasks = []
    FlyingFlasks = []
    FlyingFlasksFinish = []
    AvailableFlasks = []
    FlasksPerSec = 0

    Score = 0
    ScoreStr = StringProperty("")
    ScoreAdd = StringProperty("")
    ScoreSize = NumericProperty(70)
    ScoreColorRed = NumericProperty(1)
    ScoreColorBlue = NumericProperty(1)
    ScoreColorGreen = NumericProperty(1)

    color_red = NumericProperty(0)
    color_green = NumericProperty(0)

    Containers = []
    secs = 0
    conv = []   

    stop = False

    arrow = None

    received = []

    mix_on = StringProperty("")
    in_hidden_mixer = ""

    max_level = 0

    def __init__(self, **kwargs):
        super(ChemistryWithFunGame, self).__init__(**kwargs)            

        self.FlasksPerSec = 1

        self.tutor = Tutor()
        self.add_widget(self.tutor)

        self.enc = Encyclopaedia()
        self.enc.init()
        self.max_level = self.enc.max_level

        self.FPS = 120

        self.flask_entrance()

        Clock.schedule_interval(self.update, 1.0 / self.FPS)

    def into_the_game(self):
        self.tutor.game_stage += 1
        self.mix_on = "Mixing mode: Off"
        self.ScoreStr = str(self.Score)
        self.needed_lvl = 1

        for i in range(4):            
            new_container = Container()            
            new_container.pos = Window.width * 0.1 + (Window.height * 0.2) * i, Window.height * 0.73
            new_container.touched_down = False            
            self.add_container(new_container)

        Flask.flask_velocity /= 1.5
        self.fly_upwards()

        self.mixer = Mixer()
        
        self.progress_bar = MyProgressBar()        
        self.progress_bar.completed_lvl = 0
        self.progress_bar.needed_lvl = 1

        self.layout.add_widget(BoxLayout(orientation = "horizontal"))        
        self.layout.add_widget(self.mixer)
        self.layout.add_widget(BoxLayout(orientation = "horizontal"))
        self.layout.add_widget(BoxLayout(orientation = "horizontal"))
        self.layout.add_widget(self.progress_bar)                

        self.FlasksPerSec = 2.5

        self.arrow = Arrow()        
        
        Clock.schedule_once(self.tutor.user_guide, 1.0 / self.FPS)


    def fly_upwards(self):
        for fl in self.Flasks:
            self.remove_widget(fl)
            self.add_widget(fl)
            self.FlyingFlasks.append(fl)
            fl.go_to(None, fl.center_x, Window.height * 1.25, Window.height * 0.02, Window.height * 0.05)
        self.Flasks = []


    def start_stop(self):
        self.stop = not self.stop
        if self.stop:
            self.in_hidden_mixer = self.mix_on
            self.mix_on = ""
            self.ScoreStr = ""
        else:
            self.mix_on = self.in_hidden_mixer
            self.ScoreStr = str(self.Score)

    def adjust_score(self, value):
        self.Score += value
        self.ScoreStr = str(self.Score)
        if value > 0:
            self.ScoreAdd = "+"
            self.color_green = 1
            self.color_red = 0
        else:
            self.color_green = 0
            self.color_red = 1        
        self.ScoreAdd += str(value)
        Clock.schedule_once(self.clear_score_change, 1.0)

    def clear_score_change(self, second):
        self.ScoreAdd = ""

    def flask_entrance(self):
        if len(self.AvailableFlasks) == 0:
            self.add_flask()
        new_flask = self.AvailableFlasks[0]
        if -1 <= self.tutor.user_guide_stage <= 1:
            index = 1
        elif self.tutor.user_guide_stage == 2:
            index = 0
        else:
            index = choice(range(len(self.enc.LiquidsByStage[self.tutor.game_stage])))
        new_flask.liquid_name = self.enc.LiquidsByStage[self.tutor.game_stage][index]
        if new_flask.liquid_name in self.enc.Colors.keys():
            new_flask.color_red = self.enc.Colors[new_flask.liquid_name][0]
            new_flask.color_green = self.enc.Colors[new_flask.liquid_name][1]
            new_flask.color_blue = self.enc.Colors[new_flask.liquid_name][2]
        else:
            new_flask.color_red = random()
            new_flask.color_green = random()
            new_flask.color_blue = random()
        new_flask.pos[0] = - Flask.sz * 0.75
        new_flask.center_y = Window.height * 0.15    
        new_flask.velocity_x = Flask.flask_velocity
        new_flask.velocity_y = 0
        self.Flasks.append(new_flask)        
        del self.AvailableFlasks[0]

    def flask_appearance(self, name):
        if len(self.AvailableFlasks) == 0:
            self.add_flask()
        new_flask = self.AvailableFlasks[0]
        new_flask.liquid_name = name
        if new_flask.liquid_name in self.enc.Colors.keys():        
            new_flask.color_red = self.enc.Colors[new_flask.liquid_name][0]
            new_flask.color_green = self.enc.Colors[new_flask.liquid_name][1]
            new_flask.color_blue = self.enc.Colors[new_flask.liquid_name][2]
        else:
            new_flask.color_red = random()
            new_flask.color_green = random()
            new_flask.color_blue = random()
        new_flask.center_x = self.mixer.center_x
        new_flask.center_y = self.mixer.center_y - self.mixer.sz * 0.5
        new_flask.velocity_x = 0
        new_flask.velocity_y = 0
        self.Flasks.append(new_flask)        
        del self.AvailableFlasks[0]        

    def add_flask(self):
        new_flask = Flask()
        self.AvailableFlasks.append(new_flask)
        self.add_widget(new_flask)                

    def add_container(self, new_container):
        self.Containers.append(new_container)
        self.add_widget(new_container, 1)        

    def rotate_conveyor(self):
        if len(self.conv) > 0:
            for i in range(4):
                self.remove_widget(self.conv[i])

        self.conv = []

        Wheel.angle -= 1
        if Wheel.angle == -360:
            Wheel.angle = 0

        for i in range(4):
            self.conv.append(Wheel())
            Wheel.left_corner_x = i * (Window.width - Wheel.bottom_height) / 3.0
            self.add_widget(self.conv[i])

    def update(self, arg2):

        if self.stop:
            return

        for i in range(len(self.Flasks) - 1, -1, -1):            
            self.Flasks[i].move()
            if self.Flasks[i].pos[0] > Window.width + Flask.sz:
                game.AvailableFlasks.append(self.Flasks[i])
                del self.Flasks[i]     


        for i in range(len(self.FlyingFlasks) - 1, -1, -1):            
            if self.FlyingFlasks[i].approachingTo != None and self.FlyingFlasks[i].is_near(self.FlyingFlasks[i].destination, self.FlyingFlasks[i].eps):                                
                toContainer = self.FlyingFlasks[i].approachingTo
               
                if isinstance(toContainer, Mixer):
                    if abs(self.FlyingFlasks[i].center_y - self.FlyingFlasks[i].destination[1]) > abs(self.FlyingFlasks[i].velocity_y):
                        self.FlyingFlasks[i].move()                        
                        continue                    
                        
                    if not self.FlyingFlasks[i].inMixer:
                        self.FlyingFlasks[i].inMixer = True
                        self.mixer.received += 1
                        del self.FlyingFlasks[i]
                        if self.mixer.received == 2:
                            self.mixer.react()
                    continue

                if 10 <= game.tutor.user_guide_stage <= 12 and len(self.FlyingFlasks) == 1:
                    Clock.schedule_once(game.tutor.user_guide_inc, 0.1)                                      

                if game.tutor.user_guide_stage == 6 and self.FlyingFlasks[i].liquid_name == "HCl":
                    game.tutor.user_guide_stage = 7

                if game.tutor.user_guide_stage == 2:
                    for cont in game.Containers:
                        if cont.containFlask != None and cont != toContainer:
                            game.tutor.user_guide_stage = 3
                            break

#                if game.tutor.user_guide_stage == 1:
#                    game.tutor.user_guide_stage = 2
                    
                if toContainer.containFlask != None:                    
                    self.adjust_score(-1)
                    toContainer.containFlask.velocity_x = self.FlyingFlasks[i].velocity_x                    
                    toContainer.containFlask.velocity_y = self.FlyingFlasks[i].velocity_y                                       
                    toContainer.containFlask.destination = Window.width * 2, 0
                    self.FlyingFlasks.append(toContainer.containFlask)
                self.FlyingFlasks[i].velocity_x, self.FlyingFlasks[i].velocity_y = 0, 0
                toContainer.containFlask = self.FlyingFlasks[i]
                del self.FlyingFlasks[i]
            else:                
                self.FlyingFlasks[i].move()
                if self.FlyingFlasks[i].pos[0] > Window.width + Flask.sz \
                or self.FlyingFlasks[i].pos[0] < - Window.width * 0.2 \
                or self.FlyingFlasks[i].pos[1] < - Window.height * 0.2 \
                or self.FlyingFlasks[i].pos[1] >   Window.height * 1.2:
                    game.AvailableFlasks.append(self.FlyingFlasks[i])
                    del self.FlyingFlasks[i]     

        self.secs += 1.0 / self.FPS
        if self.secs >= self.FlasksPerSec * (Flask.sz / Flask.flask_velocity) / self.FPS and ((not 0 <= self.tutor.user_guide_stage < 2) or len(self.Flasks) == 0):
            self.secs = 0
            self.flask_entrance()

        self.rotate_conveyor()

class ChemistryWithFunApp(App):    
    def build(self):
        global game
        game = ChemistryWithFunGame()        
        return game


if __name__ == '__main__':
    ChemistryWithFunApp().run()