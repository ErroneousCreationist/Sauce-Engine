import pymunk
import pygame
import math
import os
import json
import difflib
from pymunk import Vec2d

#object classes
class UpdatableDestroyable:
    def __init__(self, name, pos, rotation, scale, theScene) -> None:
        self.name = name
        self.position = pos
        self.rotation = rotation
        self.scale = scale
        self.scene:Scene = theScene
    def earlyUpdate(self):
        pass
    def lateUpdate(self):
        pass
    def update(self):
        pass
    def destroy(self):
        if self in self.scene.objects:
            self.scene.objects.remove(self)
    def returncopy(self, name, pos, scene):
        return UpdatableDestroyable(name, pos, self.rotation, self.scale, scene)

class GraphicalObject(UpdatableDestroyable):
    def __init__(self, name, pos, rotation, scale, theScene, sprite, offset = (0,0), layer = 0, anim = None) -> None:
        super().__init__(name, pos, rotation, scale, theScene)
        self.sprite = sprite
        self.layer = layer
        self.offset = offset
        self.active = True
        self.animator:AnimationController = anim
        if self.animator:
            self.animator.init(self)
    def setscale(self, scale):
        self.scale = scale
    def setactive(self, value:bool):
        self.active = value
    def update(self):
        super().update()
        if self.layer == 1:
            #print("i drew an image")
            self.scene.TheGame.DrawImage(self.sprite, self.position, self.rotation, self.scale, self.offset)
            if self.animator:
                self.animator.update()
    def earlyUpdate(self):
        super().lateUpdate()
        if self.layer ==0:
            self.scene.TheGame.DrawImage(self.sprite, self.position, self.rotation, self.scale, self.offset)
            if self.animator:
                self.animator.update()
    def returncopy(self, name, pos, scene):
        return GraphicalObject(name, pos, self.rotation, self.scale, scene, self.sprite, self.offset, self.layer, self.animator.returncopy() if self.animator else None)

class UiObject(GraphicalObject):
    def __init__(self, name, pos, rotation, scale, theScene, sprite, offset = (0,0), anim = None) -> None:
        super().__init__(name, pos, rotation, scale, theScene, sprite, offset, 0, anim)
        self.sprite = sprite
        self.offset = offset
    def lateUpdate(self):
        self.scene.TheGame.DrawImage(self.sprite, self.position, self.rotation, self.scale, self.offset)
        if self.animator:
            self.animator.update()
        super().earlyUpdate()
    def update(self):
        pass
    def earlyUpdate(self):
        pass
    def returncopy(self, name, pos, scene):
        return UiObject(name, pos, self.rotation, self.scale, scene, self.sprite, self.offset, self.animator.returncopy() if self.animator else None)

class TextRendererUI(UiObject):
    def __init__(self, name, pos, rotation, scale, theScene, font, fontsize, text, col, bgcol=None, offset = (0,0), anim = None) -> None:
        self.textimg = pygame.font.Font(font, fontsize).render(text, True, col, bgcol)
        self.currfont = font
        self.currtext = text
        self.currfontsize = fontsize
        self.currcol = col
        self.currbgcol = bgcol
        super().__init__(name, pos, rotation, scale, theScene, self.textimg, offset, anim)
    def edit(self, text, font=None, fontsize=None, col=None, bgcol=None):
        if font==None:
            font=self.currfont
        if fontsize==None:
            fontsize=self.currfontsize
        if col==None:
            col=self.currcol
        if bgcol==None:
            bgcol=self.currbgcol
        self.textimg = pygame.font.Font(font, fontsize).render(text, True, col, bgcol)
        self.sprite = self.textimg
        self.currfont = font
        self.currbgcol = bgcol
        self.currcol = col
        self.currfontsize = fontsize
        self.currtext = text
    def returncopy(self, name, pos, scene):
        return TextRendererUI(name, pos, self.rotation, self.scale, scene, self.currfont, self.currfontsize, self.currtext, self.currcol, self.currbgcol, self.offset, self.animator.returncopy() if self.animator else None)

