import numpy as np
import pygame
import random
import time

def main():
    pygame.init()
   
    screen_width = 800
    screen_height = 800
    GRAVITY = 6.67430 * 10**-11
    time_step = 0.0003
    theta = 8
    softening = 10
    num_particles = 500
    max_fps = 40
    show_algorithm = False
    orbit = True
    dual = False
   
    screen = pygame.display.set_mode((screen_width, screen_height))
   
    boundary = Rectangle(screen_width/2, screen_height/2, screen_width, screen_height)
   
    particles = []
   
    black_hole_mass = 100000000000000000000
   
    for i in range(num_particles):
        x_pos = ((random.random() + random.random() + random.random()) * 800/3)
        y_pos = ((random.random() + random.random() + random.random()) * 200/3)+300
        #x_pos = (random.random()) * 800
        #y_pos = (random.random()) * 800
        #y_pos=random.random()*400*(-1)**sign+800*sign
       
        v1 = 50 * random.random() * (-1)**(random.randint(1,2))
        v2 = 50 * random.random() * (-1)**(random.randint(1,2))
        if orbit:
            if y_pos >= screen_height/2 and x_pos >= screen_width/2:
                y_sign = -1
                x_sign = 1
            elif y_pos >= screen_height/2 and x_pos <= screen_width/2:
                y_sign = 1
                x_sign = 1
            elif y_pos <= screen_height/2 and x_pos >= screen_width/2:
                y_sign = -1
                x_sign = 1
            elif y_pos <= screen_height/2 and x_pos <= screen_width/2:
                y_sign = 1
                x_sign = 1
            d = np.sqrt((x_pos-screen_width/2)**2+(y_pos-screen_height/2)**2)
            abs_v = 1/(d**(1/2.7)) * 45000 - random.random()*000
            v1 = abs_v*np.sin(np.arcsin((y_pos-screen_height/2)/d))*x_sign
            v2 = abs_v*np.cos(np.arcsin((y_pos-screen_height/2)/d))*y_sign
            
        
        particle = Particle(x_pos, y_pos, v1, v2, 300000000000000 + 1)
        particles.append(particle)
   
    if orbit:
        particles.append(Particle(screen_width/2, screen_height/2, 0, 0, black_hole_mass))
        
    if dual:
        particles.append(Particle(screen_width/3, screen_height/3, 0, 0, black_hole_mass))
        particles.append(Particle(2 * screen_width/3, 2* screen_height/3, 0, 0, black_hole_mass))
   
    running = True
    while running:
        screen.fill((0,0,0))
       
        quad_tree = QuadTree(boundary)
       
        for particle in particles:
            quad_tree.addParticle(particle)
       
        quad_tree.generate_com()
       
        
        time_start = time.time()
        
        quad_tree.update_acc(quad_tree.particles, theta, GRAVITY, softening)
        
        end_time = time.time()
        if (end_time - time_start) < 1/max_fps:
            time.sleep(1/(max_fps) - (end_time - time_start))
        
        if (end_time - time_start) > 0:
            print(1 / (time.time() - time_start))
        
        iterate(quad_tree.particles, time_step)
       
        for particle in quad_tree.particles:
            pygame.draw.circle(screen, (255,255,255), (particle.x, particle.y), 2)

       
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
       
        if show_algorithm:
            quad_tree.display(screen)
       
        pygame.display.update()
       
    pygame.quit()

