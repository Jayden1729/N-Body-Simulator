import pygame
import random


def main():
    pygame.init()
    
    screenWidth = 800
    screenHeight = 600
    
    screen = pygame.display.set_mode((screenWidth, screenHeight))
    
    boundary = Rectangle(screenWidth/2, screenHeight/2, screenWidth/2, screenHeight/2)
    
    qt = QuadTree(boundary)
    
    particles = []
    
    for i in range(25):
        particle = Particle(random.random() * screenWidth, random.random() * screenHeight, 0, 0, 0)
        qt.addParticle(particle)
        particles.append(particle)
    
    running = True
    while running:
        screen.fill((0,0,0))
        
        for particle in particles:
            pygame.draw.circle(screen, (255,255,255), (particle.x, particle.y), 4)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        pygame.display.update()
        
    pygame.quit()


class Particle:
    #initialise particle
    def __init__(self, x, y, vx, vy, m):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.m = m


class Rectangle:
    #initialise rectangle
    def __init__(self, centreX, centreY, w, h):
        # w is distance from centre to edge along x-axis. i.e. total width of rectangle is 2*w
        # likewise for h
        self.centreX = centreX
        self.centreY = centreY
        self.w = w
        self.h = h


class QuadTree:
    #initialise quadtree
    def __init__(self, boundary):
        self.boundary = boundary
        self.particles = []
        
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
        
            elif len(self.particles) == 1 and self.isDivided == False:
                self.divide()
                self.addParticle(self.particles[0])
                self.particles = []
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
    
   #displays the quadtree 
    def display(self, screen):
        if self.isDivided:
            self.nw.display(screen)
            self.ne.display(screen)
            self.sw.display(screen)
            self.se.display(screen)
        
        pygame.draw.rect(screen, (255, 255, 255), (self.boundary.centreX - self.boundary.w, self.boundary.centreY - self.boundary.h, self.boundary.w * 2, self.boundary.h * 2), 1)


main()