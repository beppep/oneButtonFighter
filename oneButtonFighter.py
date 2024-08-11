import pygame
import time
import random
import os
import math
import pygame_gui

clock = pygame.time.Clock()
ASSET_FOLDER_NAME = "OBFassets"
SOUND_PATH = os.path.join(ASSET_FOLDER_NAME, "sounds")
pygame.init()
pygame.display.init()

infoObject = pygame.display.Info()
SCREENSIZE = (infoObject.current_w, infoObject.current_h)
CANVASSIZE = (128, 72)
FRAMERATE = 60

gameDisplay = pygame.display.set_mode(SCREENSIZE)
#gameDisplay = pygame.display.set_mode((infoObject.current_w, infoObject.current_h), pygame.FULLSCREEN)
pygame.display.set_caption("One Button Fighter")
#pygame.display.set_icon(pygame.image.load(os.path.join("OBFassets", "textures", "player", "player.png")))

def loadImage(path):
    image = pygame.image.load(os.path.join(ASSET_FOLDER_NAME, "textures", path))
    
    return image

def load_animation(animation_name, nr):
    anim = []
    for i in range(nr):
        image = pygame.image.load(os.path.join(ASSET_FOLDER_NAME, "textures","player", animation_name, str(i)+".png"))
        anim.append(image)
    #cls.animations[animation_name] = anim
    return anim

class Sound():
    pygame.font.init() # you have to call this at the start, 
                           # if you want to use this module.
    pygame.mixer.init(buffer=32)

    crushSounds = []
    wallSounds = []
    for i in range(10):
        crushSounds.append(pygame.mixer.Sound(os.path.join(SOUND_PATH, "crush"+str(i+1)+".wav")))
        crushSounds[i].set_volume(0.1)
    for i in range(4):
        wallSounds.append(pygame.mixer.Sound(os.path.join(SOUND_PATH, "wall"+str(i+1)+".wav")))
        wallSounds[i].set_volume(0.1)

    pygame.mixer.music.load(os.path.join(SOUND_PATH, "crushing music.wav")) #must be wav 16bit and stuff?
    pygame.mixer.music.set_volume(0.01)
    pygame.mixer.music.play(-1)

def playCrushSound():
    sound = random.choice(Sound.crushSounds)
    #sound.set_volume(vol*(i+1))
    sound.play()
def playWallSound():
    sound = random.choice(Sound.wallSounds)
    #sound.set_volume(vol*(i+1))
    sound.play()

class Game():

    def __init__(self):
        self.canvas = pygame.Surface((128,72))
        self.players = [Player(0), Player(1)]
        self.screenshake = 0
        self.currentScreenShake = (0,0)
        self.screenshakeDir = (0,0)
        self.freeze_frames = 0

    def update(self):

        # SCREEENSHAKE
        if self.freeze_frames:
            self.freeze_frames -= 1
        else:
            pressed = pygame.key.get_pressed()
            for i in range(2):
                AI = 0
                if AI and i==1: 
                     self.players[i].update(random.random() < 0.5)
                else:
                    self.players[i].update(pressed[self.player_controls[i][0]]) # random order?

        if self.screenshake>0:
            ampl = 2 
            self.currentScreenShake = [(random.random()-0.5)*2*self.screenshake*ampl, ((random.random()-0.5)*2*self.screenshake*ampl)]
            self.currentScreenShake[0] += self.screenshake*ampl*self.screenshakeDir
            self.screenshake -= 0.5
        else:
            self.screenshake = 0

    def draw(self):
        self.canvas.fill((110,110,110))
        for i in range(2):
            self.players[i].draw()

    def shakeScreen(self, amount, side):
        self.screenshake = max(self.screenshake, amount)
        self.screenshakeDir = side

    def add_lag(self, nr):
        self.freeze_frames = max(self.freeze_frames, nr)

    player_controls = [[
        pygame.K_SPACE
    ],[
        pygame.K_RETURN,
    ]]

class Player():

    animations = {}
    for i in [("idle",1), ("windup",3), ("charging",4), ("shield",1), ("punch",5), ("hurt",3)]:
        animations[i[0]] = load_animation(*i)

    def __init__(self, side):
        self.side = side

        self.hp = 1
        self.stun = 0

        self.state = "idle"
        self.stateTimer = 0

    def update_state(self, nr):
        self.state = nr
        self.stateTimer = 0
        self.update_animation(0)

    def update_animation(self, nr):
        if nr > len(self.animations[self.state]) -1:
            nr = len(self.animations[self.state]) -1
        self.image = self.animations[self.state][nr]

    def update(self, pressed):
        self.stateTimer += 1
        match self.state:
            case "idle":
                self.update_animation(0)
                if pressed:
                    self.update_state("windup")
            case "windup":
                self.update_animation(self.stateTimer*3//12)
                if self.stateTimer == 11:
                    if pressed:
                        self.update_state("charging")
                    else:
                        self.update_state("shield")
            case "charging":
                self.update_animation(self.stateTimer*4//140)
                if self.stateTimer == 139 or not pressed:
                    self.update_state("punch")
            case "shield":
                self.update_animation(0)
                if self.stateTimer > 10 and pressed:
                    self.update_state("idle") #change this
            case "punch":
                self.update_animation(self.stateTimer*5//21)
                if self.stateTimer == 16:
                    game.players[not self.side].hurt(0.1, 14)
                if self.stateTimer == 40:
                    self.update_state("idle")
            case "hurt":
                self.update_animation(self.stateTimer*3//(self.stun+1))
                if self.stateTimer >= self.stun:
                    self.update_state("idle")

    def hurt(self, dmg, stun):
        if self.state in ["shield","charging"]:
            self.hp -= dmg/10
            playWallSound()
            game.add_lag(10)
            game.shakeScreen(10, self.side - 0.5)
        else:
            self.hp = self.hp - dmg
            self.update_state("hurt")
            self.stun = stun
            playCrushSound()
            game.add_lag(10)
            game.shakeScreen(10, self.side - 0.5)

    def draw(self):
        blitting_pos = (self.side*64, 0)
        if self.side == 1:
            img = pygame.transform.flip(self.image, True, False)
        else:
            img = self.image
        game.canvas.blit(img, blitting_pos)



game = Game()

jump_out = False
while jump_out == False:
    time_delta = clock.tick(FRAMERATE)/1000.0
    
    #pygame.event.get()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            jump_out = True
        
    game.update()
    game.draw()
    

    gameDisplay.blit(pygame.transform.scale(game.canvas,SCREENSIZE), game.currentScreenShake)
    pygame.display.flip()
    
    
pygame.quit()
#quit() #bad for pyinstaller