class Particle:

    def __init__(self, x, y, vx, vy, m):
        """Initialise an instance of the particle class.

        Args:
            x (float): the x position of the particle.
            y (float): the y position of the particle.
            vx (float): the velocity in the x direction of the particle.
            vy (float): the velocity in the y direction of the particle.
            m (float): the mass of the particle.
        """
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.ax = 0
        self.ay = 0
        self.m = m

    def find_acc(self, node, GRAVITY, softening):
        """Finds the acceleration due to gravity acting on self from a node in the QuadTree.

        Args:
            node (QuadTree): a node in the quad tree.
            GRAVITY (float): the gravitational constant.
            softening (float): the softening constant
        """
        rx = node.centre_of_mass_x - self.x
        ry = node.centre_of_mass_y - self.y
        r = np.sqrt((rx) ** 2 + (ry) ** 2 + softening ** 2)
        
        if r != 0:
            x_acc = (GRAVITY * node.total_mass * rx)/ (r **3)
            y_acc = (GRAVITY * node.total_mass * ry)/ (r **3)
       
            self.ax += x_acc
            self.ay += y_acc

class Rectangle:

    def __init__(self, centre_x, centre_y, w, h):
        """Initialise an instance of the Rectangle class.

        Args:
            centre_x (float): the centre of the rectangle in the x direction.
            centre_y (float): the centre of the rectangle in the y direction.
            w (float): 1/2 of the width of the rectangle.
            h (float): 1/2 of the height of the rectangle.
        """
        self.centre_x = centre_x
        self.centre_y = centre_y
        self.w = w
        self.h = h
   
    def overlap(self, rectangle):
        return not ((self.centre_x + self.w < rectangle.centre_x - rectangle.w) or (self.centre_x - self.w > rectangle.centre_x + rectangle.w) or (self.centre_y + self.h < rectangle.centre_y - rectangle.h) or (self.centre_y - self.h > rectangle.centre_y + rectangle.h))