class TextRenderer(GraphicalObject):
    def __init__(self, name, pos, rotation, scale, theScene, font, fontsize, text, col, bgcol=None, offset = (0,0), anim = None) -> None:
        self.textimg = pygame.font.Font(font, fontsize).render(text, True, col, bgcol)
        self.currfont = font
        self.currfontsize = fontsize
        self.currcol = col
        self.currbgcol = bgcol
        self.currtext = text
        super().__init__(name, pos, rotation, scale, theScene, self.textimg, offset, anim)
    def edit(self, text, font=None, fontsize=None, col=None, bgcol=None):
        if font==None:
            font=self.currfont
        if fontsize==None:
            fontsize=self.currfontsize
        if col==None:
            col=self.currcol
        if bgcol==None:
            bgcol=self.currbgcol
        self.textimg = pygame.font.Font(font, fontsize).render(text, True, col, bgcol)
        self.sprite = self.textimg
        self.currfont = font
        self.currfontsize = fontsize
        self.currcol = col
        self.currbgcol = bgcol
        self.currtext = text
    def returncopy(self, name, pos, scene):
        return TextRenderer(name, pos, self.rotation, self.scale, scene, self.currfont, self.currfontsize, self.currtext, self.currcol, self.currbgcol, self.offset, self.animator.returncopy() if self.animator else None)

class Button(TextRendererUI):
    ButtonPressedThisFrame = False
    def __init__(self, name, pos, rotation, scale, theScene, font, fontsize, text, col, action, mousebutton=1, bgcol=None, offset = (0,0), anim = None) -> None:
        super().__init__(name, pos, rotation, scale, theScene, font, fontsize, text, col, bgcol, offset, anim)
        self.action = action
        self.rect = self.textimg.get_rect()
        self.rect.center = self.position
        self.mousebutton = mousebutton
    def earlyUpdate(self):
        self.rect = self.textimg.get_rect()
        self.rect.center = self.position
        if self.scene.TheGame.GetMouseDown(self.mousebutton):
            if self.rect.collidepoint(self.scene.TheGame.GetMousePosition()):
                self.action(self)
                Button.ButtonPressedThisFrame = True
        super().earlyUpdate()
    def lateUpdate(self):
        super().lateUpdate()
        Button.ButtonPressedThisFrame = False
    def returncopy(self, name, pos, scene):
        return Button(name, pos, self.rotation, self.scale, scene, self.currfont, self.currfontsize, self.currtext, self.currcol, self.action, self.mousebutton, self.currbgcol, self.offset, self.animator.returncopy() if self.animator else None)

class InputField(TextRendererUI):
    currselected=None
    def __init__(self, name, pos, rotation, scale, theScene, font, fontsize, col, action, autocorrectlist=None, defaulttext = "", maxcharacters = 20, autocorrectlabelcol = None, bgcolSelected = None, offset = (0,0), anim = None) -> None:
        super().__init__(name, pos, rotation, scale, theScene, font, fontsize, defaulttext, col, None, offset, anim)
        self.user_text = defaulttext
        self.action = action
        self.autocorrectlist=autocorrectlist
        self.rect = self.textimg.get_rect()
        self.rect.center = self.position
        self.bgcolSelected = bgcolSelected
        self.autocorrectlabel = None
        self.maxcharacters = maxcharacters
        self.autocorrectlabelcol = autocorrectlabelcol
        self.defaulttext = defaulttext
        if self.autocorrectlist != None:
            self.autocorrectlabel = self.scene.spawn(TextRenderer(self.name+"_label", self.position, self.rotation, self.scale, self.scene, self.currfont, self.currfontsize, "", autocorrectlabelcol, None, None, None))
    def onkeypress(self):
        events = self.scene.TheGame.currentevents
        for k in events:
            if not k.type == pygame.KEYDOWN:
                continue
            if k.key == pygame.K_DELETE or k.key == pygame.K_BACKSPACE:
                self.user_text = self.user_text[:-1]
            elif k.key == pygame.K_KP_ENTER or k.key == pygame.K_RETURN:
                InputField.currselected = None
            elif len(self.user_text) < self.maxcharacters:
                self.user_text += k.unicode
        if self.autocorrectlist:
            closest = difflib.get_close_matches(self.user_text, possibilities=self.autocorrectlist, n=1)
            if len(closest) > 0:
                self.autocorrectlabel.edit(closest[0])
        self.action(self,self.user_text)
    def earlyUpdate(self):
        self.rect = self.textimg.get_rect()
        self.rect.center = self.position
        self.rect.w = max(100, self.currtextimg.get_rect().width+10)
        if self.scene.TheGame.GetMouseDown(1):
            if self.rect.collidepoint(self.scale.TheGame.GetMousePosition()):
                InputField.currselected = self
        if self.scene.TheGame.GetAnyKeyDown():
            self.onkeypress()
        self.edit(self.user_text)
        self.scene.TheGame.DrawRect(self.bgcolSelected if InputField.currselected ==self else self.bgcol, self.rect)
        super().earlyUpdate()
    def returncopy(self, name, pos, scene):
        return InputField(name, pos, self.rotation, self.scale, scene, self.currfont, self.currfontsize, self.currcol, self.action, self.autocorrectlist, self.defaulttext, self.maxcharacters, self.autocorrectlabelcol, self.bgcolSelected, self.offset, self.animator.returncopy() if self.animator else None)

