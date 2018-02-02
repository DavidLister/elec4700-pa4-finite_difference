# finite_difference.py
#
# For ELEC 4700 - pa4
# David Lister
# February 2018
#

# self.grid[y][x]

import random
from PIL import Image
import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt




def closerTo(x1, y1, x2, y2, res):
    return (x1 - x2)**2 + (y1 - y2)**2 <= 0.5 * res **2

class Space:

    def __init__(self, x, y, res):
        self.grid = [[0 for i in range(0, x, res)] for j in range(0, y, res)]
        self.res = res
        self.x = x
        self.y = y
        self.objects = []
        self.oldGrid = [[0 for i in range(0, x, res)] for j in range(0, y, res)]
        self.objectMask = [[0 for i in range(0, x, res)] for j in range(0, y, res)]
        self.deltaMask = [[0 for i in range(0, x, res)] for j in range(0, y, res)]
        self.delta = [[0 for i in range(0, x, res)] for j in range(0, y, res)]
        self.xRange = len(self.grid[0])
        self.yRange = len(self.grid)
        self.maxV = 0
    
    def addObject(self, obj):
        if obj.fits(self.x, self.y):
            self.objects.append(obj)
            return True
        return False

    def defineObjects(self):
        self.maxV = self.objects[0].v
        for obj in self.objects:
            if obj.v > self.maxV:
                self.maxV = obj.v

            for coord in obj.getCoords(self.res):
                self.grid[coord[0]][coord[1]] = obj.v
                self.objectMask[coord[0]][coord[1]] = 1

    def seed(self):
        self.grid = [[random.randrange(0, self.maxV) if self.isValid(x, y) else self.grid[y][x] for x in range(self.x)] for y in range(self.y)]
 

    def average(self, lst, x, y):
        return sum([lst[y + 1][x], lst[y - 1][x], lst[y][x + 1], lst[y][x - 1]])/4

    def isValid(self, x, y, allowObjects = 0):
        if x >= 2 and y >= 2 and x <= self.xRange - 2 and y <= self.yRange - 2:
            if not self.objectMask[y][x] or allowObjects:
                return True
        return False
        

    def iterate(self):
        self.oldGrid = np.array(self.grid)
        #self.oldGrid = [[self.grid[y][x] for x in range(self.xRange)] for y in range(self.yRange)]
        self.grid = [[self.average(self.grid, x, y) if self.isValid(x, y) else self.grid[y][x] for x in range(self.xRange)] for y in range(self.yRange)]
        self.delta = np.abs(np.array(self.grid) - self.oldGrid)
        return np.max(self.delta)

    def new_solve(self, resolution):
        self.defineObjects()
        steady = np.array(self.grid)
        self.seed()
        grid = np.array(self.grid)
        #mask = np.array(self.objectMask)
        positive_mask = np.array(self.objectMask)
        negative_mask = np.abs(np.ones(positive_mask.shape) - positive_mask)
        print(negative_mask)
        seed = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
        seed = seed / np.sum(seed)
        over = False
        tally = 0
        plt.imshow(grid)
        plt.show()
        plt.imshow(steady)
        plt.show()
        plt.show()
        while not over:
            new = ndimage.convolve(grid, seed)
            new = new * negative_mask + steady
            print(np.max(new))
            delta = np.abs(grid - new)
            diff = np.max(delta)
            grid = new
            if diff < resolution:
                over = True
            tally += 1
            print(tally, diff)
        self.grid = grid



    def solve(self, resolution):
        # Make object Map
        self.defineObjects()
        self.seed()

        tally = 0
        over = False
        while not over:
            tally += 1
            delta = self.iterate()
            print(tally, delta)
            if delta < resolution:
                over = True

    def gradientMap(self, peak, value):
        interval = peak / 255
        mappedValue = int(value / interval)
        R = 0 + mappedValue
        G = 0
        B = 255 - mappedValue
        return (R, G, B)
        

    def colourAtPoint(self, x, y, peak):
        if self.objectMask[y][x]:
            return (0, 0, 0)
        return self.gradientMap(peak, self.grid[y][x])

    def photo(self, fname):
        peak = np.max(self.grid)
        im = Image.new("RGB", (len(self.grid[0]), len(self.grid)), "white")
        img = im.load()
        for y in range(len(self.grid)):
            for x in range(len(self.grid[0])):
                img[x, y] = self.colourAtPoint(x, y, peak)

        im.save(fname + '.png', "PNG")


class Rectangle:

    def __init__(self, px, py, x, y, v):
        self.px = px
        self.py = py
        self.x = x
        self.y = y
        self.v = v

    def getCoords(self, res):
        xStart = int(self.px / res)
        yStart = int(self.py / res)
        
        if self.px - xStart * res > (res/2):
            xStart += 1

        if self.py - yStart * res > (res/2):
            yStart += 1

        xEnd = int((self.px + self.x)/ res) - 1
        yEnd = int((self.py + self.y)/ res) - 1
        
        if self.px + self.x - xEnd * res < (res/2):
            xEnd += 1

        if self.py + self.y - yEnd * res < (res/2):
            yEnd += 1

        lst = [ [j, i] for j in range(yStart, yEnd + 1) for i in range(xStart, xEnd + 1)]

        return lst
        

    def fits(self, x, y):
        if x < self.px + self.x:
            return False
        if y < self.py + self.y:
            return False
        return True


a = Space(1500, 1500, 1)
o1 = Rectangle(140, 240, 1220, 10, 0)
o2 = Rectangle(140, 240, 10, 1010, 0)
o3 = Rectangle(1350, 240, 10, 1010, 0)
o4 = Rectangle(250, 1250, 1000, 10, 100)
a.addObject(o1)
a.addObject(o2)
a.addObject(o3)
a.addObject(o4)
#a.solve(0.1)
a.new_solve(0.1)
a.photo("demo_new")


