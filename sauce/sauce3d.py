from sauce import sauce
#import sauce
import math
import pygame
import os
import json

_ = False
"""A false value for making maps in code easier"""
ExampleMap = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,_,_,_,_,_,_,_,_,1,_,_,1],
    [1,_,_,_,1,1,_,_,_,1,_,_,1],
    [1,_,_,_,_,_,_,_,_,1,1,_,1],
    [1,_,_,_,1,1,_,_,_,1,1,_,1],
    [1,_,_,_,1,1,_,_,_,1,1,_,1],
    [1,_,_,_,_,_,_,_,_,_,_,_,1],
    [1,_,_,_,1,1,_,_,_,1,1,_,1],
    [1,_,_,_,_,_,_,_,_,1,_,_,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1]
]
"""An example map. Note that maps are 2D arrays, and that a number is a wall and a false value is not (you can use the provided _ value so you dont have to write false a ton of times)"""

turnscheme_Arrows = 0
turnscheme_Mouse = 1

class GraphicalObject3D(sauce.UpdatableDestroyable):
    def __init__(self, name, pos, theScene, image, scale = (1.0, 1.0), offset = (0,0), anim = None) -> None:

        super().__init__(name, pos, 0, sauce.NormalScale, theScene)
        if type(self.scene) != "Scene3D":
            self.destroy()
        self.image:pygame.Surface = image
        self.imgwidth = self.image.get_width()
        self.imgheight = self.image.get_height()

        self.half_imgwidth = self.imgwidth//2
        self.half_imgheight = self.imgheight //2
        self.imageratio = self.imgwidth  / self.imgheight
        self.dx, self.dy, self.theta, self.screen_x, self.dist, self.norm_dist = 0,0,0,0,0,0
        self.scale = scale
        self.offset = offset
        self.animator = anim
        if self.animator:
            self.animator.init(self)
    def get_sprite(self):
        dx = self.position[0] - self.scene.player.position[0]
        dy = self.position[1] - self.scene.player.position[1]
        self.dx, self.dy = dx, dy
        self.theta = math.atan2(dy, dx)

        delta = self.theta - math.radians(self.scene.player.rotation)
        if (dx > 0 and math.radians(self.scene.player.rotation) > math.pi) or (dx < 0 and dy < 0):
            delta += math.tau
        delta_rays = delta / (self.scene.player.raycaster.FOV / self.scene.player.raycaster.num_rays)
        self.screen_x = (self.scene.player.raycaster.half_num_rays + delta_rays) * self.scene.player.raycaster.scale

        self.dist = math.hypot(dx, dy)
        self.norm_dist = self.dist * math.cos(delta)
        if -self.half_imgwidth < self.screen_x < (self.scene.TheGame.display_width + self.half_imgwidth) and self.norm_dist > 0.5:
            self.get_sprite_projection()
    def get_sprite_projection(self):
        proj = self.scene.player.raycaster.screendist / self.norm_dist
        projwidth, projheight = proj * self.imageratio * self.scale[0], proj * self.scale[1]
        image = pygame.transform.scale(self.image, (projwidth, projheight))

        self.sprite_halfwidth = projwidth//2
        pos = self.screen_x - self.sprite_halfwidth + (projwidth*self.offset[0]), (self.scene.TheGame.display_height / 2) - projheight//2 + (projheight*self.offset[1])+self.scene.player.raycaster.yoffset

        self.scene.player.raycaster.objects_to_render.append((self.norm_dist, image, pos))
    def lateUpdate(self):
        self.get_sprite()
        if self.animator:
            self.animator.update()
    def returncopy(self, name, pos, scene):
        return GraphicalObject3D(name, pos, scene, self.image, self.scale, self.offset, self.animator.returncopy())

class AnimationController3D(sauce.AnimationController):
    """This is required for GraphicalObject3D animating!"""
    def __init__(self, idleframe, animations, playonstart=-1) -> None:
        super().__init__(idleframe, animations, playonstart)
        self.attached:GraphicalObject3D = None
    def update(self):
        if self.playing:
            for i in self.currentlyplaying.animationframes:
                if self.animt > i.start and self.animt < i.end and self.currframe != i:
                    self.currframe = i
                    if self.currframe.event:
                        self.currframe.event()
            if self.currframe != None:
                if self.currframe.scale:
                    self.attached.scale = self.currframe.scale
                if self.currframe.offset:
                    self.attached.offset = self.currframe.offset
                if self.currframe.sprite:
                    self.attached.image = self.currframe.sprite
            self.animt+=1/self.attached.scene.TheGame.fps
            if self.animt > self.currentlyplaying.totallength:
                self.currentlyplaying = None
                self.playing = False
                self.reset()
    def reset(self):
        if self.playing:
            return
        if self.idleframe.scale:
            self.attached.scale = self.idleframe.scale
        if self.idleframe.offset:
            self.attached.offset = self.idleframe.offset
        if self.idleframe.sprite:
            self.attached.image = self.idleframe.sprite
    def returncopy(self):
        return AnimationController3D(self.idleframe, self.animations, self.playonstart)  