#animation
class AnimationController:
    def __init__(self, idleframe, animations, playonstart = -1) -> None:
        self.idleframe:AnimationFrame = idleframe
        self.animations:list[Animation] = animations
        self.attached:GraphicalObject = None
        self.playonstart = playonstart
        self.currframe = None
    def init(self, attached):
        self.attached = attached
        for i in self.animations:
            i.attached = self.attached
            i.fps = self.attached.scene.TheGame.fps
            i.myanimationcontroller = self
        self.playing = False
        self.reset()
        self.currentlyplaying = None
        self.animt = 0
        if self.playonstart != -1:
            self.playanim(self.playonstart)
    def stop(self):
        self.playing = False
    def update(self):
        if self.playing:
            for i in self.currentlyplaying.animationframes:
                if self.animt > i.start and self.animt < i.end and self.currframe != i:
                    self.currframe = i
                    if self.currframe.event:
                        self.currframe.event()
            if self.currframe != None:
                if self.currframe.rotation:
                    self.attached.rotation = self.currframe.rotation
                if self.currframe.scale:
                    self.attached.setscale(self.currframe.scale)
                if self.currframe.offset:
                    self.attached.offset = self.currframe.offset
                if self.currframe.sprite:
                    self.attached.sprite = self.currframe.sprite
            self.animt+=1/self.attached.scene.TheGame.fps
            if self.animt > self.currentlyplaying.totallength:
                self.currentlyplaying = None
                self.playing = False
                self.reset()
    def playanim(self, index):
        if not self.attached:
            return
        self.currentlyplaying = self.animations[index]
        self.playing = True
        self.animt = 0
    def reset(self):
        if self.playing:
            return
        if self.idleframe.rotation:
            self.attached.rotation = self.idleframe.rotation
        if self.idleframe.scale:
            self.attached.setscale(self.idleframe.scale)
        if self.idleframe.offset:
            self.attached.offset = self.idleframe.offset
        if self.idleframe.sprite:
            self.attached.sprite = self.idleframe.sprite
    def returncopy(self):
        return AnimationController(self.idleframe, self.animations, self.playonstart)  
    
class Animation:
    def __init__(self, frames, totallength) -> None:
        self.animationframes:list[AnimationFrame] = frames
        self.totallength = totallength

class AnimationFrame:
    def __init__(self, start, end, rotation=None, scale=None, offset=None, sprite=None, event=None) -> None:
        """The event parameter should be a function that takes one parameter, being the object that the animator is on."""
        self.rotation = rotation
        self.scale = scale
        self.offset = offset
        self.sprite = sprite
        self.start = start
        self.event = event
        self.end = end

#collider types
class ColliderData:
    def __init__(self) -> None:
        pass

class ColliderCircleData(ColliderData):
    def __init__(self, radius) -> None:
        super().__init__()
        self.radius = radius

class ColliderSquareData(ColliderData):
    def __init__(self, width, height) -> None:
        super().__init__()
        self.width = width
        self.height = height

#physics object data
class PhysicsData:
    def __init__(self, mass, elasticity, friction, moment, layer, static=False) -> None:
        self.mass = mass
        self.elasticity = elasticity
        self.friction = friction
        self.moment = moment
        self.layer = layer
        self.static = static

