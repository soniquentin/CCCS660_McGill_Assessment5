import pygame
import sys
import numpy as np
from drones import Drone
import json



############################################
########### CONSTANTS FROM JSON ############
############################################
params = json.load(open("params.json"))

HORIZONTAL_DISTANCE = params["horizontal_distance"]
VERTICAL_DISTANCE = params["vertical_distance"]
FRICTION = 1/params["mass"]
WIDTH, HEIGHT = params["width"], params["height"]
WAVE_FREQUENCY = params["wave_frequency"]
CAPTURE_WIDTH, CAPTURE_HEIGHT = params["capture_width"], params["capture_height"]
SHOW_CAPTURE = params["show_capture"]




############################################
######### COMPUTE OTHER CONSTANTS ##########
############################################
security_zone = min(HORIZONTAL_DISTANCE, VERTICAL_DISTANCE)//4




# Initialize Pygame
pygame.init()

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)


# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Drone Orthmosaic")

#Leader drone
leader_drone = Drone(x = WIDTH // 2, 
                    y = HEIGHT // 2, 
                    color = RED, 
                    friction = FRICTION, 
                    leader = True, 
                    width = WIDTH,
                    height = HEIGHT,
                    security_zone = security_zone,
                    wave_frequency = WAVE_FREQUENCY
                    )


#Automatic drones : Formation in V
leader_pos = (WIDTH // 2, HEIGHT // 2)
drones = []
drones.append(Drone(WIDTH // 2 + HORIZONTAL_DISTANCE, HEIGHT // 2 + VERTICAL_DISTANCE, BLUE, FRICTION, False, WIDTH, HEIGHT, leader_pos))
drones.append(Drone(WIDTH // 2 - HORIZONTAL_DISTANCE, HEIGHT // 2 + VERTICAL_DISTANCE, BLUE, FRICTION, False, WIDTH, HEIGHT, leader_pos))
drones.append(Drone(WIDTH // 2 + 2*HORIZONTAL_DISTANCE, HEIGHT // 2 + 2*VERTICAL_DISTANCE, BLUE, FRICTION, False, WIDTH, HEIGHT, leader_pos))
drones.append(Drone(WIDTH // 2 - 2*HORIZONTAL_DISTANCE, HEIGHT // 2 + 2*VERTICAL_DISTANCE, BLUE, FRICTION, False, WIDTH, HEIGHT, leader_pos))
drones.append(Drone(WIDTH // 2 + 3*HORIZONTAL_DISTANCE, HEIGHT // 2 + 3*VERTICAL_DISTANCE, BLUE, FRICTION, False, WIDTH, HEIGHT, leader_pos))


#Pixels captures
captures = np.zeros((WIDTH, HEIGHT))

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    


    #Fill the screen with white
    screen.fill(WHITE)


    # KEY PRESS FOR THE LEADER DRONE
    keys = pygame.key.get_pressed()
    moves_leader = [0, 0, 0, 0] #Left, Right, Up, Down
    if keys[pygame.K_LEFT]:
        moves_leader[0] = 1
    if keys[pygame.K_RIGHT]:
        moves_leader[1] = 1
    if keys[pygame.K_UP]:
        moves_leader[2] = 1
    if keys[pygame.K_DOWN]:
        moves_leader[3] = 1
    leader_drone.move(moves_leader)
    
    
    """
    #Draw the pixels captures
    if SHOW_CAPTURE :
        #For the leader
        captures[int(leader_drone.x - CAPTURE_WIDTH//2 + leader_drone.square_size//2) : int(leader_drone.x + CAPTURE_WIDTH//2 + leader_drone.square_size//2), int(leader_drone.y - CAPTURE_HEIGHT//2 + leader_drone.square_size//2) : int(leader_drone.y + CAPTURE_HEIGHT//2 + leader_drone.square_size//2)] = 1
        
        #For the automatic drones
        for drone in drones :
            captures[int(drone.x - CAPTURE_WIDTH//2 + drone.square_size//2) : int(drone.x + CAPTURE_WIDTH//2 + drone.square_size//2), int(drone.y - CAPTURE_HEIGHT//2 + drone.square_size//2) : int(drone.y + CAPTURE_HEIGHT//2 + drone.square_size//2)] = 1
    
    #Draw the pixels captures in blue
    for i in range(WIDTH) :
        for j in range(HEIGHT) :
            if captures[i, j] == 1 :
                screen.set_at((i, j), (200, 200, 255))
    """


    #Draw the automatic drones
    for drone in drones :
        drone.update_com_wave_collide(leader_drone.communication_waves)  #Update the last wave collision from the leader
        move = drone.get_intelligent_move() #Get the move for the drone according to the last interaction with the leader
        drone.move(move)
        drone.draw(screen)
        if SHOW_CAPTURE : #Draw the capture zone
            pygame.draw.rect(screen, BLUE, (drone.x - CAPTURE_WIDTH//2 + drone.square_size//2  , drone.y - CAPTURE_HEIGHT//2 + drone.square_size//2, CAPTURE_WIDTH, CAPTURE_HEIGHT), 1)
    
    if SHOW_CAPTURE : #Draw the capture zone for the leader
        pygame.draw.rect(screen, BLUE, (leader_drone.x - CAPTURE_WIDTH//2 + leader_drone.square_size//2  , leader_drone.y - CAPTURE_HEIGHT//2 + leader_drone.square_size//2, CAPTURE_WIDTH, CAPTURE_HEIGHT), 1)
        #Set all the pixels in the capture zone to 1

    #Draw the leader drone
    leader_drone.draw(screen)


    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(40)

# Quit Pygame
pygame.quit()
sys.exit()
