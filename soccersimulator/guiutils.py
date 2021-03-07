# -*- coding: utf-8 -*-
import pyglet
from pyglet import gl
from .utils import Vector2D, MobileMixin
from . import settings
import math
import time
import traceback
import logging
from .guisettings import *


logger = logging.getLogger("soccersimulator.gui")



def minmax(x, mi=0, ma=1):
    return max(mi, min(ma, x))


def get_color_scale(x):
    return [minmax(x), 0., minmax(1. - x)]


def col2rgb(color):
    return [int(minmax(x * 255, 0, 255)) for x in color]


class ObjectSprite(MobileMixin):
    def __init__(self, items=None):
        MobileMixin.__init__(self)
        self.primitives = []
        if items:
            self.add_primitives(items)

    def add_primitives(self, items):
        for item in items:
            self.primitives.append(item)

    def draw(self):
        try:
            gl.glPushMatrix()
            gl.glTranslatef(self.position.x, self.position.y, 0)
            gl.glRotatef(self.vitesse.angle * 180. / math.pi, 0, 0, 1)
            vec_prim = []
            if self.vitesse.norm != 0:
                vec_prim = get_vector_prims(self.vitesse.norm * 10, get_color_scale(
                        self.vitesse.norm / settings.maxBallAcceleration))
            for p in self.primitives + vec_prim:
                p.draw()
        except Exception as e:
            time.sleep(0.0001)
            logger.error("%s\n\t%s" % (e, traceback.format_exc()))
        finally:
            gl.glPopMatrix()


class Primitive2DGL(object):
    def __init__(self, verts, color, primtype=gl.GL_TRIANGLE_FAN):
        self.verts = verts
        self.color = color
        self.primtype = primtype

    def offset(self, dx, dy):
        self.verts = [(v[0] + dx, v[1] + dy) for v in self.verts]
        return self
    def draw(self):
        gl.glColor3f(*self.color)
        gl.glBegin(self.primtype)
        for vert in self.verts:
            gl.glVertex2f(*vert)
        gl.glEnd()


def get_circle_prims(radius, color=None, prct=1., angle=0.):
        if not color:
            color = [1, 1, 1]
        steps = int(10 * radius * math.pi * prct)
        s = math.sin(2 * math.pi / steps)
        c = math.cos(2 * math.pi / steps)
        dx, dy = math.cos(angle) * radius, math.sin(angle) * radius
        res = [(0., 0.)]
        for i in range(steps):
            res.append((dx, dy))
            dx, dy = (dx * c - dy * s), (dy * c + dx * s)
        return [Primitive2DGL(res, color)]

def get_vector_prims(length, color=None):
        if not color:
            color = [1, 1, 1]
        primtype = gl.GL_LINES
        verts = [(0, 0), (length, 0), (length, 0), (length * 0.9, 0.1 * length), (length, 0),
                 (length * 0.9, -0.1 * length)]
        return [Primitive2DGL(verts, color, primtype)]

def get_player_prims(color, shape):
        rad = settings.PLAYER_RADIUS
        eps = 0.3 * rad
        if shape == "carre":
            corps = Primitive2DGL([(-rad, -rad), (-rad, rad),
                                   (rad , rad), (rad, -rad)], color)
            front = Primitive2DGL([(rad - eps, rad * 0.85), (rad, 0), (rad - eps, -rad * 0.85)], color)
        elif shape == "triangle":
            corps = Primitive2DGL([(rad, 0), (-rad-eps,rad+eps),(-rad-eps, -rad-eps)], color)
            front = Primitive2DGL([(0, rad * 0.85), (rad+eps, 0)], color)
        else: #hexagone
            corps = Primitive2DGL([(-rad-eps/2, -rad+eps), (-rad-eps/2, rad-eps), (0, rad+rad/2),
                                   (rad+eps/2, rad-eps), (rad+eps/2, -rad+eps), (0, -rad-rad/2)], color)
            front = Primitive2DGL([(rad - eps, rad * 0.85), (rad, 0), (rad - eps, -rad * 0.85)], color)
        return [corps, front]

def get_ball_prims():
        rad = settings.BALL_RADIUS
        return get_circle_prims(rad, BALL_COLOR)