#physics object
class PhysicalObject(GraphicalObject):
    def __init__(self, name, pos, rotation, scale, theScene, sprite, layer=0, colliderdata:ColliderData = None, physicsdata:PhysicsData = None, offset = (0,0)) -> None:
        super().__init__(name, pos, rotation, scale, theScene, sprite, offset, layer)
        bodytype = pymunk.Body.DYNAMIC
        if physicsdata.static:
            bodytype==pymunk.Body.STATIC
        self.body = pymunk.Body(physicsdata.mass, physicsdata.moment, bodytype)
        self.shape = None
        self.circle = False
        self.scale_prev = scale
        if type(colliderdata) == "ColliderCircleData":
            self.shape = pymunk.Circle(self.body, colliderdata.radius)
            self.shape.elasticity = physicsdata.elasticity
            self.shape.friction = physicsdata.friction
            self.shape.collision_type = physicsdata.layer
            self.origradius = colliderdata.radius
            self.circle = True
        if type(colliderdata) == "ColliderSquareData":
            self.shape = pymunk.Poly(self.body, ((-colliderdata.width/2,-colliderdata.height/2), (-colliderdata.width/2,colliderdata.height/2), (colliderdata.width/2,colliderdata.height/2),(colliderdata.width/2,-colliderdata.height/2)))
            self.shape.elasticity = physicsdata.elasticity
            self.shape.friction = physicsdata.friction
            self.shape.collision_type = physicsdata.layer
            self.origwidth = colliderdata.width
            self.origheight = colliderdata.height
        self.scene.space.add(self.body,self.shape)
    def earlyUpdate(self):
        self.pos = self.body.position
        self.rotation = -math.degrees(self.body.angle)
        #update collider scale (oh no)
        if self.scale_prev != self.scale:
            if self.circle:
                self.shape.unsafe_set_radius(self.origradius*self.scale[0])
            else:
                self.shape.unsafe_set_vertices(((-self.origwidth/2*self.scale,-self.origheight/2*self.scale), (-self.origwidth/2*self.scale,self.origheight/2*self.scale), (self.origwidth/2*self.scale,self.origheight/2*self.scale),(self.origwidth/2*self.scale,-self.origheight/2*self.scale)))
        super().earlyUpdate()
        self.scale_prev = self.scale 
    
    def addforce(self, force):
        self.body.apply_force_at_world_point(force, self.body.position)
    def addimpulse(self, force):
        self.body.apply_impulse_at_world_point(force, self.body.position)
    def setvelocity(self, vel):
        self.body.velocity = vel
    def applyangularforce(self, force):
        """Apply a force in degrees per second to the body rotation"""
        self.body.angular_velocity += math.radians(force)
    def setangularvelocity(self, vel):
        """Set the body's angular velocity in degrees per second"""
        self.body.angular_velocity = math.radians(vel)
    
    def destroy(self):
        self.scene.space.remove(self.body, self.shape)
        super().destroy()
    def returncopy(self, name, pos, scene):
        colldata = None
        if self.circle:
            colldata = ColliderCircleData(self.origradius)
        else:
            colldata = ColliderSquareData(self.origwidth, self.origheight)

        physdata = PhysicsData(self.body.mass, self.shape.elasticity, self.shape.friction, self.body.moment, self.shape.collision_type, True if self.body.body_type==pymunk.Body.STATIC else False)
        return PhysicalObject(name, pos, self.rotation, self.scale, scene, self.sprite, self.layer, colldata, physdata)

#scene, contains objects and a physics space
class Scene:
    def __init__(self, gravity, game, backgroundcol) -> None:
        self.objects = []
        self.space = None
        self.gravity = gravity
        self.TheGame:Game = game
        self.backgroundcol = backgroundcol
    def loadthisscene(self):
        self.space = pymunk.Space()
        self.space.gravity = self.gravity
        #you can add all of your initial objects here
    def findobjectbyName(self, name):
        for o in self.objects:
            if o.name == name:
                return o
        return None
    def spawn(self, object):
        self.objects.append(object)
        return object
    def gameloop(self):
        """A single loop of the game"""
        for i in self.objects:
            i.earlyUpdate()
        for i in self.objects:
            i.update()
        for i in self.objects:
            i.lateUpdate()
        self.space.step(1/self.TheGame.fps)
    def exitscene(self):
        self.objects = []
        self.space = None

