from settings import *
from utilities import *
from GUI import *
import pygame as pg
from pygame.math import Vector2 as vec
import random, math, time


class Player(pg.sprite.Sprite):
    def __init__(self, game):
        # init pygame
        pg.sprite.Sprite.__init__(self)
        # get game
        self.game = game
        # set direction
        self.direction = "right"
        # create surface to blit on screen - called image for sprite function - load images
        self.imageDict = {
            "right": pg.transform.scale(
                pg.image.load("images/player/player.png"), PLAYER_SIZE
            ),
            "right_ouch": pg.transform.scale(
                pg.image.load("images/player/playerOuch.png"), PLAYER_SIZE
            ),
            "right_blink0": pg.transform.scale(
                pg.image.load("images/player/blink/0.png"), PLAYER_SIZE
            ),
            "right_blink1": pg.transform.scale(
                pg.image.load("images/player/blink/1.png"), PLAYER_SIZE
            ),
            "right_blink2": pg.transform.scale(
                pg.image.load("images/player/blink/2.png"), PLAYER_SIZE
            ),
            "right_blink3": pg.transform.scale(
                pg.image.load("images/player/blink/1.png"), PLAYER_SIZE
            ),
            "right_blink4": pg.transform.scale(
                pg.image.load("images/player/blink/0.png"), PLAYER_SIZE
            ),
            "left": pg.transform.flip(
                pg.transform.scale(
                    pg.image.load("images/player/player.png"), PLAYER_SIZE
                ),
                True,
                False,
            ),
            "left_ouch": pg.transform.flip(
                pg.transform.scale(
                    pg.image.load("images/player/playerOuch.png"), PLAYER_SIZE
                ),
                True,
                False,
            ),
            "left_blink0": pg.transform.flip(
                pg.transform.scale(
                    pg.image.load("images/player/blink/0.png"), PLAYER_SIZE
                ),
                True,
                False,
            ),
            "left_blink1": pg.transform.flip(
                pg.transform.scale(
                    pg.image.load("images/player/blink/1.png"), PLAYER_SIZE
                ),
                True,
                False,
            ),
            "left_blink2": pg.transform.flip(
                pg.transform.scale(
                    pg.image.load("images/player/blink/2.png"), PLAYER_SIZE
                ),
                True,
                False,
            ),
            "left_blink3": pg.transform.flip(
                pg.transform.scale(
                    pg.image.load("images/player/blink/1.png"), PLAYER_SIZE
                ),
                True,
                False,
            ),
            "left_blink4": pg.transform.flip(
                pg.transform.scale(
                    pg.image.load("images/player/blink/0.png"), PLAYER_SIZE
                ),
                True,
                False,
            ),
        }
        self.image = self.imageDict[self.direction]
        self.imageCode = self.direction
        # create rect to collide
        self.rect = self.image.get_rect()
        self.rect.midbottom = intTuple((WIDTH / 2, HEIGHT / 2))
        # set position, velocity, and acceleration
        self.pos = vec(intTuple((WIDTH / 2, HEIGHT / 2)))
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        # set health & invul & healthbar
        self.maxHealth = 100
        self.health = self.maxHealth
        self.healthbar = HealthBar((PLAYER_SIZE[0], 15), self, vec(0, -70), self.game)
        self.game.all_GUI.add(self.healthbar)
        self.invul = 0
        # set how many coins player has
        self.coins = 0
        # check if touching ground
        self.on_ground = False

    def update(self):
        # set image
        self.image = self.imageDict[self.imageCode]
        # count invul
        if self.invul > 0:
            self.invul -= 1
            if self.invul % 2 == 0:
                self.imageCode = self.direction
            else:
                self.imageCode = self.direction + "_ouch"
        # blink if random is true, keep blinking if already started
        if not "blink" in self.imageCode:
            if random.randint(0, 50) == 1:
                self.imageCode = self.direction + "_blink0"
        else:
            frame = int(self.imageCode[-1])
            nextFrame = frame + 1
            # turn around if blink turn
            if nextFrame == 3:
                if not self.direction in self.imageCode:
                    self.imageCode = self.direction + "_blink3"
            if nextFrame == 5:
                self.imageCode = self.direction
            else:
                self.imageCode = self.imageCode.replace(str(frame), str(nextFrame))

        # reset acc and add gravity
        self.acc = vec(0, GRAVITY)
        # make a list of all keys pressed
        keys = pg.key.get_pressed()
        # if left arrow key pressed
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            # acc left
            self.acc.x = -PLAYER_X_ACC
            # set direction and start blink
            if self.direction == "right":
                self.imageCode = self.direction + "_blink0"
                self.direction = "left"
        # if right arrow key pressed
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            # acc right
            self.acc.x = PLAYER_X_ACC
            # set direction and start blink
            if self.direction == "left":
                self.imageCode = self.direction + "_blink0"
                self.direction = "right"
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            # acc down
            self.acc.y = PLAYER_X_ACC * 2
        # decrease acc by friction - friction is fraction of velocity
        self.acc.x += -self.vel.x * PLAYER_X_FRICTION
        # decrease acc by y friction - friction is fraction of velocity
        self.acc.y += -self.vel.y * PLAYER_Y_FRICTION
        # change vel by acc
        self.vel += self.game.dt * self.acc
        # chang pos by vel
        self.pos += self.vel + self.acc / 2
        # change rect by pos
        self.rect.midbottom = self.pos

    def jump(self):
        self.vel.y += -PLAYER_JUMP
        self.on_ground = False

    def damage(self, damage):
        if self.invul == 0:
            self.health -= damage
            self.invul = PLAYER_INVUL
        self.healthbar.changePercent(float(self.health) / self.maxHealth)