class PlayerSettings:
    """Stores data about the player, which is really just a glorified camera that can move"""
    def __init__(self, initpos, rotation, speed, turnspeed, playerscale = 60, headbobintensity = 15, headbobspeed = 8, fov=75, maxdepth = 20, forwardkey=pygame.K_w, backwardkey=pygame.K_s, leftkey = pygame.K_a, rightkey = pygame.K_d, turnscheme = turnscheme_Arrows, mouse_sens = 0.04, mouse_maxrelmove = 40) -> None:
        self.initialposition = initpos
        self.rotation = rotation
        self.speed = speed
        self.turnspeed = turnspeed
        self.forward = forwardkey
        self.backward = backwardkey
        self.left = leftkey
        self.right = rightkey
        self.fov = fov
        self.headbob = headbobintensity
        self.headbobspeed = headbobspeed
        self.maxdepth = maxdepth
        self.turnscheme = turnscheme
        self.playerscale = playerscale

        self.mouse_sens = mouse_sens
        self.mouse_maxrelmove = mouse_maxrelmove

class Player3D(sauce.UpdatableDestroyable):
    """The player. This just movement code, that moves a camera."""
    def __init__(self, name, theScene, playersettings) -> None:
        super().__init__(name, (0,0), 0, sauce.NormalScale, theScene)
        self.position = playersettings.initialposition
        self.rotation = playersettings.rotation
        self.speed = playersettings.speed
        self.turnspeed = playersettings.turnspeed
        self.forward = playersettings.forward
        self.backward = playersettings.backward
        self.left = playersettings.left
        self.right = playersettings.right
        self.turnscheme = playersettings.turnscheme
        self.headbobpos = 0
        self.headbobintensity = playersettings.headbob
        self.headbobspeed = playersettings.headbobspeed
        self.scale = playersettings.playerscale
        if self.turnscheme == turnscheme_Mouse:
            pygame.mouse.set_visible(False)
        self.mouse_sens = playersettings.mouse_sens
        self.mouse_maxrelmove = playersettings.mouse_maxrelmove

        #we have to be in a 3d scene
        if type(self.scene) != "Scene3D":
            self.destroy()
        self.generateRaycaster(playersettings)
        
    def generateRaycaster(self, playersettings):
        self.raycaster = Raycaster(self.scene.TheGame, self, playersettings.fov, playersettings.maxdepth)

    def checkCollision(self, pos) -> bool:
        return pos in self.scene.realmap

    def movement(self):
        sin_a = math.sin(math.radians(self.rotation))
        cos_a = math.cos(math.radians(self.rotation))
        dx,dy = 0,0
        speed = self.speed * self.scene.TheGame.deltatime
        speed_sin = sin_a*speed
        speed_cos = cos_a*speed

        keys = pygame.key.get_pressed()
        moving = False
        if(keys[self.forward]):
            moving = True
            dx += speed_cos
            dy += speed_sin
        if(keys[self.backward]):
            moving = True
            dx += -speed_cos
            dy += -speed_sin
        if(keys[self.left]):
            moving = True
            dx += speed_sin
            dy += -speed_cos
        if(keys[self.right]):
            moving = True
            dx += -speed_sin
            dy += speed_cos
        if moving and self.headbobintensity > 0:
            s = math.sin(self.scene.TheGame.gametime * self.headbobspeed)
            s *= self.headbobintensity
            self.headbobpos = s
        else:
            self.headbobpos = 0
        pos = self.position
        scale = self.scale/self.scene.TheGame.deltatime
        if self.checkCollision((int(pos[0]+dx*scale),int(pos[1]))) != True:
            self.position = self.position[0]+dx,self.position[1]
        if self.checkCollision((int(pos[0]),int(pos[1]+dy*scale))) !=True:
            self.position = self.position[0],self.position[1]+dy
        
    @property
    def map_pos(self):
        return int(self.position[0]), int(self.position[1])
    
    def turn(self):
        if self.turnscheme == turnscheme_Arrows:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT]:
                self.rotation += self.turnspeed * self.scene.TheGame.deltatime
            if keys[pygame.K_LEFT]:
                self.rotation -= self.turnspeed * self.scene.TheGame.deltatime
        elif self.turnscheme == turnscheme_Mouse:
            x,y = pygame.mouse.get_pos()
            if x < 100 or x > self.scene.TheGame.display_width - 100:
                pygame.mouse.set_pos(self.scene.TheGame.display_width/2, self.scene.TheGame.display_height/2)
            self.rel = pygame.mouse.get_rel()[0]
            self.rel = max(-self.mouse_maxrelmove, min(self.mouse_maxrelmove, self.rel))
            self.rotation += self.rel * self.mouse_sens * self.scene.TheGame.deltatime
        self.rotation %= 360

    def update(self):
        self.movement()
        self.turn()
        self.raycaster.update()
        self.raycaster.yoffset = self.headbobpos
        #self.scene.TheGame.DrawCircle(sauce.Red, (self.position[0]*100, self.position[1]*100), 10)
        super().update()

