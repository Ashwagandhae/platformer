from settings import *
from sprites import *
import pygame as pg
import math
import csv


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True

    def new(self, filename):
        # create camera and offset
        self.cameraPos = vec(intTuple((WIDTH / 2, HEIGHT / 2)))
        self.cameraVel = vec(0, 0)
        self.cameraOffset = vec(0, 0)
        # create all sprites group
        self.all_sprites = pg.sprite.Group()
        # load level and spawn
        self.spawnLevel(self.loadLevel(filename))
        # create all gui
        self.all_GUI = pg.sprite.Group()
        # create player
        self.player = Player(self)
        self.all_sprites.add(self.player)
        # create enemy
        self.all_enemies = pg.sprite.Group()
        self.enemy = Enemy(self, (100, 300))
        self.all_enemies.add(self.enemy)
        self.all_sprites.add(self.enemy)
        # RUN
        self.run()

    def run(self):
        self.playing = True
        while self.playing:
            # set frame rate
            # set delta time
            self.dt = self.clock.tick(FRAMERATE) / 300
            self.clock.tick(FRAMERATE)
            self.dt = 1
            self.events()
            self.update()
            self.draw()

    def events(self):
        # x out of screen
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
        # move camera
        if self.player.pos.x > self.cameraPos.x:
            self.cameraVel.x += abs(self.player.vel.x) * CAMERA_SPEED
        elif self.player.pos.x < self.cameraPos.x:
            self.cameraVel.x += abs(self.player.vel.x) * -CAMERA_SPEED
        if self.player.pos.y > self.cameraPos.y:
            self.cameraVel.y += abs(self.player.vel.y) * CAMERA_SPEED
        elif self.player.pos.y < self.cameraPos.y:
            self.cameraVel.y += abs(self.player.vel.y) * -CAMERA_SPEED
        self.cameraVel *= CAMERA_FRICTION
        self.cameraPos += self.cameraVel

        # make a list of all keys pressed
        keys = pg.key.get_pressed()
        # jump if up arrow pressed
        if keys[pg.K_UP] or keys[pg.K_w] or keys[pg.K_SPACE]:
            # if player on ground
            if self.player.on_ground:
                self.player.jump()

    def update(self):
        # save prev pos
        prevPos = vec(self.player.pos)
        # set correction
        correction = False
        # update all sprites
        self.all_sprites.update()
        # collide platforms
        collisions = pg.sprite.spritecollide(self.player, self.all_platforms, False)
        if len(collisions) > 0:
            for collision in collisions:
                diff = ((prevPos) - vec(0, self.player.rect.height / 2)) - vec(
                    collision.rect.center
                )
                angle = -math.degrees(math.atan2(diff.y, diff.x))
                # if on top
                if angle < 180 - collision.angle and angle > collision.angle:
                    self.player.pos.y = collision.rect.top
                    self.player.on_ground = True
                    # set y vel
                    collision.collidePlayer(self, "top")
                else:
                    self.player.on_ground = False
                    # if on right
                    if angle < collision.angle and angle > -collision.angle:
                        self.player.pos.x = (
                            collision.rect.right + self.player.rect.width / 2
                        )
                        self.player.vel.x = 0
                        # set x vel
                        collision.collidePlayer(self, "right")
                    # if on left
                    elif (
                        angle < -180 + collision.angle or angle > 180 - collision.angle
                    ):
                        self.player.pos.x = (
                            collision.rect.left - self.player.rect.width / 2
                        )
                        self.player.vel.x = 0
                        # set x vel
                        collision.collidePlayer(self, "left")
                    # if on bottom
                    elif angle < collision.angle and angle > -180 + collision.angle:
                        self.player.pos.y = (
                            collision.rect.bottom + self.player.rect.height
                        )
                        self.player.vel.y = 0
                        # set y vel
                        collision.collidePlayer(self, "bottom")
        # collide floats
        collisions = pg.sprite.spritecollide(self.player, self.all_floats, False)
        if len(collisions) > 0:
            for collision in collisions:
                collision.collidePlayer(self)
        # collide enemies
        for enemy in self.all_enemies.sprites():
            prevPos = vec(enemy.pos)
            collisions = pg.sprite.spritecollide(enemy, self.all_platforms, False)
            if len(collisions) > 0:
                for collision in collisions:
                    diff = ((prevPos) - vec(0, enemy.rect.height / 2)) - vec(
                        collision.rect.center
                    )
                    angle = -math.degrees(math.atan2(diff.y, diff.x))
                    # if on top
                    if angle < 180 - collision.angle and angle > collision.angle:
                        enemy.pos.y = collision.rect.top
                        enemy.on_ground = True
                        # set y vel
                        collision.collideEnemy(enemy, "top")
                    else:
                        enemy.on_ground = False
                        # if on right
                        if angle < collision.angle and angle > -collision.angle:
                            enemy.pos.x = collision.rect.right + enemy.rect.width / 2
                            enemy.vel.x = 0
                            # set x vel
                            collision.collideEnemy(enemy, "right")
                        # if on left
                        elif (
                            angle < -180 + collision.angle
                            or angle > 180 - collision.angle
                        ):
                            enemy.pos.x = collision.rect.left - enemy.rect.width / 2
                            enemy.vel.x = 0
                            # set x vel
                            collision.collideEnemy(enemy, "left")
                        # if on bottom
                        elif angle < collision.angle and angle > -180 + collision.angle:
                            enemy.pos.y = collision.rect.bottom + enemy.rect.height
                            enemy.vel.y = 0
                            # set y vel
                            collision.collideEnemy(enemy, "bottom")
            # collide floats
            collisions = pg.sprite.spritecollide(enemy, self.all_floats, False)
            if len(collisions) > 0:
                for collision in collisions:
                    collision.collideEnemy(enemy)

        # collide coins
        collisions = pg.sprite.spritecollide(self.player, self.all_coins, True)
        if len(collisions) > 0:
            # add to coin count
            self.player.coins += len(collisions)
        # collide player with enemeis
        collisions = pg.sprite.spritecollide(self.player, self.all_enemies, False)
        for collision in collisions:
            self.player.damage(collision.damage)
            if self.player.invul > 0:
                knockbackVec = vec(self.player.pos - enemy.pos)
                if knockbackVec.length() == 0:
                    knockbackVec = vec(0, -1)
                else:
                    knockbackVec = knockbackVec.normalize()
                self.player.vel = knockbackVec * enemy.knockback

        # correction and camera movement
        if correction:
            self.player.vel.y -= RUBBER_HEIGHT_CORRECTION
        self.cameraOffset = vec(
            intTuple((-self.cameraPos.x + WIDTH / 2, -self.cameraPos.y + HEIGHT / 2))
        )
        self.all_GUI.update()

    def draw(self):
        # apply offset
        for sprite in self.all_sprites.sprites() + self.all_GUI.sprites():
            sprite.rect.center += self.cameraOffset
        # draw all sprites, GUI and background
        self.screen.fill(BACKGROUND_COLOR)
        self.all_sprites.draw(self.screen)
        self.all_GUI.draw(self.screen)
        # update display
        pg.display.update()
        # apply offset
        for sprite in self.all_sprites.sprites() + self.all_GUI.sprites():
            sprite.rect.center -= self.cameraOffset

    def loadLevel(self, file):
        with open(file, "r") as levelFile:
            reader = csv.reader(levelFile)
            level = []
            for row in reader:
                level.append(row)
            return level

    def spawnLevel(self, grid):
        self.all_platforms = pg.sprite.Group()
        self.all_floats = pg.sprite.Group()
        self.all_coins = pg.sprite.Group()
        rowCount = 0
        for row in grid:
            blockCount = 0
            for block in row:
                if not block == "a ":
                    if block == "st":
                        platformGroup = [(blockCount, rowCount)]
                        row[blockCount] = "a "
                        i = blockCount + 1
                        while i < len(row) and row[i] == "st":
                            platformGroup.append((i, rowCount))
                            row[i] = "a "
                            i += 1
                        # check for y direction
                        if len(platformGroup) == 1:
                            j = rowCount + 1
                            while j < len(grid) and grid[j][blockCount] == "st":
                                platformGroup.append((blockCount, j))
                                grid[j][blockCount] = "a "
                                j += 1
                            platform = Stone(
                                (
                                    blockCount * BLOCK_SIZE + BLOCK_SIZE / 2,
                                    (platformGroup[-1][1] + platformGroup[0][1])
                                    / 2
                                    * BLOCK_SIZE
                                    + BLOCK_SIZE / 2,
                                ),
                                (BLOCK_SIZE, len(platformGroup) * BLOCK_SIZE),
                            )
                        else:
                            platform = Stone(
                                (
                                    (platformGroup[-1][0] + platformGroup[0][0])
                                    / 2
                                    * BLOCK_SIZE
                                    + BLOCK_SIZE / 2,
                                    rowCount * BLOCK_SIZE + BLOCK_SIZE / 2,
                                ),
                                (len(platformGroup) * BLOCK_SIZE, BLOCK_SIZE),
                            )
                        self.all_platforms.add(platform)
                        self.all_sprites.add(platform)
                    elif block == "di":
                        platform = self.makeGroup(
                            block, grid, row, blockCount, rowCount, "di"
                        )
                        self.all_platforms.add(platform)
                        self.all_sprites.add(platform)
                    elif block == "s ":
                        platform = Slime(
                            (
                                blockCount * BLOCK_SIZE + BLOCK_SIZE / 2,
                                rowCount * BLOCK_SIZE + BLOCK_SIZE / 2,
                            ),
                            (BLOCK_SIZE, BLOCK_SIZE),
                        )
                        self.all_floats.add(platform)
                        self.all_sprites.add(platform)
                    elif block == "w ":
                        platform = Water(
                            (
                                blockCount * BLOCK_SIZE + BLOCK_SIZE / 2,
                                rowCount * BLOCK_SIZE + BLOCK_SIZE / 2,
                            ),
                            (BLOCK_SIZE, BLOCK_SIZE),
                        )
                        self.all_floats.add(platform)
                        self.all_sprites.add(platform)
                    elif block == "r ":
                        platform = Rubber(
                            (
                                blockCount * BLOCK_SIZE + BLOCK_SIZE / 2,
                                rowCount * BLOCK_SIZE + BLOCK_SIZE / 2,
                            ),
                            (BLOCK_SIZE, BLOCK_SIZE),
                        )
                        self.all_platforms.add(platform)
                        self.all_sprites.add(platform)
                    elif block[:2] == "do":
                        filename = block.split("_")
                        platform = Door(
                            (
                                blockCount * BLOCK_SIZE + BLOCK_SIZE / 2,
                                rowCount * BLOCK_SIZE + BLOCK_SIZE / 2,
                            ),
                            (BLOCK_SIZE, BLOCK_SIZE),
                            filename[1],
                        )
                        self.all_floats.add(platform)
                        self.all_sprites.add(platform)
                    elif block[0] == "m":
                        parameters = block.split("_")
                        path = []
                        for i in range(2, len(parameters)):
                            string = parameters[i].split(";")
                            point = vec(int(string[0]), int(string[1]))
                            path.append(point)
                        platform = MovingStone(
                            (
                                blockCount * BLOCK_SIZE + BLOCK_SIZE / 2,
                                rowCount * BLOCK_SIZE + BLOCK_SIZE / 2,
                            ),
                            (BLOCK_SIZE * 3, BLOCK_SIZE),
                            path,
                            int(parameters[1]),
                        )
                        self.all_platforms.add(platform)
                        self.all_sprites.add(platform)
                    elif block[0] == "c":
                        # create all coins
                        coin = Coin(
                            (
                                blockCount * BLOCK_SIZE + BLOCK_SIZE / 2,
                                rowCount * BLOCK_SIZE + BLOCK_SIZE / 2,
                            )
                        )
                        self.all_coins.add(coin)
                        self.all_sprites.add(coin)
                blockCount += 1
            rowCount += 1

    def makeGroup(self, block, grid, row, blockCount, rowCount, blockName):
        if block == blockName:
            platformGroup = [(blockCount, rowCount)]
            row[blockCount] = "a "
            i = blockCount + 1
            while i < len(row) and row[i] == blockName:
                platformGroup.append((i, rowCount))
                row[i] = "a "
                i += 1
            # check for y direction
            if len(platformGroup) == 1:
                j = rowCount + 1
                while j < len(grid) and grid[j][blockCount] == blockName:
                    platformGroup.append((blockCount, j))
                    grid[j][blockCount] = "a "
                    j += 1
                platform = Dirt(
                    (
                        blockCount * BLOCK_SIZE + BLOCK_SIZE / 2,
                        (platformGroup[-1][1] + platformGroup[0][1]) / 2 * BLOCK_SIZE
                        + BLOCK_SIZE / 2,
                    ),
                    (BLOCK_SIZE, len(platformGroup) * BLOCK_SIZE),
                )
            else:
                platform = Dirt(
                    (
                        (platformGroup[-1][0] + platformGroup[0][0]) / 2 * BLOCK_SIZE
                        + BLOCK_SIZE / 2,
                        rowCount * BLOCK_SIZE + BLOCK_SIZE / 2,
                    ),
                    (len(platformGroup) * BLOCK_SIZE, BLOCK_SIZE),
                )
            return platform

    def start(self):
        pass

    def end(self):
        pass