class Enemy(pg.sprite.Sprite):
    def __init__(self, game, pos):
        # init pygame
        pg.sprite.Sprite.__init__(self)
        # get game
        self.game = game
        # create surface to blit on screen - called image for sprite function
        self.image = pg.Surface(PLAYER_SIZE)
        self.image.fill((213, 0, 0))
        # create rect to collide
        self.rect = self.image.get_rect()
        self.rect.midbottom = intTuple((WIDTH / 2, HEIGHT / 2))
        # set position, velocity, and acceleration
        self.pos = vec(pos)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        # check if touching ground
        self.on_ground = False
        # enemy variables
        self.jump_speed = 20
        self.damage = 20
        self.knockback = 20

    def update(self):
        # reset acc and add gravity
        self.acc = vec(0, GRAVITY)
        # make a list of all keys pressed
        keys = pg.key.get_pressed()
        # if player pos smaller than pos
        if self.game.player.pos.x < self.pos.x:
            # acc left
            self.acc.x = -1
        # if player pos larger then pos
        if self.game.player.pos.x > self.pos.x:
            # acc right
            self.acc.x = 1
        # if player y pos larger than pos
        if self.game.player.pos.y + self.rect.height < self.pos.y and self.on_ground:
            self.jump()
        # decrease acc by friction - friction is fraction of velocity
        self.acc.x += -self.vel.x * PLAYER_X_FRICTION
        # decrease acc by y friction - friction is fraction of velocity
        self.acc.y += -self.vel.y * PLAYER_Y_FRICTION
        # change vel by acc
        self.vel += self.game.dt * self.acc
        # chang pos by vel
        self.pos += self.vel * self.game.dt + self.acc / 2 * self.game.dt ** 2
        # change rect by pos
        self.rect.midbottom = self.pos

    def jump(self):
        self.vel.y += -self.jump_speed
        self.on_ground = False