class Raycaster():
    """Created and used by the player class. you shouldn't need to edit this"""
    def __init__(self, game:sauce.Game, player:Player3D, fov, maxdepth) -> None:
        self.FOV = math.radians(fov)
        self.half_FOV = self.FOV/2
        self.game:sauce.Game = game
        self.player = player
        self.num_rays = game.display_width//2
        self.half_num_rays = self.num_rays // 2
        self.deltaangle = self.FOV/self.num_rays
        self.maxdepth = maxdepth
        self.screendist = (game.display_width //2) / math.tan(self.half_FOV)
        self.scale = game.display_width//self.num_rays
        self.half_height = game.display_height//2
        self.half_width = game.display_width//2
        self.yoffset = 0

        self.ray_casting_result = []
        self.objects_to_render = []
        self.walltextures = self.player.scene.walltextures
        self.texsize = self.player.scene.wallimgsize
        self.halftexsize = self.texsize // 2
        self.skyoffset = 0
        self.prevsky = 0

    def get_objects_to_render(self):
        #get them
        for ray, values in enumerate(self.ray_casting_result):
            depth, proj_height, texture, offset = values
            displayheight = self.game.display_height
            if proj_height < displayheight:
                wall_column = self.walltextures[texture].subsurface(
                    offset * (self.texsize - self.scale), 0, self.scale, self.texsize
                )
                wall_column = pygame.transform.scale(wall_column, (self.scale, proj_height))
                #wall_column.fill((min(255*(depth/self.maxdepth), 255), min(255,255*(depth/self.maxdepth)), min(255,255*(depth/self.maxdepth))), special_flags=pygame.BLEND_SUB) 
                wall_pos = (ray * self.scale, self.half_height - proj_height // 2+self.yoffset)
                self.objects_to_render.append((depth, wall_column, wall_pos))
                #self.game.DrawImageRaw(wall_column, wall_pos)
            else:
                texture_height = self.texsize * displayheight / proj_height
                wall_column = self.walltextures[texture].subsurface(
                    offset * (self.texsize - self.scale), self.halftexsize - texture_height // 2, self.scale, texture_height
                )
                wall_column = pygame.transform.scale(wall_column, (self.scale, displayheight))
                #wall_column.fill((min(255*(depth/self.maxdepth), 255), min(255,255*(depth/self.maxdepth)), min(255,255*(depth/self.maxdepth))), special_flags=pygame.BLEND_SUB) 
                wall_pos = (ray*self.scale, 0+self.yoffset)
                self.objects_to_render.append((depth, wall_column, wall_pos))
                #self.game.DrawImageRaw(wall_column, wall_pos)
        #then draw them
        self.objects_to_render = sorted(self.objects_to_render, key=lambda t: t[0], reverse=True)
        for depth, image, pos in self.objects_to_render:
            self.game.DrawImageRaw(image, pos)
        self.objects_to_render = []

    
    def drawbackground(self):
        bgimg:pygame.Surface = self.player.scene.backgroundimage
        self.skyoffset = ((self.skyoffset-self.prevsky) + 4.0 * (self.player.rotation*4)) % self.game.display_width
        
        self.game.DrawImageRawOffset(bgimg, (0, 0), (-self.skyoffset, 0))
        self.game.DrawImageRawOffset(bgimg, (0, 0), (-self.skyoffset + self.game.display_width, 0))

        self.game.DrawRect(self.player.scene.floorcol, pygame.Rect(0, self.game.display_height/2+self.yoffset, self.game.display_width, self.game.display_height-self.yoffset))
        self.prevsky = self.skyoffset

    def ray_cast(self):
        self.ray_casting_result = []
        origrayangle = math.radians(self.player.rotation) - self.half_FOV +0.0001
        ray_angle = origrayangle
        maxangle = math.radians(self.player.rotation) + self.half_FOV +0.0001
        xx = 0
        xxstep = self.game.display_width / self.num_rays
        ox,oy = self.player.position
        x_map,y_map = self.player.map_pos
        texture_vert, texture_hor = 1,1
        

        for ray in range(self.num_rays):
            sin_a = math.sin(ray_angle)
            cos_a = math.cos(ray_angle)

            #horizontals
            y_hor, dy = (y_map+1, 1) if sin_a > 0 else (y_map - 1e-6, -1)
            depth_hor = (y_hor - oy) / sin_a
            x_hor = ox + depth_hor * cos_a

            delta_depth = dy/sin_a
            dx = delta_depth *cos_a

            for i in range(self.maxdepth):
                tile_hor = int(x_hor), int(y_hor)
                if tile_hor in self.player.scene.realmap:
                    texture_hor = self.player.scene.realmap[tile_hor]
                    break
                x_hor += dx
                y_hor += dy
                depth_hor += delta_depth

            #verticals
            x_vert, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-6, -1)

            depth_vert = (x_vert - ox) / cos_a
            y_vert = oy + depth_vert * sin_a

            delta_depth = dx / cos_a
            dy = delta_depth * sin_a

            for i in range(self.maxdepth):
                tile_vert = int(x_vert), int(y_vert)
                if tile_vert in self.player.scene.realmap:
                    texture_vert = self.player.scene.realmap[tile_vert]
                    break
                x_vert += dx
                y_vert += dy
                depth_vert += delta_depth

            if depth_vert < depth_hor:
                depth, texture = depth_vert, texture_vert
                y_vert %= 1
                offset = y_vert if cos_a > 0 else (1-y_vert)
            else:
                depth, texture = depth_hor, texture_hor
                x_hor %= 1
                offset = (1-x_hor) if sin_a > 0 else x_hor
            
            #remove fisheye
            depth *= math.cos(math.radians(self.player.rotation) - ray_angle)
            
            proj_height = self.screendist / (depth+0.0001)
            
            self.ray_casting_result.append((depth, proj_height, texture, offset))

            #col = min(255 / (1+depth ** 5 * 0.00002), 255)
            #colour = (col,col,col)
            #self.game.DrawRect(colour, 
                               #pygame.Rect(ray * self.scale, self.half_height - proj_height//2 + self.yoffset, self.scale, proj_height))
            ray_angle += self.deltaangle
            #ray_angle = origrayangle + math.atan(math.radians(xx/self.FOV))
            #xx += xxstep
    def update(self):
        self.ray_cast()
        self.drawbackground()
        self.get_objects_to_render()

class Scene3D(sauce.Scene):
    def __init__(self, gravity, game, map:list[list[bool]], playersettings:PlayerSettings, backgroundimage, walltextures, wallimgsize = 256, floorcol = sauce.Grey) -> None:
        self.map = map
        self.realmap = {}
        self.inaccessibletiles = {}
        for i, row in enumerate(map):
            for j, value in enumerate(row):
                if value == -1:
                    self.inaccessibletiles[(i,j)] = value
                if value > 0:
                    self.realmap[(i,j)] = value
        
        self.rows = len(map)
        self.cols = len(map[0])
        self.player = None
        self.playersettings = playersettings
        #create the wall textures list
        self.walltextures = []
        self.walltextures.append(None)
        self.walltextures.extend(walltextures)
        self.wallimgsize = wallimgsize
        self.floorcol = floorcol
        #scale the walltextures
        for i in walltextures:
            surf:pygame.Surface = i
            surf = pygame.transform.scale(surf, (wallimgsize, wallimgsize))
        self.backgroundimage = backgroundimage
        super().__init__(gravity, game, floorcol)

    def loadthisscene(self):
        self.createplayer()
        super().loadthisscene()
    def createplayer(self):
        self.player = self.spawn(Player3D("Player", self, self.playersettings))
    def gameloop(self):
        #for i in self.realmap.keys():
            #self.TheGame.DrawSquare(sauce.White, (i[0]*100, i[1]*100), 100, 100)
        super().gameloop()

def LoadMapFile(startingpath, assetname) -> [[]]:
    """Set the starting path to __file__ and the assetname to the map file's name (including extension). This loads map files from the JSON folder. Do make sure all textures from this map exist and are loaded in your scene3d."""
    startingpath = os.path.dirname(startingpath)
    f = open(os.path.join(os.path.join(os.path.join(startingpath,"assets"), "json"), assetname))
    st = f.read()
    f.close()
    dict = json.loads(st)
    return dict["map"]
