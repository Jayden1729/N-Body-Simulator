import numpy as np
import pygame
import random
import time

def main():
    pygame.init()
   
    screenWidth = 800
    screenHeight = 800
    GRAVITY = 6.67430 * 10**-11
    timeStep = 0.0003
    theta = 5
    softening = 10
    numParticles = 500
    maxFPS = 30
    orbit = True
    dual = False
   
    screen = pygame.display.set_mode((screenWidth, screenHeight))
   
    boundary = Rectangle(screenWidth/2, screenHeight/2, screenWidth, screenHeight)
   
    particles = []
   
    blackholeMass = 100000000000000000000
   
    for i in range(numParticles):
        xPos = ((random.random() + random.random() + random.random()) * 800/3)
        yPos = ((random.random() + random.random() + random.random()) * 200/3)+300
        #xPos = (random.random()) * 800
        #yPos = (random.random()) * 800
        #yPos=random.random()*400*(-1)**sign+800*sign
       
        v1 = 50 * random.random() * (-1)**(random.randint(1,2))
        v2 = 50 * random.random() * (-1)**(random.randint(1,2))
        if orbit:
            if yPos >= screenHeight/2 and xPos >= screenWidth/2:
                ySign = -1
                xSign = 1
            elif yPos >= screenHeight/2 and xPos <= screenWidth/2:
                ySign = 1
                xSign = 1
            elif yPos <= screenHeight/2 and xPos >= screenWidth/2:
                ySign = -1
                xSign = 1
            elif yPos <= screenHeight/2 and xPos <= screenWidth/2:
                ySign = 1
                xSign = 1
            d = np.sqrt((xPos-screenWidth/2)**2+(yPos-screenHeight/2)**2)
            absV = 1/(d**(1/2.7)) * 45000 - random.random()*000
            v1 = absV*np.sin(np.arcsin((yPos-screenHeight/2)/d))*xSign
            v2 = absV*np.cos(np.arcsin((yPos-screenHeight/2)/d))*ySign
            
        
        particle = Particle(xPos, yPos, v1, v2, 300000000000000 + 1)
        particles.append(particle)
   
    if orbit:
        particles.append(Particle(screenWidth/2, screenHeight/2, 0, 0, blackholeMass))
        
    if dual:
        particles.append(Particle(screenWidth/3, screenHeight/3, 0, 0, blackholeMass))
        particles.append(Particle(2 * screenWidth/3, 2* screenHeight/3, 0, 0, blackholeMass))
   
    running = True
    while running:
        screen.fill((0,0,0))
       
        quadTree = QuadTree(boundary)
       
        for particle in particles:
            quadTree.addParticle(particle)
       
        quadTree.generateCOM()
       
        
        timeStart = time.time()
        
        quadTree.updateAcc(quadTree.particles, theta, GRAVITY, softening)
        
        endTime = time.time()
        if (endTime - timeStart) < 1/maxFPS:
            time.sleep(1/(maxFPS) - (endTime - timeStart))
        
        if (endTime - timeStart) > 0:
            print(1 / (time.time() - timeStart))
        
        Particle.iterate(quadTree.particles, timeStep)
       
        for particle in quadTree.particles:
            pygame.draw.circle(screen, (255,255,255), (particle.x, particle.y), 2)

       
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
       
        #quadTree.display(screen)
       
        pygame.display.update()
       
    pygame.quit()

class Particle:
    #initialise particle
    def __init__(self, x, y, vx, vy, m):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.ax = 0
        self.ay = 0
        self.m = m
   
    #finds the acceleration of a node of the quadtree on a particle
    def findAcc(self, node, GRAVITY, softening):
        rx = node.centreOfMassX - self.x
        ry = node.centreOfMassY - self.y
        r = np.sqrt((rx) ** 2 + (ry) ** 2 + softening ** 2)
        
        if r != 0:
            xAcc = (GRAVITY * node.totalMass * rx)/ (r **3)
            yAcc = (GRAVITY * node.totalMass * ry)/ (r **3)
       
            self.ax += xAcc
            self.ay += yAcc
        
    def iterate(particles, timeStep):
        for particle in particles:
            particle.vx += particle.ax * timeStep
            particle.vy += particle.ay * timeStep
            particle.x += particle.vx * timeStep
            particle.y += particle.vy * timeStep
            
            particle.ax = 0
            particle.ay = 0

class Rectangle:
    #initialise rectangle
    def __init__(self, centreX, centreY, w, h):
        # w is distance from centre to edge along x-axis. i.e. total width of rectangle is 2*w
        # likewise for h
        self.centreX = centreX
        self.centreY = centreY
        self.w = w
        self.h = h
   
    def overlap(self, rectangle):
        return not ((self.centreX + self.w < rectangle.centreX - rectangle.w) or (self.centreX - self.w > rectangle.centreX + rectangle.w) or (self.centreY + self.h < rectangle.centreY - rectangle.h) or (self.centreY - self.h > rectangle.centreY + rectangle.h))