def get_field_prims():
        field = Primitive2DGL([(0, 0), (0, settings.GAME_HEIGHT),
                               (settings.GAME_WIDTH, settings.GAME_HEIGHT),
                               (settings.GAME_WIDTH, 0)], FIELD_COLOR)
        bandes_1 = Primitive2DGL([(0, 0), (settings.GAME_WIDTH, 0),
                                  (settings.GAME_WIDTH, settings.GAME_HEIGHT),
                                  (0, settings.GAME_HEIGHT), (0, 0)], LINE_COLOR, gl.GL_LINE_STRIP)
        bandes_2 = Primitive2DGL([(settings.GAME_WIDTH / 2, settings.GAME_HEIGHT),
                                  (settings.GAME_WIDTH / 2, 0)], LINE_COLOR, gl.GL_LINE_STRIP)
        y1 = (settings.GAME_HEIGHT - settings.GAME_GOAL_HEIGHT) / 2
        y2 = (settings.GAME_HEIGHT + settings.GAME_GOAL_HEIGHT) / 2
        xend = settings.GAME_WIDTH
        goals_1 = Primitive2DGL([(0, y1), (0, y2), (2, y2), (2, y1)], GOAL_COLOR)
        goals_2 = Primitive2DGL([(xend, y2), (xend, y1), (xend - 2, y1), (xend - 2, y2)], GOAL_COLOR)
        return [field, bandes_1, bandes_2, goals_1, goals_2]

def get_hud_prims():
        hud = Primitive2DGL([(0, settings.GAME_HEIGHT), (0, settings.GAME_HEIGHT + HUD_HEIGHT),
                             (settings.GAME_WIDTH, settings.GAME_HEIGHT + HUD_HEIGHT),
                             (settings.GAME_WIDTH, settings.GAME_HEIGHT)], HUD_BKG_COLOR)
        return [hud]

def get_orders_hud_prims():
        orders_hud = Primitive2DGL([(settings.GAME_WIDTH, 0), (settings.GAME_WIDTH, settings.GAME_HEIGHT + HUD_HEIGHT),
                             (settings.GAME_WIDTH*3/2, settings.GAME_HEIGHT + HUD_HEIGHT),
                             (settings.GAME_WIDTH*3/2, 0)], HUD_BKG_COLOR)
        return [orders_hud]

def get_panel_prims():
        panel = Primitive2DGL(
                [(settings.GAME_WIDTH, settings.GAME_HEIGHT + HUD_HEIGHT), (settings.GAME_WIDTH + PANEL_WIDTH,
                                                                            settings.GAME_HEIGHT + HUD_HEIGHT),
                 (settings.GAME_WIDTH + PANEL_WIDTH, 0), (settings.GAME_WIDTH, 0)], PANEL_BKG_COLOR)
        return [panel]

def get_rec_prims(l,color):
    prims = Primitive2DGL([(0,0),(l,0),(l,l),(0,l)],color)
    return [prims]

class TextSprite(object):
    def __init__(self, text="", position=None, color=None, scale=0.1):
        if not position:
            position = Vector2D()
        if not color:
            color = [255, 255, 255, 255]
        try:
            self._label = pyglet.text.Label(text, color=color, font_name="Arial", font_size=40)
        except Exception as e:
            logger.error("%s\n\t%s" % (e, traceback.format_exc()))
            time.sleep(0.0001)
            raise e
        self.scale = scale
        self.position = position
        self._ready = True
    def draw(self):
        try:
            gl.glPushMatrix()
            gl.glLoadIdentity()
            gl.glTranslatef(self.position.x, self.position.y, 0)
            gl.glScalef(self.scale, self.scale, 1)
            self._label.draw()
        except Exception as e:
            logger.error("%s\n\t%s" % (e, traceback.format_exc()))
            time.sleep(0.0001)
            raise e
        finally:
            gl.glPopMatrix()

class PlayerSprite(ObjectSprite):
    def __init__(self, name, color, type):
        ObjectSprite.__init__(self)
        self.name = name
        self.color = color
        self.type = type
        if type == "agility":
            self.add_primitives(get_player_prims(self.color, "carre"))
        elif type == "strength":
            self.add_primitives(get_player_prims(self.color, "hexagone"))
        else:
            self.add_primitives(get_player_prims(self.color, "triangle"))
        self.text = TextSprite(self.name, color=col2rgb(self.color) + [200], scale=SCALE_NAME)

    def draw(self):
        self.text.position = self.position
        ObjectSprite.draw(self)
        self.text.draw()


