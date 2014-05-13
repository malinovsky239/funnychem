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
from gc import get_objects, garbage
from kivy.uix.widget import Widget
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
            if self.containFlask:
                self.containFlask.go_to(game.mixer, game.mixer.pos[0] - Window.width * 0.1 + Window.width * 0.2 * game.mixer.count, game.mixer.pos[1], Window.height * 0.015, float("inf"))
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

class Encyclopaedia:
    Liquids = []
    Colors = []
    Type = []
    Reactions = {"Cl_2+Mg": "MgCl_2", "Cl_2+H_2": "HCl"}   

    def preprocess(self, name):        
        res = ""
        for x in name:
            if '0' <= x <= '9':
                res += '[sub]' + x + '[/sub]'
            else:
                res += x        
        return res

    def init(self):        
        with open(os.path.dirname(os.path.realpath(sys.argv[0])) + "\data", "r") as inp:
            data = inp.readlines()
            for i in range(0, len(data), 3):
                name = self.preprocess(data[i])
                self.Liquids.append(name)
                self.Colors.append(map(float, data[i + 1].split()))
                self.Type.append(data[i + 2])


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
    flask_velocity = Window.height * 0.000875;
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

    cyl_width = Window.height * 0.07    
    cyl_height = Window.height * 0.125    

    def __init__(self, **kwargs):
        super(Mixer, self).__init__(**kwargs)            
        self.center_x = Window.width * 0.8
        self.center_y = Window.height * 0.5           

    def add_flask(self, flask):
        if self.count == 2:
            return

        self.count += 1
        self.chosen.append(flask)
        
        if self.count == 2:
           print "Reaction!", self.chosen[0].liquid_name, self.chosen[1].liquid_name

    def on_touch_down(self, touch):
        center = self.center_x, self.center_y
        if abs(touch.x - self.center_x) > self.width / 2 or abs(touch.y - self.center_y) > self.height / 2:
            return           
        self.state = 1 - self.state

    def animate_mix(self, arg2):
        self.step += 1
        ANG = 60.0
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

        Clock.schedule_once(self.animate_mix, 1.0 / game.FPS)

    def react_part2(self, arg2):
        reagents = "+".join(sorted((self.chosen[0].liquid_name, self.chosen[1].liquid_name)))
        if reagents in Encyclopaedia.Reactions:
            new_liquid = Encyclopaedia.Reactions[reagents]
            game.flask_appearance(new_liquid)
            game.Flasks = game.Flasks[-1:] + game.Flasks[:-1]

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


class Tutor(Widget):
    text = StringProperty("")
    x_left = NumericProperty(0)
    y_left = NumericProperty(0)
    wnd_height = NumericProperty(0)
    wnd_width = NumericProperty(0)
    halign = StringProperty("left")
    full_text = ["Did| you| ever| thought||\nthat studying chemistry|\nmay bring [b]you[/b]||\n[size=72][color=#ff0000]F[/color]|[color=#00ff00]U[/color]|[color=#0000ff]N[/color]|?[/size]|||",
                   "Anyway,\n||you are\n|WELCOME\n|to the app that\n|will\n|help you to learn\n|and\n|will make you [b][i]enjoy[/i][/b] chemistry|||||||",
                   "Best regards,\nIlia Malinovskii\nSaint Petersburg\nMay, 2014||||||"]
    sentence = 0
    word = 0
    shown = True
    arrow_added = False
    user_guide_stage = 0
    iterations = 0

#    def show(self):
#        global game
#        game.add_widget(self)

    def user_guide(self, second):
        if self.user_guide_stage == 3:
            game.remove_widget(game.arrow)
            return   

        if self.user_guide_stage == 0:
            if len(game.Flasks) and game.Flasks[0].center_x > 0:
                if not self.arrow_added:
                    game.arrow.text = "This is a flask with substance"
                    game.add_widget(game.arrow)
                    self.arrow_added = True
                    game.arrow.text_tab = game.arrow.hor_line / 2
                game.arrow.indicate(game.Flasks[0].center_x, game.Flasks[0].center_y + game.Flasks[0].sz)        
                self.iterations += 1
            if self.iterations == game.FPS * 2:
                self.iterations = 0
                self.user_guide_stage += 1                        

        if self.user_guide_stage == 1:
            if len(game.Containers):
                game.arrow.text = "Touch the shelf to place the first flask from the conveyor there"
                game.arrow.indicate(game.Containers[0].center_x, game.Containers[0].center_y)        
                game.arrow.text_tab = - game.arrow.hor_line / 2                

        if self.user_guide_stage == 2:
            game.arrow.text = "Great! Now add another flask to another container"
            game.arrow.indicate(game.arrow.start_x, game.arrow.start_y)        

        Clock.schedule_once(self.user_guide, 1.0 / game.FPS)


    def on_touch_down(self, touch):
        if not self.shown:
            return
        center = self.x_left + self.wnd_width / 2, self.y_left + self.wnd_height * 1.15
        if abs(touch.x - center[0]) > self.wnd_width / 4 or abs(touch.y - center[1]) > self.height * 0.2:
            return           
        self.hide()
        game.into_the_game()

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

    def intro(self, second):
        if not self.shown:
            return
        self.word += 1
        if self.sentence == 2:
            self.halign = "right" 
        self.text = "".join(self.full_text[self.sentence].split("|")[:self.word])
        if self.word == len(self.full_text[self.sentence].split("|")):
            self.word = 0
            self.sentence += 1
