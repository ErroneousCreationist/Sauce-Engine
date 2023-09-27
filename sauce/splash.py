from . import sauce

class IntroScene(sauce.TimedScene):
    """This is a default splash screen, you need an image called 'splash.png' in assets/Images/splash.png also put __file__ into the 'myfile' parameter"""
    def __init__(self, gravity, game, backgroundcol, scenetime, nextsceneindex, myfile) -> None:
        super().__init__(gravity, game, backgroundcol, scenetime, nextsceneindex)
        self.timestuff = scenetime
        self.f = myfile
    def loadthisscene(self):
        introframes = [
            sauce.AnimationFrame(0, 0.05, scale=(0,0), offset=(0,-300)),
            sauce.AnimationFrame(0, 0.1, scale=(0.05,0.05), offset=(0,-284)),
            sauce.AnimationFrame(0.1, 0.15, scale=(0.1,0.1), offset=(0,-268)),
            sauce.AnimationFrame(0.15, 0.2, scale=(0.15,0.15), offset=(0,-253)),
            sauce.AnimationFrame(0.2, 0.25, scale=(0.2,0.2), offset=(0,-237)),
            sauce.AnimationFrame(0.25, 0.3, scale=(0.25,0.25), offset=(0,-221)),
            sauce.AnimationFrame(0.3, 0.35, scale=(0.3,0.3), offset=(0,-205)),
            sauce.AnimationFrame(0.35, 0.4, scale=(0.35,0.35), offset=(0,-189)),
            sauce.AnimationFrame(0.4, 0.45, scale=(0.4,0.4), offset=(0,-174)),
            sauce.AnimationFrame(0.45, 0.5, scale=(0.45,0.45), offset=(0,-158)),
            sauce.AnimationFrame(0.5, 0.55, scale=(0.5,0.5), offset=(0,-142)),
            sauce.AnimationFrame(0.55, 0.6, scale=(0.55,0.55), offset=(0,-126)),
            sauce.AnimationFrame(0.6, 0.65, scale=(0.6,0.6), offset=(0,-111)),
            sauce.AnimationFrame(0.65, 0.7, scale=(0.65,0.65), offset=(0,-95)),
            sauce.AnimationFrame(0.7, 0.75, scale=(0.7,0.7), offset=(0,-79)),
            sauce.AnimationFrame(0.75, 0.8, scale=(0.75,0.75), offset=(0,-63)),
            sauce.AnimationFrame(0.8, 0.85, scale=(0.8,0.8), offset=(0,-47)),
            sauce.AnimationFrame(0.85, 0.9, scale=(0.85,0.85), offset=(0,-32)),
            sauce.AnimationFrame(0.9, 0.95, scale=(0.925,0.925), offset=(0,-16)),
            sauce.AnimationFrame(0.95, 1, scale=(1,1), offset=(0,0)),
            sauce.AnimationFrame(1, self.timestuff, scale=(1,1), offset=(0,0)),
        ]

        introanimation = sauce.AnimationController(sauce.AnimationFrame(0,0,scale=sauce.NormalScale), [sauce.Animation(introframes,self.timestuff)], 0)
        self.spawn(sauce.GraphicalObject("introsplash", (self.TheGame.display_width/2, self.TheGame.display_height/2), 0, sauce.NormalScale, self, sauce.FindAsset(sauce.assetpathImages, self.f, "splash.png"),anim=introanimation))

        super().loadthisscene()
