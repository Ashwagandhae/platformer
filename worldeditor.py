from sprites import *
import csv


class Editor:
    def __init__(self):
        # get stuff
        if input("Would you like to make a new level (y/n)?\n") == "n":
            self.grid = self.loadLevel(
                ";evels/" + input("What level would you like to load?\n") + ".csv"
            )
            self.height = len(self.grid)
            self.width = len(self.grid[0])
        else:
            self.width = int(input("How many blocks wide should it be?\n"))
            self.height = int(input("How many blocks high should it be?\n"))
            self.grid = []
            for i in range(self.height):
                row = ["a " for j in range(self.width)]
                self.grid.append(row)
        self.blocksize = (WIDTH / self.width, HEIGHT / self.height)
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("Level Editor")
        self.blockList = ["a ", "st", "di", "r ", "s ", "w ", "c "]
        self.currentBlock = 0

    def new(self):
        # create all sprites group
        self.all_sprites = pg.sprite.Group()
        # load level and spawn
        self.spawnLevel(self.grid)
        # RUN
        self.run()

    def run(self):
        self.playing = True
        while self.playing:
            self.events()
            self.update()
            self.draw()

    def events(self):
        # x out of screen
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            if event.type == pg.MOUSEBUTTONUP:
                # self.findClickedBlock(pg.mouse.get_pos())
                index = self.findClickedBlockIndex(pg.mouse.get_pos())
                self.grid[index[1]][index[0]] = self.blockList[self.currentBlock]
                self.spawnLevel(self.grid)
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_0:
                    self.currentBlock = 0
                if event.key == pg.K_1:
                    self.currentBlock = 1
                if event.key == pg.K_2:
                    self.currentBlock = 2
                if event.key == pg.K_3:
                    self.currentBlock = 3
                if event.key == pg.K_4:
                    self.currentBlock = 4
                if event.key == pg.K_5:
                    self.currentBlock = 5
                if event.key == pg.K_6:
                    self.currentBlock = 6
                if event.key == pg.K_7:
                    self.currentBlock = 7
                if event.key == pg.K_RETURN:
                    self.saveLevel(input("What should the level be called?\n"))

    def update(self):
        # update all sprites
        self.all_sprites.update()

    def draw(self):
        # draw all sprites, GUI and background
        self.screen.fill(BACKGROUND_COLOR)
        self.all_sprites.draw(self.screen)
        for sprite in self.all_sprites.sprites():
            pg.draw.rect(self.screen, (255, 255, 255), sprite.rect, 1)
        # update display
        pg.display.update()

    def spawnLevel(self, grid):
        self.all_sprites.empty()
        rowCount = 0
        for row in grid:
            blockCount = 0
            for block in row:
                if not block == "a ":
                    if block == "st":
                        platform = Stone(
                            (
                                blockCount * self.blocksize[0] + self.blocksize[0] / 2,
                                rowCount * self.blocksize[1] + self.blocksize[1] / 2,
                            ),
                            self.blocksize,
                        )
                        self.all_sprites.add(platform)
                    elif block[:2] == "di":
                        platform = Dirt(
                            (
                                blockCount * self.blocksize[0] + self.blocksize[0] / 2,
                                rowCount * self.blocksize[1] + self.blocksize[1] / 2,
                            ),
                            self.blocksize,
                        )
                        self.all_sprites.add(platform)
                    elif block == "s ":
                        platform = Slime(
                            (
                                blockCount * self.blocksize[0] + self.blocksize[0] / 2,
                                rowCount * self.blocksize[1] + self.blocksize[1] / 2,
                            ),
                            self.blocksize,
                        )
                        self.all_sprites.add(platform)
                    elif block == "w ":
                        platform = Water(
                            (
                                blockCount * self.blocksize[0] + self.blocksize[0] / 2,
                                rowCount * self.blocksize[1] + self.blocksize[1] / 2,
                            ),
                            self.blocksize,
                        )
                        self.all_sprites.add(platform)
                    elif block == "r ":
                        platform = Rubber(
                            (
                                blockCount * self.blocksize[0] + self.blocksize[0] / 2,
                                rowCount * self.blocksize[1] + self.blocksize[1] / 2,
                            ),
                            self.blocksize,
                        )
                        self.all_sprites.add(platform)
                    elif block[0] == "d":
                        filename = block.split("_")
                        platform = Door(
                            (
                                blockCount * self.blocksize[0] + self.blocksize[0] / 2,
                                rowCount * self.blocksize[1] + self.blocksize[1] / 2,
                            ),
                            self.blocksize,
                            filename[1],
                        )
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
                                blockCount * self.blocksize[0] + self.blocksize[0] / 2,
                                rowCount * self.blocksize[1] + self.blocksize[1] / 2,
                            ),
                            self.blocksize,
                            path,
                            int(parameters[1]),
                        )
                        self.all_sprites.add(platform)
                    elif block[0] == "c":
                        # create all coins
                        coin = Coin(
                            (
                                blockCount * self.blocksize[0] + self.blocksize[0] / 2,
                                rowCount * self.blocksize[1] + self.blocksize[1] / 2,
                            )
                        )
                        self.all_sprites.add(coin)
                blockCount += 1
            rowCount += 1

    def saveLevel(self, levelname):
        with open("levels/" + levelname + ".csv", mode="w") as newfile:
            writer = csv.writer(
                newfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
            )
            for row in self.grid:
                writer.writerow(row)

    def findClickedBlock(self, xy):
        for sprite in self.all_sprites:
            if sprite.rect.collidepoint(xy):
                return sprite

    def findClickedBlockIndex(self, xy):
        return (
            math.floor(xy[0] / WIDTH * self.width),
            math.floor(xy[1] / HEIGHT * self.height),
        )

    def loadLevel(self, file):
        with open(file, "r") as levelFile:
            reader = csv.reader(levelFile)
            level = []
            for row in reader:
                level.append(row)
            return level


editor = Editor()
editor.new()
pg.quit()