class Stone(pg.sprite.Sprite):
    def __init__(self, pos, size):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface(size)
        # self.image = pg.transform.flip(pg.image.load("images/stone" + str(random.randint(0, 1)) + ".png"), bool(random.getrandbits(1)), bool(random.getrandbits(1)))
        self.rect = self.image.get_rect()
        # add image
        if self.rect.width >= self.rect.height:
            for i in range(int(self.rect.width / BLOCK_SIZE)):
                image = pg.transform.flip(
                    pg.image.load("images/stone" + str(random.randint(0, 1)) + ".png"),
                    bool(random.getrandbits(1)),
                    bool(random.getrandbits(1)),
                )
                self.image.blit(image, (i * BLOCK_SIZE, 0))
        else:
            for i in range(int(self.rect.height / BLOCK_SIZE)):
                image = pg.transform.flip(
                    pg.image.load("images/stone" + str(random.randint(0, 1)) + ".png"),
                    bool(random.getrandbits(1)),
                    bool(random.getrandbits(1)),
                )
                self.image.blit(image, (0, i * BLOCK_SIZE))
        self.rect.center = pos
        self.angle = math.degrees(math.atan2(self.rect.height / 2, self.rect.width / 2))

    def collidePlayer(self, game, direction):
        if direction in ("left", "right"):
            game.player.vel.x = 0
        elif direction in ("top", "bottom"):
            game.player.vel.y = 0

    def collideEnemy(self, enemy, direction):
        if direction in ("left", "right"):
            enemy.vel.x = 0
        elif direction in ("top", "bottom"):
            enemy.vel.y = 0


class Dirt(pg.sprite.Sprite):
    def __init__(self, pos, size):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface(size)
        # self.image = pg.transform.flip(pg.image.load("images/stone" + str(random.randint(0, 1)) + ".png"), bool(random.getrandbits(1)), bool(random.getrandbits(1)))
        self.rect = self.image.get_rect()
        # add image
        if self.rect.width >= self.rect.height:
            for i in range(int(self.rect.width / BLOCK_SIZE)):
                image = pg.transform.flip(
                    pg.image.load("images/dirt/dirt .png"),
                    bool(random.getrandbits(1)),
                    bool(random.getrandbits(1)),
                )
                self.image.blit(image, (i * BLOCK_SIZE, 0))
        else:
            for i in range(int(self.rect.height / BLOCK_SIZE)):
                image = pg.transform.flip(
                    pg.image.load("images/dirt/dirt .png"),
                    bool(random.getrandbits(1)),
                    bool(random.getrandbits(1)),
                )
                self.image.blit(image, (0, i * BLOCK_SIZE))
        self.rect.center = pos
        self.angle = math.degrees(math.atan2(self.rect.height / 2, self.rect.width / 2))

    def collidePlayer(self, game, direction):
        if direction in ("left", "right"):
            game.player.vel.x = 0
        elif direction in ("top", "bottom"):
            game.player.vel.y = 0

    def collideEnemy(self, enemy, direction):
        if direction in ("left", "right"):
            enemy.vel.x = 0
        elif direction in ("top", "bottom"):
            enemy.vel.y = 0


class Rubber(pg.sprite.Sprite):
    def __init__(self, pos, size):
        pg.sprite.Sprite.__init__(self)
        # self.image = pg.Surface(size)
        # self.image.blit(pg.transform.flip(pg.image.load("images/rubber.png"), bool(random.getrandbits(1)), False), (0, 0))
        self.image = pg.transform.flip(
            pg.image.load("images/rubber.png"), bool(random.getrandbits(1)), False
        )
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.angle = math.degrees(math.atan2(self.rect.height / 2, self.rect.width / 2))

    def collidePlayer(self, game, direction):
        if direction == "top":
            game.player.vel.y = -RUBBER_BOUNCE
            game.player.on_ground = False
        elif direction == "right":
            game.player.vel.x = RUBBER_BOUNCE
            game.player.on_ground = False
        elif direction == "left":
            game.player.vel.x = -RUBBER_BOUNCE
            game.player.on_ground = False
        elif direction == "bottom":
            game.player.vel.y = RUBBER_BOUNCE
            game.player.on_ground = False

    def collideEnemy(self, enemy, direction):
        if direction == "top":
            enemy.vel.y = -RUBBER_BOUNCE
            enemy.on_ground = False
        elif direction == "right":
            enemy.vel.x = RUBBER_BOUNCE
            enemy.on_ground = False
        elif direction == "left":
            enemy.vel.x = -RUBBER_BOUNCE
            enemy.on_ground = False
        elif direction == "bottom":
            enemy.vel.y = RUBBER_BOUNCE
            enemy.on_ground = False