#a scene that switches after a few seconds (for title cards and whatever)
class TimedScene(Scene):
    def __init__(self, gravity, game, backgroundcol, scenetime, nextsceneindex) -> None:
        super().__init__(gravity, game, backgroundcol)
        self.scenetime = scenetime
        self.nextsceneindex = nextsceneindex
    def gameloop(self):
        super().gameloop()
        self.scenetime -= 1/self.TheGame.fps
        if self.scenetime <= 0:
            self.TheGame.loadscene(self.nextsceneindex)

#the game class, controls scenes, game time, input stuff, and quitting
class Game:
    def __init__(self, displaywidth, displayheight, fps, caption, scenes) -> None:
        self.display_width = displaywidth
        self.display_height = displayheight
        self.fps = fps
        pygame.init()
        self.clock = pygame.time.Clock()
        self.display = pygame.display.set_mode((self.display_width, self.display_height))
        pygame.display.set_caption(caption)
        self.crashed = False
        self.gametime = 0
        self.scenes:list[Scene] = scenes
        self.currentscene:Scene = None
        self.loadscene(0)
        self.currentevents = None
        self.deltatime = 0.1
        try:
            pygame.mixer.init()
        except pygame.error:
            print("Error Init Audio")
        self.gameloop()

    def Quit(self):
        self.crashed = True

    def DrawImage(self, image, position, rotation, scale, offset):
        """Draw an image to the display"""
        # we need to rotate 180 degrees because of the y coordinate flip
        scaledimg = pygame.transform.scale_by(image, scale)
        rotatedimg = pygame.transform.rotate(scaledimg, rotation)
        Scaleoffset = Vec2d(*rotatedimg.get_size()) / 2
        position = position - Scaleoffset
        position = position+offset
        self.display.blit(rotatedimg, (round(position[0]), round(position[1])))

    def DrawImageRaw(self, image, position):
        """Draw an image to the display"""
        # we need to rotate 180 degrees because of the y coordinate flip
        self.display.blit(image, (round(position[0]), round(position[1])))

    def DrawImageRawOffset(self, image, position, offset):
        """Draw an image to the display"""
        # we need to rotate 180 degrees because of the y coordinate flip
        self.display.blit(image, (round(position[0]+offset[0]), round(position[1]+offset[1])))

    def GetAnyKeyDown(self):
        for i in self.currentevents:
            if i.type==pygame.KEYDOWN:
                return True
        return False
    
    def GetAnyKey(self):
        for i in pygame.key.get_pressed:
            if i:
                return True
        return False
    
    def GetAnyKeyUp(self):
        for i in self.currentevents:
            if i.type==pygame.KEYUP:
                return True
        return False

    def GetKeyDown(self, key):
        for i in self.currentevents:
            if i.type==pygame.KEYDOWN and i.key==key:
                return True
        return False
    
    def GetKeyUp(self, key):
        for i in self.currentevents:
            if i.type==pygame.KEYUP and i.key==key:
                return True
        return False
    
    def GetKey(self, key):
        keys = pygame.key.get_pressed()
        return keys[key]
    
    def GetMouseDown(self, button = 1):
        """BUTTON 1 IS LMB, BUTTON 2 IS RMB"""
        for i in self.currentevents:
            if i.type == pygame.MOUSEBUTTONDOWN and i.button == button:
                return True
        return False
    
    def GetMouseUp(self, button = 0):
        for i in self.currentevents:
            if i.type == pygame.MOUSEBUTTONUP and i.button == button:
                return True
        return False

    def GetMouse(self, button = 0):
        pressed = pygame.mouse.get_pressed()
        return pressed[button]
    
    def GetMousePosition(self):
        return pygame.mouse.get_pos()
    
    def GetMouseMoving(self):
        """Note, this returns the mouses position if it moves"""
        for i in self.currentevents:
            if i.type == pygame.MOUSEMOTION:
                return i.pos 
        return None
    
    def GetNormalisedMousePosition(self):
        """This returns the mouse position, X divided by SCREEN WIDTH, Y divided by SCREEN HEIGHT"""
        return (pygame.mouse.get_pos()[0] / self.display_width, pygame.mouse.get_pos()[1] / self.display_height)

    def DrawCircle(self, colour, position, radius, width=0, draw_topleft=True, draw_topright=True, draw_bottomleft=True, draw_bottomright=True):
        pygame.draw.circle(self.display, colour, position, radius, width, draw_topright, draw_topleft, draw_bottomleft, draw_bottomright)

    def DrawRect(self, colour, rect, thick=0):
        pygame.draw.rect(self.display, colour, rect, thick)

    def DrawSquare(self, colour, position, width, height, thick=0):
        pygame.draw.rect(self.display, colour, pygame.Rect(position[0]-width/2, position[1]-height/2, width, height), thick)

    def loadscene(self, index):
        if self.currentscene:
            self.currentscene.exitscene()
        self.scenes[index].loadthisscene()
        self.currentscene = self.scenes[index]
        
    def gameloop(self):
        while not self.crashed:
            self.currentevents = pygame.event.get()
            for event in self.currentevents:
                if event.type == pygame.QUIT:
                    self.crashed = True
            self.display.fill(self.currentscene.backgroundcol)
            self.currentscene.gameloop()
            pygame.display.flip()
            self.gametime += 1/self.fps
            self.deltatime = self.clock.tick(self.fps)
        pygame.quit()
        quit()