game = Game()
game.start()
while game.running:
    game.new("levels/level4.csv")
    game.end()
pg.quit()

# random stuff
# create grid
"""grid = []
for i in range(int(HEIGHT/BLOCK_SIZE)):
    row = []
    for i in range(int(WIDTH/BLOCK_SIZE)):
        chance = random.randint(0, 50)
        if chance >= 0 and chance <= 3:
            for ii in range(random.randint(2, 4)):
                row.append("s")
                i += 1
        elif chance == 6:
            for ii in range(random.randint(3, 5)):
                row.append("c")
                i += 1
        elif chance == 7:
            row.append("r")
        else:
            row.append("")
    grid.append(row)"""
"""rowCount = 0
        for row in grid:
            blockCount = 0
            for block in row:
                if not block == "a ": 
                    if block == "st":
                        platform = Stone((blockCount*BLOCK_SIZE + BLOCK_SIZE/2, rowCount*BLOCK_SIZE + BLOCK_SIZE/2), (BLOCK_SIZE, BLOCK_SIZE))
                        self.all_platforms.add(platform)
                        self.all_sprites.add(platform)
                    elif block[:2] == "di":
                        platform = Dirt((blockCount*BLOCK_SIZE + BLOCK_SIZE/2, rowCount*BLOCK_SIZE + BLOCK_SIZE/2), (BLOCK_SIZE, BLOCK_SIZE), block[2])
                        self.all_platforms.add(platform)
                        self.all_sprites.add(platform)
                    elif block == "s ":
                        platform = Slime((blockCount*BLOCK_SIZE + BLOCK_SIZE/2, rowCount*BLOCK_SIZE + BLOCK_SIZE/2), (BLOCK_SIZE, BLOCK_SIZE))
                        self.all_floats.add(platform)
                        self.all_sprites.add(platform)
                    elif block == "w ":
                        platform = Water((blockCount*BLOCK_SIZE + BLOCK_SIZE/2, rowCount*BLOCK_SIZE + BLOCK_SIZE/2), (BLOCK_SIZE, BLOCK_SIZE))
                        self.all_floats.add(platform)
                        self.all_sprites.add(platform)
                    elif block == "r ":
                        platform = Rubber((blockCount*BLOCK_SIZE + BLOCK_SIZE/2, rowCount*BLOCK_SIZE + BLOCK_SIZE/2), (BLOCK_SIZE, BLOCK_SIZE))
                        self.all_platforms.add(platform)
                        self.all_sprites.add(platform)
                    elif block[0] == "d":
                        filename = block.split("_")
                        platform = Door((blockCount*BLOCK_SIZE + BLOCK_SIZE/2, rowCount*BLOCK_SIZE + BLOCK_SIZE/2), (BLOCK_SIZE, BLOCK_SIZE), filename[1])
                        self.all_floats.add(platform)
                        self.all_sprites.add(platform)
                    elif block[0] == "m":
                        parameters = block.split("_")
                        path = []
                        for i in range(2, len(parameters)):
                            string = parameters[i].split(";")
                            point = vec(int(string[0]), int(string[1]))
                            path.append(point)
                        platform = MovingStone((blockCount*BLOCK_SIZE + BLOCK_SIZE/2, rowCount*BLOCK_SIZE + BLOCK_SIZE/2), (BLOCK_SIZE*3, BLOCK_SIZE), path, int(parameters[1]))
                        self.all_platforms.add(platform)
                        self.all_sprites.add(platform)
                    elif block[0] == "c":
                        #create all coins
                        coin = Coin((blockCount*BLOCK_SIZE + BLOCK_SIZE/2, rowCount*BLOCK_SIZE + BLOCK_SIZE/2))
                        self.all_coins.add(coin)
                        self.all_sprites.add(coin)
                blockCount += 1
            rowCount += 1"""
