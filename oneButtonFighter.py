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

def load_animation(animation_name, nr = None):
    da_path = os.path.join(ASSET_FOLDER_NAME, "textures","player", animation_name)
    if nr==None:
        lst = os.listdir(da_path)
        nr = len(lst)
    anim = []
    for i in range(nr):
        image = pygame.image.load(os.path.join(da_path, str(i)+".png"))
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
        self.projectiles = []

    def update(self):

        # SCREEENSHAKE
        if self.freeze_frames:
            self.freeze_frames -= 1
        else:
            pressed = pygame.key.get_pressed()
            for i in range(2):
                AI = 1
                if AI and i==1: 
                     self.players[i].update(random.random() < 0.5)
                else:
                    self.players[i].update(pressed[self.player_controls[i][0]]) # random order?

            for i in self.projectiles:
                i.update()

        if self.screenshake>0:
            ampl = 2 
            self.currentScreenShake = [(random.random()-0.5)*2*self.screenshake*ampl, ((random.random()-0.5)*2*self.screenshake*ampl)]
            self.currentScreenShake[0] += self.screenshake*ampl*self.screenshakeDir
            self.screenshake -= 0.5
        else:
            self.screenshake = 0

    def draw(self):
        if self.freeze_frames:
            color = (150,110,110)
        else:
            color = (110,110,110)
        self.canvas.fill(color)
        for i in range(2):
            self.players[i].draw()

        for i in self.projectiles:
            i.draw()

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
    da_path = os.path.join(ASSET_FOLDER_NAME, "textures","player")
    all_animation_names = os.listdir(da_path)
    for i in all_animation_names:
        animations[i] = load_animation(i)

    def __init__(self, side):
        self.side = side

        self.hp = 1
        self.stun = 0

        self.state = "idle"
        self.stateTimer = 0

        self.state_after_stun = "idle"
        self.gun_ammo = 1

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
                self.state_after_stun = "idle"
                if pressed:
                    self.update_state("windup")
            case "windup":
                self.update_animation(self.stateTimer*3//10)
                if self.stateTimer == 9:
                    if pressed:
                        self.update_state("charging")
                    else:
                        self.update_state("shield")
            case "charging":
                self.update_animation(self.stateTimer*4//160)
                if not pressed:
                    if self.stateTimer < 120:
                        self.update_state("punch")
                    else:
                        self.update_state("firepunch")
            case "shield":
                self.update_animation(0)
                if self.stateTimer > 10 and pressed:
                    self.update_state("idle") #change this
            case "punch":
                self.update_animation(self.stateTimer*5//20)
                if self.stateTimer == 13:
                    game.players[not self.side].hurt(0.1, 14)
                    if pressed:
                        self.update_state("handspike")
                if self.stateTimer == 40:
                    self.update_state("idle")
            case "firepunch":
                self.update_animation(self.stateTimer*5//25)
                if self.stateTimer == 16:
                    game.players[not self.side].hurt(0.15, 24)
                if self.stateTimer == 45:
                    self.update_state("idle")
            case "hurt":
                self.update_animation(self.stateTimer*3//(self.stun+1))
                if self.stateTimer >= self.stun:
                    self.update_state(self.state_after_stun)
                if self.stateTimer == int(self.stun*0.66) and pressed:
                    self.update_state("skullbash")
            case "skullbash":
                self.update_animation(self.stateTimer*4//32)
                if self.stateTimer == 18:
                    dmg = self.stun * 0.005 + 0.05
                    game.players[not self.side].hurt(dmg, 10 + self.stun)
                    #game.players[not self.side].hurt(0.1, 14)
                if self.stateTimer == 40:
                    self.update_state(self.state_after_stun)
            case "handspike":
                self.update_animation(self.stateTimer*4//30)
                if self.stateTimer == 8:
                    game.players[not self.side].hurt(0.05, 4)
                    self.state_after_stun = "spikeidle"
                    self.hurt(0.05, 0)
                if self.stateTimer >= 30:
                    self.update_state("spikeidle")
            case "spikeidle":
                self.update_animation((self.stateTimer//6) %2)
                self.state_after_stun = "spikeidle"
                if pressed:
                    self.update_state("drill")
            case "drill":
                self.update_animation(self.stateTimer*4//40)
                if self.stateTimer == 10 and not pressed:
                    self.update_state("spiketoss")
                if self.stateTimer in [23,30,37]:
                    game.players[not self.side].hurt(0.02, 0)
                if self.stateTimer >= 40:
                    if pressed:
                        self.stateTimer = 20
                    else:
                        self.update_state("spikeidle")
            case "spiketoss":
                self.update_animation(self.stateTimer*3//20)
                if self.stateTimer == 7:
                    game.projectiles.append(SpikeProjectile(self.side))
                    self.state_after_stun = "idle"
                if self.stateTimer == 20:
                    self.update_state("idle")
            case "gunidle":
                self.update_animation(0)
                self.state_after_stun = "gunidle"
                if pressed:
                    if self.gun_ammo > 0:
                        self.update_state("gunshot")
                    else:
                        self.update_state("reload")
            case "gunshot":
                self.update_animation(self.stateTimer*2//10)
                if self.stateTimer == 2:
                    self.gun_ammo -= 1
                    game.players[not self.side].hurt(0.2, 20)
                if self.stateTimer == 25:
                    self.update_state("gunidle")
            case "reload":
                self.update_animation(self.stateTimer*5//50)
                if self.stateTimer == 30:
                    self.gun_ammo = 1
                if self.stateTimer == 50:
                    self.update_state("gunidle")

    def hurt(self, dmg, stun):
        if self.state in ["shield","charging"]:
            self.hp -= dmg/10
            playWallSound()
            game.add_lag(stun//2+1)
            game.shakeScreen(stun//2+1, self.side - 0.5)
        else:
            self.hp = self.hp - dmg
            if stun > 0:
                self.update_state("hurt")
                self.stun = stun
            playCrushSound()
            game.add_lag(stun//2+1)
            game.shakeScreen(stun//2+1, self.side - 0.5)

    def draw(self):
        blitting_pos = (self.side*64, 0)
        if self.side == 1:
            img = pygame.transform.flip(self.image, True, False)
        else:
            img = self.image
        pygame.draw.rect(game.canvas, (40,20,20), (blitting_pos[0], blitting_pos[1], 64, 2))
        pygame.draw.rect(game.canvas, (20,180,20), (blitting_pos[0], blitting_pos[1], 64*self.hp, 2))
        game.canvas.blit(img, blitting_pos)

class Projectile():

    def __init__(self, side):
        self.age = 0
        self.side = side

    def update(self):
        pass

    def draw(self):
        pass

class SpikeProjectile(Projectile):

    def __init__(self, side):
        super().__init__(side)
        self.image = loadImage("spike.png")
        if self.side == 1:
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self):
        self.age += 1

        if self.age >= 20:
            if self in game.projectiles:
                game.projectiles.remove(self)
            game.players[not self.side].hurt(0.05, 4)

    def draw(self):
        x = 64 + (self.age - 5)*2 * (self.side-0.5)*-2
        y = 5 + (self.age-12)**2 * 0.2
        game.canvas.blit(self.image, (x-16, y-16))


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