class QuadTree:

    def __init__(self, boundary):
        """Initialise an instance of the QuadTree class.

        Args:
            boundary (Rectangle): a rectangle specifying the boundary of the node.
        """
        self.boundary = boundary
        self.particles = []
        self.centre_of_mass_x = 0
        self.centre_of_mass_y = 0
        self.total_mass = 0
       
        self.is_divided = False
        self.nw = None
        self.ne = None
        self.sw = None
        self.se = None

    def addParticle(self, particle):
        """Add a particle to the quad tree.

        Args:
            particle (Particle): the particle to be added to the quad tree.
        """
        if self.contains(particle):
            if self.is_divided:
                self.nw.addParticle(particle)
                self.ne.addParticle(particle)
                self.sw.addParticle(particle)
                self.se.addParticle(particle)
                self.particles.append(particle)
               
            elif len(self.particles) == 1 and not self.is_divided:
                self.divide()
                self.addParticle(self.particles[0])
                self.particles = [self.particles[0]]
                self.addParticle(particle)
               
            else:
                self.particles.append(particle)

    def divide(self):
        """Divide the segment into a new layer of the quad tree.
        """
        northwest = Rectangle(self.boundary.centre_x - self.boundary.w / 2, self.boundary.centre_y - self.boundary.h / 2, self.boundary.w / 2, self.boundary.h / 2)
        self.nw = QuadTree(northwest)
       
        northeast = Rectangle(self.boundary.centre_x + self.boundary.w / 2, self.boundary.centre_y - self.boundary.h / 2, self.boundary.w / 2, self.boundary.h / 2)
        self.ne = QuadTree(northeast)
       
        southwest = Rectangle(self.boundary.centre_x - self.boundary.w / 2, self.boundary.centre_y + self.boundary.h / 2, self.boundary.w / 2, self.boundary.h / 2)
        self.sw = QuadTree(southwest)
       
        southeast = Rectangle(self.boundary.centre_x + self.boundary.w / 2, self.boundary.centre_y + self.boundary.h / 2, self.boundary.w / 2, self.boundary.h / 2)
        self.se = QuadTree(southeast)
       
        self.is_divided = True

    def contains(self, particle):
        """Determines whether the particle is contained within the boundary of this node.

        Args:
            particle (Particle): the particle to check.

        Returns:
            bool: returns True if the particle is within the boundary of the node.
        """
        if particle.x >= self.boundary.centre_x - self.boundary.w and particle.x < self.boundary.centre_x + self.boundary.w and particle.y >= self.boundary.centre_y - self.boundary.h and particle.y < self.boundary.centre_y + self.boundary.h:
            return True
   
    def generate_com(self):
        """Generates the centre of mass of the node.

        Finds the centre of mass position of all the particles in the node, and the total mass, then sets the
        self.centre_of_mass_x and _y variables and self.total_mass variable.
        """
        if len(self.particles) == 0:
            return
       
        if self.is_divided:
            self.nw.generate_com()
            self.ne.generate_com()
            self.sw.generate_com()
            self.se.generate_com()
           
            self.total_mass = self.nw.total_mass + self.ne.total_mass + self.sw.total_mass + self.se.total_mass
            self.centre_of_mass_x = ((self.nw.centre_of_mass_x * self.nw.total_mass) + (self.ne.centre_of_mass_x * self.ne.total_mass) + (self.sw.centre_of_mass_x * self.sw.total_mass) + (self.se.centre_of_mass_x * self.se.total_mass)) / self.total_mass
            self.centre_of_mass_y = ((self.nw.centre_of_mass_y * self.nw.total_mass) + (self.ne.centre_of_mass_y * self.ne.total_mass) + (self.sw.centre_of_mass_y * self.sw.total_mass) + (self.se.centre_of_mass_y * self.se.total_mass)) / self.total_mass
           
        else:
            self.total_mass = self.particles[0].m
            self.centre_of_mass_x = self.particles[0].x
            self.centre_of_mass_y = self.particles[0].y
       
    def update_acc(self, particles, theta, GRAVITY, softening):
        """Finds the acceleration of each particle in the quad_tree.

        Args:
            particles (List[Particles]): the list of particles on the screen.
            theta (float): the value of theta for the simulation.
            GRAVITY (float): the gravitational constant.
            softening (float): the softening constant for the simulation.
        """
        for particle in particles:
            self.check_nodes(particle, theta, GRAVITY, softening)

    def check_nodes(self, particle, theta, GRAVITY, softening):
        """Checks all the nodes of the simulation and updates a specified particles acceleration.

        Args:
            particle (Particle): the particle to find the acceleration for.
            theta (float): the theta value of the simulation.
            GRAVITY (float): the gravitational constant.
            softening (float): the softening constant for the simulation.
        """
        if len(self.particles) == 0:
            return

        distance = np.sqrt((particle.x - self.centre_of_mass_x) ** 2 + (particle.y - self.centre_of_mass_y) ** 2)
        if distance == 0:
            return

        if (self.boundary.w * 2) / distance <= theta or len(self.particles) == 1:
            particle.find_acc(self, GRAVITY, softening)

        elif self.is_divided:
            self.nw.check_nodes(particle, theta, GRAVITY, softening)
            self.ne.check_nodes(particle, theta, GRAVITY, softening)
            self.sw.check_nodes(particle, theta, GRAVITY, softening)
            self.se.check_nodes(particle, theta, GRAVITY, softening)

    def display(self, screen):
        """Displays the quad tree on the screen.

        Args:
            screen (pygame.display): the screen to display the quad tree.
        """
        if self.is_divided:
            self.nw.display(screen)
            self.ne.display(screen)
            self.sw.display(screen)
            self.se.display(screen)
       
        pygame.draw.rect(screen, (255, 255, 255), (self.boundary.centre_x - self.boundary.w, self.boundary.centre_y - self.boundary.h, self.boundary.w * 2, self.boundary.h * 2), 1)

def iterate(particles, time_step):
    """Moves the particles one time step forward.

    Args:
        particles (List[Particles]): a list of particles.
        time_step (float): the change in time to iterate over.

    """
    for particle in particles:
        particle.vx += particle.ax * time_step
        particle.vy += particle.ay * time_step
        particle.x += particle.vx * time_step
        particle.y += particle.vy * time_step

        particle.ax = 0
        particle.ay = 0

if __name__ == '__main__':
    main()