class QuadTree:
    #initialise quadtree
    def __init__(self, boundary):
        self.boundary = boundary
        self.particles = []
        self.centreOfMassX = 0
        self.centreOfMassY = 0
        self.totalMass = 0
       
        self.isDivided = False
        self.nw = None
        self.ne = None
        self.sw = None
        self.se = None
   
    #add a particle to the quadtree
    def addParticle(self, particle):
        if self.contains(particle):
            if self.isDivided:
                self.nw.addParticle(particle)
                self.ne.addParticle(particle)
                self.sw.addParticle(particle)
                self.se.addParticle(particle)
                self.particles.append(particle)
               
            elif len(self.particles) == 1 and not self.isDivided:
                self.divide()
                self.addParticle(self.particles[0])
                self.particles = [self.particles[0]]
                self.addParticle(particle)
               
            else:
                self.particles.append(particle)
   
    #divide segment into quadrants
    def divide(self):
        northwest = Rectangle(self.boundary.centreX - self.boundary.w / 2, self.boundary.centreY - self.boundary.h / 2, self.boundary.w / 2, self.boundary.h / 2)
        self.nw = QuadTree(northwest)
       
        northeast = Rectangle(self.boundary.centreX + self.boundary.w / 2, self.boundary.centreY - self.boundary.h / 2, self.boundary.w / 2, self.boundary.h / 2)
        self.ne = QuadTree(northeast)
       
        southwest = Rectangle(self.boundary.centreX - self.boundary.w / 2, self.boundary.centreY + self.boundary.h / 2, self.boundary.w / 2, self.boundary.h / 2)
        self.sw = QuadTree(southwest)
       
        southeast = Rectangle(self.boundary.centreX + self.boundary.w / 2, self.boundary.centreY + self.boundary.h / 2, self.boundary.w / 2, self.boundary.h / 2)
        self.se = QuadTree(southeast)
       
        self.isDivided = True
   
    #determines if the region contains the particle
    def contains(self, particle):
        if particle.x >= self.boundary.centreX - self.boundary.w and particle.x < self.boundary.centreX + self.boundary.w and particle.y >= self.boundary.centreY - self.boundary.h and particle.y < self.boundary.centreY + self.boundary.h:
            return True
   
    def query(self, region):
        result = []
       
        if not self.boundary.overlap(region):
            return result
       
        if self.isDivided:
            result.extend(self.nw.query(region))
            result.extend(self.ne.query(region))
            result.extend(self.sw.query(region))
            result.extend(self.se.query(region))
           
        else:
            for particle in self.particles:
                if particle.x < region.centreX + region.w and particle.x >= region.centreX - region.w and particle.y <= region.centreY + region.h and particle.y > region.centreY - region.h:
                    result.append(particle)
       
        return result
   
    def generateCOM(self):
        if len(self.particles) == 0:
            return
       
        if self.isDivided:
            self.nw.generateCOM()
            self.ne.generateCOM()
            self.sw.generateCOM()
            self.se.generateCOM()
           
            self.totalMass = self.nw.totalMass + self.ne.totalMass + self.sw.totalMass + self.se.totalMass
            self.centreOfMassX = ((self.nw.centreOfMassX * self.nw.totalMass) + (self.ne.centreOfMassX * self.ne.totalMass) + (self.sw.centreOfMassX * self.sw.totalMass) + (self.se.centreOfMassX * self.se.totalMass)) / self.totalMass
            self.centreOfMassY = ((self.nw.centreOfMassY * self.nw.totalMass) + (self.ne.centreOfMassY * self.ne.totalMass) + (self.sw.centreOfMassY * self.sw.totalMass) + (self.se.centreOfMassY * self.se.totalMass)) / self.totalMass
           
        else:
            self.totalMass = self.particles[0].m
            self.centreOfMassX = self.particles[0].x
            self.centreOfMassY = self.particles[0].y
       
    def updateAcc(self, particles, theta, GRAVITY, softening):
        for particle in particles:
            self.checkNodes(particle, theta, GRAVITY, softening)
       
    def checkNodes(self, particle, theta, GRAVITY, softening):
        if len(self.particles) == 0:
            return
   
        distance = np.sqrt((particle.x - self.centreOfMassX) ** 2 + (particle.y - self.centreOfMassY) ** 2)
        if distance == 0:
            return
       
        if (self.boundary.w * 2) / distance <= theta or len(self.particles) == 1:
            particle.findAcc(self, GRAVITY, softening)
       
        elif self.isDivided:
            self.nw.checkNodes(particle, theta, GRAVITY, softening)
            self.ne.checkNodes(particle, theta, GRAVITY, softening)
            self.sw.checkNodes(particle, theta, GRAVITY, softening)
            self.se.checkNodes(particle, theta, GRAVITY, softening)                
           
    #displays the quadtree
    def display(self, screen):
        if self.isDivided:
            self.nw.display(screen)
            self.ne.display(screen)
            self.sw.display(screen)
            self.se.display(screen)
       
        pygame.draw.rect(screen, (255, 255, 255), (self.boundary.centreX - self.boundary.w, self.boundary.centreY - self.boundary.h, self.boundary.w * 2, self.boundary.h * 2), 1)


main()