class Slime(pg.sprite.Sprite):
    def __init__(self, pos, size):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.transform.flip(
            pg.image.load("images/slime.png"), bool(random.getrandbits(1)), False
        )
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def collidePlayer(self, game):
        game.player.vel *= SLIME_FRICTION
        game.player.on_ground = True

    def collideEnemy(self, enemy):
        enemy.vel *= SLIME_FRICTION
        enemy.on_ground = True


class Water(pg.sprite.Sprite):
    def __init__(self, pos, size):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.transform.flip(
            pg.image.load("images/water.png"), bool(random.getrandbits(1)), False
        )
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def collidePlayer(self, game):
        game.player.vel *= WATER_FRICTION
        if self.rect.colliderect(
            pg.Rect(
                game.player.rect.x,
                game.player.rect.y - 20,
                game.player.rect.width,
                game.player.rect.height,
            )
        ):
            game.player.vel += vec(0, -2)
        game.player.on_ground = True

    def collideEnemy(self, enemy):
        enemy.vel *= WATER_FRICTION
        if self.rect.colliderect(
            pg.Rect(
                enemy.rect.x, enemy.rect.y - 20, enemy.rect.width, enemy.rect.height
            )
        ):
            enemy.vel += vec(0, -2)
        enemy.on_ground = True


class Door(pg.sprite.Sprite):
    def __init__(self, pos, size, filename):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface(size)
        self.image.fill(DOOR_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.filename = filename

    def collidePlayer(self, game):
        game.new("levels/" + self.filename + ".csv")

    def collideEnemy(self, enemy):
        pass


class Coin(pg.sprite.Sprite):
    def __init__(self, pos):
        pg.sprite.Sprite.__init__(self)
        self.imageList = []
        for i in range(0, 8):
            image = pg.image.load("images/coin/" + str(i) + ".png")
            self.imageList.append(pg.transform.scale(image, (COIN_SIZE, COIN_SIZE)))
        self.imageIndex = 0
        self.lastImageChange = time.time()
        self.imageSpeed = 0.06
        self.image = self.imageList[self.imageIndex]
        self.rect = pg.Rect(0, 0, COIN_HITBOX, COIN_HITBOX)
        self.rect.center = pos

    def update(self):
        if time.time() > self.lastImageChange + self.imageSpeed:
            self.lastImageChange = time.time()
            self.imageIndex += 1
            if self.imageIndex > len(self.imageList) - 1:
                self.imageIndex = 0
            self.image = self.imageList[self.imageIndex]


class MovingStone(Stone):
    def __init__(self, pos, size, path, speed):
        Stone.__init__(self, pos, size)
        self.image = pg.Surface(size)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.path = path
        self.image.fill(MOVESTONE_COLOR)
        self.speed = speed
        self.targetPoint = self.path[0]

    def update(self):
        direction = vec(self.targetPoint - vec(self.rect.center)).normalize()
        self.rect.center = vec(self.rect.center) + direction * self.speed
        if self.targetPoint.distance_to(self.rect.center) < self.speed * 1.5:
            if self.path.index(self.targetPoint) + 1 == len(self.path):
                self.targetPoint = self.path[0]
            else:
                self.targetPoint = self.path[self.path.index(self.targetPoint) + 1]