#important functions
assetpathSound = 0
assetpathMusic = 1
assetpathImages = 2
assetpathJson = 3

def FindAsset(assettype, startingpath, assetname) -> pygame.mixer.Sound or pygame.Surface or str or dict:
    """load an asset of a type (use the assetpath constants), returning a sound (sound), string (music), surface (image), dictionary (json). SET THE STARTINGPATH TO __FILE__ FOR THIS TO WORK, AND ENSURE YOU HAVE THE CORRECT ASSET LAYOUT"""
    startingpath = os.path.dirname(startingpath)
    match(assettype):
        case 0:
            return pygame.mixer.Sound(os.path.join(os.path.join(os.path.join(startingpath,"assets"), "sound"), assetname))
        case 1:
            return os.path.join(os.path.join(os.path.join(startingpath,"assets"), "music"), assetname)
        case 2:
            return pygame.image.load(os.path.join(os.path.join(os.path.join(startingpath,"assets"), "images"), assetname))
        case 3:
            f = open(pygame.image.load(os.path.join(os.path.join(os.path.join(startingpath,"assets"), "images"), assetname)))
            st = f.read()
            f.close()
            return json.loads(st)
    
def PlaySound(sound, loops = 0, ):
    if pygame.mixer.get_init != True:
        print("AUDIO NOT INIT")
        return
    s:pygame.mixer.Sound = sound
    s.play(loops=loops)

def SetCurrentMusic(music:str):
    if pygame.mixer.get_init != True:
        print("AUDIO NOT INIT")
        return
    pygame.mixer_music.load(music)

def PlayMusic(fadeS = 0):
    if pygame.mixer.get_init != True:
        print("AUDIO NOT INIT")
        return
    pygame.mixer_music.play(fade_ms=fadeS*1000)

def StopMusic():
    if pygame.mixer.get_init != True:
        print("AUDIO NOT INIT")
        return
    pygame.mixer_music.stop()

def ReMap(value, minInput, maxInput, minOutput, maxOutput):

	value = maxInput if value > maxInput else value
	value = minInput if value < minInput else value

	inputSpan = maxInput - minInput
	outputSpan = maxOutput - minOutput

	scaledThrust = float(value - minInput) / float(inputSpan)

	return minOutput + (scaledThrust * outputSpan)

#constant colours
White = (255,255,255)
Black = (0,0,0)
Red = (255,0,0)
Green = (0,255,0)
Blue = (0,0,255)
Grey = (128, 128, 128)

#other random constants
ZeroGravity = (0,0)
NormalGravity = (0,500)
NormalScale = (1,1)
Up = (0,-1)
Down = (0,1)
Left = (-1,0)
Right = (1,0)
DefaultFramerate = 60
DefaultScreenWidth = 1366
DefaultScreenHeight = 768
DefaultFont = 'freesansbold.ttf'