#            self.parent.remove_widget(self)        
            if self.sentence == len(self.full_text):
                self.hide()             
                game.into_the_game()                
                return
        Clock.schedule_once(self.intro, 0.5)

class ChemistryIsFunGame(Widget):

    Flasks = []
    FlyingFlasks = []
    FlyingFlasksFinish = []
    AvailableFlasks = []
    FlasksPerSec = 0
    Score = NumericProperty(0)

    Containers = []
    secs = 0
    conv = []   

    stop = False

    arrow = None

    def __init__(self, **kwargs):
        super(ChemistryIsFunGame, self).__init__(**kwargs)            

        self.FlasksPerSec = 1

        self.tutor = Tutor()
        self.add_widget(self.tutor)
#        self.tutor.show();

        self.enc = Encyclopaedia()
        self.enc.init()

        self.FPS = 120

        self.flask_entrance()

        Clock.schedule_interval(self.update, 1.0 / self.FPS)

    def into_the_game(self):
        for i in range(4):            
            new_container = Container()            
            new_container.pos = Window.width * 0.1 + (Window.height * 0.2) * i, Window.height * 0.73
            new_container.touched_down = False            
            self.add_container(new_container)

        self.mixer = Mixer()
        self.add_widget(self.mixer)        
        for fl in self.Flasks:
            self.remove_widget(fl)
            self.add_widget(fl)
            self.FlyingFlasks.append(fl)
            fl.go_to(None, fl.center_x, Window.height * 1.25, Window.height * 0.02, Window.height * 0.05)
        self.Flasks = []

        self.FlasksPerSec = 1.5

        self.arrow = Arrow()        

        Clock.schedule_once(self.tutor.user_guide, 1.0 / self.FPS)


    def start_stop(self):
        stop = not stop

    def flask_entrance(self):
        if len(self.AvailableFlasks) == 0:
            self.add_flask()
        new_flask = self.AvailableFlasks[0]
        index = choice(range(len(self.enc.Liquids)))
        new_flask.liquid_name = self.enc.Liquids[index]
        new_flask.color_red = self.enc.Colors[index][0]
        new_flask.color_green = self.enc.Colors[index][1]
        new_flask.color_blue = self.enc.Colors[index][2]
        new_flask.pos[0] = - Window.width * 0.1
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
        print(name)
        new_flask.color_red = random()
        new_flask.color_green = random()
        new_flask.color_blue = random()
        new_flask.center_x = self.mixer.pos[0]
        new_flask.center_y = self.mixer.pos[1]
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

        for fl in self.Flasks:
            fl.move()

        for i in range(len(self.FlyingFlasks) - 1, -1, -1):            
            if self.FlyingFlasks[i].approachingTo != None and self.FlyingFlasks[i].is_near(self.FlyingFlasks[i].destination, self.FlyingFlasks[i].eps):                                
                toContainer = self.FlyingFlasks[i].approachingTo
               
                if isinstance(toContainer, Mixer):
                    if abs(self.FlyingFlasks[i].center_y - game.mixer.pos[1]) > abs(self.FlyingFlasks[i].velocity_y):
                        self.FlyingFlasks[i].move()                        
                        continue                    
#                        if self.mixer.sentBack == 0:
#                            self.mixer.sentBack += 1
                        
                    if not self.FlyingFlasks[i].inMixer:
                        self.FlyingFlasks[i].inMixer = True
                        self.mixer.received += 1
                        del self.FlyingFlasks[i]
                        if self.mixer.received == 2:
                            self.mixer.react()
                    continue                                                           

                if game.tutor.user_guide_stage == 2:
                    for cont in game.Containers:
                        if cont.containFlask != None and cont != toContainer:
                            game.tutor.user_guide_stage = 3
                            break

                if game.tutor.user_guide_stage == 1:
                    game.tutor.user_guide_stage = 2
                    
                if toContainer.containFlask != None:                    
                    self.Score -= 1
                    toContainer.containFlask.velocity_x = self.FlyingFlasks[i].velocity_x                    
                    toContainer.containFlask.velocity_y = self.FlyingFlasks[i].velocity_y                                       
                    toContainer.containFlask.destination = Window.width * 2, 0
                    self.FlyingFlasks.append(toContainer.containFlask)
                self.FlyingFlasks[i].velocity_x, self.FlyingFlasks[i].velocity_y = 0, 0
                toContainer.containFlask = self.FlyingFlasks[i]
                del self.FlyingFlasks[i]
            else:                
                self.FlyingFlasks[i].move()
                if self.FlyingFlasks[i].pos[0] > Window.width * 1.2 \
                or self.FlyingFlasks[i].pos[0] < - Window.width * 0.2 \
                or self.FlyingFlasks[i].pos[1] < - Window.height * 0.2 \
                or self.FlyingFlasks[i].pos[1] >   Window.height * 1.2:
                    game.AvailableFlasks.append(self.FlyingFlasks[i])
                    del self.FlyingFlasks[i]     


#            fl.velocity_x += 0.001    
        self.secs += 1.0 / self.FPS
        if self.secs >= self.FlasksPerSec * (Flask.sz / Flask.flask_velocity) / self.FPS:
            self.secs = 0
            self.flask_entrance()

        self.rotate_conveyor()

class ChemistryIsFunApp(App):    
    def build(self):
        global game
        game = ChemistryIsFunGame()        
        return game


if __name__ == '__main__':
    ChemistryIsFunApp().run()