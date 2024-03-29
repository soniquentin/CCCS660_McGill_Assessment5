import pygame
import numpy as np
import json


params = json.load(open("params.json"))


class Drone() :

    speed_max = params["speed_max"] #Maximum speed of the drone
    show_waves = params["show_waves"] #Show the communication waves
    wind_speed, wind_angle = params["wind_speed"], params["wind_angle"]

    def __init__(self, x, y, friction = 1, leader = False, width = 800, height = 600, leader_pos = None, security_zone = 30, wave_frequency = 5) :

        self.x = x
        self.y = y
        self.speed_x = 0
        self.speed_y = 0
        self.leader = leader
        self.width = width
        self.height = height
        self.friction = friction
        self.image = pygame.image.load("img/leader_drone.png") if leader else pygame.image.load("img/automatic_drone.png")
        self.rect = self.image.get_rect()
        #size of rectangle of image
        self.square_size = self.rect.width
        if self.leader : 
            self.wave_frequency = wave_frequency
            self.tick = 0
            self.communication_waves = []
        else :
            self.last_wave_collision = None
            self.leader_pos_x, self.leader_pos_y = leader_pos
            self.relative_pos_x, self.relative_pos_y = self.x - self.leader_pos_x, self.y - self.leader_pos_y
            self.security_zone = security_zone


    def move(self, moves) :
        """
        moves is a list [left, right, up, down] with values 0 or 1
        """
        horizontal_move = moves[1] - moves[0]
        vertical_move = moves[3] - moves[2]

        if horizontal_move > 0 :
            self.speed_x = min(self.speed_x + self.friction, self.speed_max) 
        elif horizontal_move < 0 :
            self.speed_x = max(self.speed_x - self.friction, -self.speed_max)
        else :
            self.speed_x = max(self.speed_x - self.friction, 0) if self.speed_x >= 0 else min(self.speed_x + 1, 0)

        if vertical_move > 0 :
            self.speed_y = min(self.speed_y + self.friction, self.speed_max)
        elif vertical_move < 0 :
            self.speed_y = max(self.speed_y - self.friction, -self.speed_max)
        else :
            self.speed_y = max(self.speed_y - self.friction, 0) if self.speed_y >= 0 else min(self.speed_y + 1, 0)


        # Update the position of the square
        if self.speed_x != 0 and self.speed_y != 0 :
            self.x += self.speed_x / np.sqrt(2)
            self.y += self.speed_y / np.sqrt(2)
        else :
            self.x += self.speed_x
            self.y += self.speed_y

        #Random float number between 0 and wind_speed
        wind_x, wind_y = np.random.rand() * self.wind_speed, np.random.rand() * self.wind_speed
        self.x += wind_x*np.cos(self.wind_angle*np.pi/180)
        self.y += -wind_y*np.sin(self.wind_angle*np.pi/180)


        # Prevent the square from going out of bounds
        self.x = max(0, min(self.width - self.square_size, self.x))
        self.y = max(0, min(self.height - self.square_size, self.y))



        #Update the tick if the drone is a leader : send communication waves
        if self.leader :
            self.tick += 1
            if self.tick % self.wave_frequency == 0 :
                self.communication_waves.append(Communication_wave(self.x + self.square_size // 2, self.y + self.square_size // 2, self.speed_x , self.speed_y , ( 255 , 200, 200)))
            for wave in self.communication_waves :
                wave.grow()
            self.communication_waves = [wave for wave in self.communication_waves if not wave.is_out_of_bounds(self.width, self.height)]


    def get_intelligent_move(self) :
        """
        Only for automatic drones
        """
        move = [0, 0, 0, 0]

        if self.last_wave_collision is not None :
            move[0] = 1 if self.last_wave_collision.x + self.relative_pos_x + self.security_zone < self.x else 0
            move[1] = 1 if self.last_wave_collision.x + self.relative_pos_x - self.security_zone >= self.x else 0
            move[2] = 1 if self.last_wave_collision.y + self.relative_pos_y + self.security_zone < self.y else 0
            move[3] = 1 if self.last_wave_collision.y + self.relative_pos_y - self.security_zone >= self.y else 0

        return move


    
    def update_com_wave_collide(self, leader_waves_list) :
        """
        Only for automatic drones
        """
        min_distance_wave_border = np.sqrt(self.width**2 + self.height**2)
        idx_min = -1

        for i, wave in enumerate(leader_waves_list) :
            distance_to_center = np.sqrt((self.x - wave.x)**2 + (self.y - wave.y)**2)
            if distance_to_center < wave.radius and wave.radius - distance_to_center < min_distance_wave_border:
                min_distance_wave_border = wave.radius - distance_to_center
                idx_min = i

        if idx_min != -1 :
            self.last_wave_collision = leader_waves_list[idx_min]


    def draw(self, screen) :
        self.rect.topleft = (self.x, self.y)
        screen.blit(self.image, self.rect)


        #Draw the communication waves if the drone is a leader
        if self.show_waves and self.leader :
            
            for wave in self.communication_waves :
                wave.draw(screen)
        """
                #Draw the idx of the wave on the circle
                font = pygame.font.Font(None, 36)
                text = font.render(str(wave.idx), True, (0, 0, 0))
                screen.blit(text, (wave.x + wave.radius, wave.y))
        else :
            #Put a text in the square with the last wave collision
            if self.last_wave_collision is not None :
                font = pygame.font.Font(None, 36)
                text = font.render(str(self.last_wave_collision.idx), True, (0, 0, 0))
                screen.blit(text, (self.x, self.y))
        """




class Communication_wave():


    wave_speed = params["wave_speed"]
    idx = 0

    def __init__(self, x, y, speed_x, speed_y, color, radius = 10) : #speed_x and speed_y are the speed of the drone when the wave is created
        self.x = x
        self.y = y
        self.color = color
        self.radius = radius
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.idx = Communication_wave.idx
        Communication_wave.idx += 1


    def __str__(self) :
        return f"Wave {self.idx} : ({self.x}, {self.y}) , radius = {self.radius}"

    def draw(self, screen) :
        #Circle with only the border
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius, 1)
        
    def grow(self) :
        self.radius += self.wave_speed

    def is_out_of_bounds(self, width, height) :
        return self.radius >= max(width, height)
    