class BallSprite(ObjectSprite):
    def __init__(self):
        ObjectSprite.__init__(self)
        self.add_primitives(get_ball_prims())

class RectSprite(ObjectSprite):
    def __init__(self,l,color):
        ObjectSprite.__init__(self)
        self.l=l
        self.add_primitives(get_rec_prims(self.l,color))
    def set_color(self,color):
        self.primitives[0].color=color

class BackgroundSprite(ObjectSprite):
    def __init__(self):
        ObjectSprite.__init__(self)
        self.add_primitives(get_field_prims())
        self.add_primitives(get_hud_prims())
        self.add_primitives(get_orders_hud_prims())



class Hud(object):
    def __init__(self):
        self.sprites = dict()
        self.sprites["team1"] = TextSprite(color=HUD_TEAM1_COLOR, scale=0.07,
                                           position=Vector2D(0, settings.GAME_HEIGHT + 6))
        self.sprites["team2"] = TextSprite(color=HUD_TEAM2_COLOR, scale=0.07,
                                           position=Vector2D(0, settings.GAME_HEIGHT + 2))
        self.sprites["ongoing"] = TextSprite(position=Vector2D(settings.GAME_WIDTH - 50, settings.GAME_HEIGHT + 7),
                                             color=HUD_TEXT_COLOR,
                                             scale=0.05)
        self.sprites["ibattle"] = TextSprite(position=Vector2D(settings.GAME_WIDTH - 50, settings.GAME_HEIGHT + 4),
                                             color=HUD_TEXT_COLOR,
                                             scale=0.05)
        self.sprites["itour"] = TextSprite(position=Vector2D(settings.GAME_WIDTH - 50, settings.GAME_HEIGHT + 1),
                                           color=HUD_TEXT_COLOR,
                                           scale=0.05)

    def set_val(self, **kwargs):
        for k, v in kwargs.items():
            self.sprites[k]._label.text = v

    def draw(self):
        for s in self.sprites.values():
            s.draw()


class Panel(object):
    def __init__(self):
        self.scale = 0.055
        self._is_ready = True
        self.sprites = []

    def from_list(self, l):
        self._is_ready = False
        delta = -PANEL_DELTA
        self.sprites = []
        for i, s in enumerate(l):
            t1 = TextSprite("%d - %s" % (i + 1, s[1]), color=PANEL_TXT_COLOR, scale=self.scale,
                            position=Vector2D(settings.GAME_WIDTH,
                                              settings.GAME_HEIGHT + HUD_HEIGHT + delta))
            t2 = TextSprite(s[2], color=PANEL_SCORE_COLOR, scale=self.scale, position=Vector2D(settings.GAME_WIDTH
                                                                                               + PANEL_WIDTH * 1 / 4.,
                                                                                               settings.GAME_HEIGHT + HUD_HEIGHT + delta - PANEL_DELTA / 2.))
            self.sprites.append([t1, t2])
            delta -= PANEL_DELTA
            self._is_ready = True

    def draw(self):
        if self._is_ready:
            for s in self.sprites:
                s[0].draw()
                s[1].draw()

class Orders_hud(object):
    def __init__(self):
        self.action = "tire vers"
        self.player = ""
        self.currentAction = ""
        self.targets = []
        self.target = "SaCage"
        self.sprites = dict()
        self.sprites["title"] = TextSprite(position=Vector2D(settings.GAME_WIDTH + 5, settings.GAME_HEIGHT),
                                             color=[255,116,0,255],
                                             scale=0.07)
        self.sprites["title"]._label.text = "ORDRE :"
        self.sprites["instruction1"] = TextSprite(position=Vector2D(settings.GAME_WIDTH + 5, settings.GAME_HEIGHT - 5),
                                             color=[0,202,255,255],
                                             scale=0.05)
        self.sprites["instruction1"]._label.text = "1) Cliquez sur le joueur pour le sélectionner"
        self.sprites["instruction2"] = TextSprite(position=Vector2D(settings.GAME_WIDTH + 5, settings.GAME_HEIGHT - 10),
                                             color=[0,202,255,255],
                                             scale=0.05)
        self.sprites["instruction2"]._label.text = "2) Appuyez sur A pour changer l'action"
        self.sprites["instruction3"] = TextSprite(position=Vector2D(settings.GAME_WIDTH + 5, settings.GAME_HEIGHT - 15),
                                             color=[0,202,255,255],
                                             scale=0.05)
        self.sprites["instruction3"]._label.text = "3) Appuyez sur T pour changer de cible"

        self.sprites["player"] = TextSprite(position=Vector2D(settings.GAME_WIDTH + 5, settings.GAME_HEIGHT - 20),
                                             color=ORDERS_HUD_COLOR,
                                             scale=0.06)
        self.sprites["ongoing_order"] = TextSprite(position=Vector2D(settings.GAME_WIDTH + 5, settings.GAME_HEIGHT - 25),
                                             color=ORDERS_HUD_COLOR,
                                             scale=0.06)
        self.sprites["action"] = TextSprite(position=Vector2D(settings.GAME_WIDTH + 5, settings.GAME_HEIGHT - 30),
                                             color=ORDERS_HUD_COLOR,
                                             scale=0.06)
        self.sprites["action"]._label.text = "Choix de l'action : "+self.action
        self.sprites["target"] = TextSprite(position=Vector2D(settings.GAME_WIDTH + 5, settings.GAME_HEIGHT - 35),
                                           color=ORDERS_HUD_COLOR,
                                           scale=0.06)
        self.sprites["target"]._label.text = "Choix de la cible : "+self.target

        self.sprites["ok"] = TextSprite(position=Vector2D(settings.GAME_WIDTH*6/5-15, settings.GAME_HEIGHT - 55),
                                           color=ORDERS_HUD_COLOR,
                                           scale=0.06)
        self.sprites["ok"]._label.text = "AJOUTER"
        self.rectangle = pyglet.shapes.Rectangle(settings.GAME_WIDTH+27-15, settings.GAME_HEIGHT - 57, width=21, height=6.5)
        self.rectangle.opacity = 120
        #######################################
        self.sprites["ok2"] = TextSprite(position=Vector2D(settings.GAME_WIDTH*6/5+10, settings.GAME_HEIGHT - 55),
                                        color=ORDERS_HUD_COLOR,
                                        scale=0.06)
        self.sprites["ok2"]._label.text = "VIDER"
        self.rectangle2 = pyglet.shapes.Rectangle(settings.GAME_WIDTH+27+10, settings.GAME_HEIGHT - 57, width=15.5,
                                                 height=6.5)
        self.rectangle2.opacity = 120
        #okImg = pyglet.image.load("ok.png")
        #ok = pyglet.sprite.Sprite(okImg, settings.GAME_WIDTH*6/5, settings.GAME_HEIGHT - 55)
        #ok.scale = 0.05

    def set_val(self, **kwargs):
        for k, v in kwargs.items():
            if k == "player":
                self.sprites[k]._label.text = "Joueur sélectionné : "+v
                self.player = v
            elif k == "ongoing_order": #A CONNECTE AU RESTE (pour l'instant c'est juste une string)
                self.sprites[k]._label.text = "Action en cours : "+v
            elif k == "target":
                self.targets = v

    def change_target(self):
        print("#################################")
        print(self.targets)
        print(self.target)
        for i in range(0, len(self.targets)):
            if self.target == self.targets[i]:
                print(i)
                if i == len(self.targets)-1:
                    self.target = self.targets[0]
                else:
                    self.target = self.targets[i+1]
                self.sprites["target"]._label.text = "Choix de la cible : "+self.target
                break
        print(self.target)

    def get_target(self):
        return self.target

    def change_action(self):
        if self.action == "tire vers":
            self.action = "se déplace vers"
        else:
            self.action = "tire vers"
        self.sprites["action"]._label.text = "Choix de l'action : "+self.action

    def change_currentAction(self,currentAction):
        print(currentAction)
        self.currentAction = currentAction
        self.sprites["ongoing_order"]._label.text = "Action en cours : " + self.currentAction

    def get_action(self):
        return self.action

    def get_order(self):
        return [self.action, self.target]

    def draw(self):
        for s in self.sprites.values():
            s.draw()
        self.rectangle.draw()
        self.rectangle2.draw()
