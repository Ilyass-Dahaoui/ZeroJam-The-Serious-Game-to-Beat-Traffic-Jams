import random
import pygame
from pygame.locals import *
from vehicle import *
from configurations import *
from graphes import Graphe

pygame.init()

# create the window
screen_size = (width, height)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Car Game')

#game settings
temps = 0
temps_unit=20
random_vehicle=None
step_backword=13
coef_changing_simulation_speed=1
font = pygame.font.Font(pygame.font.get_default_font(), 16)

### graphs settings ###

my_graph = Graphe()
simulation_case=None
if ( CONSTANT_SPEED) and ( not CHANGE_LANE)  and ( not STOP_VEHICLES) : simulation_case= 1
elif ( not CONSTANT_SPEED) and ( not CHANGE_LANE)  and ( STOP_VEHICLES) : simulation_case= 2
elif ( not CONSTANT_SPEED) and ( CHANGE_LANE)  and ( not STOP_VEHICLES) : simulation_case= 3

'for the second lane: freinage des vehicules'
graph_list_temps,graph_list_bouchons_longs=[],[ [], [], [] ]

'for the third lane: changement de ligne'
graph_list_nbr_of_lanes_changing, graph_list_taux_embouteillage = [],[]
nbr_of_lanes_changing,taux_embouteillage= 0,0


# colors
gray = (100, 100, 100)
green = (76, 208, 56)
red = (200, 0, 0)
white = (255, 255, 255)
yellow = (255, 232, 0)

# road and marker sizes
road_height = 300
marker_height = 50
marker_width = 10

# lane coordinates
top_lane = 150
center_lane = 250
buttom_lane = 350
lanes = [top_lane, center_lane, buttom_lane]

# road and edge markers
road = (0, 100,width, road_height)
left_edge_marker = (0, 95, width, marker_width)
right_edge_marker = (0, 395, width, marker_width)

# for animating movement of the lane markers
lane_marker_move_x = 0

# player's starting coordinates
player_x = 400
player_y = 250

# frame settings
clock = pygame.time.Clock()
fps = 120


#adding cars settings
proba_to_add_vehicle=0.5
max_vehiculs_width= 100

def add_vehicle(vehicle_group,vehicle_images):
    if proba_to_add_vehicle > random.random() :
        # select a random lane
        lane = random.choice(lanes)
        
        # ensure there's enough gap between vehicles in the lane
        add_vehicle = True
        for vehicle in vehicle_group:
            if all((vehicle.rect.right < (vehicle.rect.width + random.uniform(1,2)),
                    vehicle.rect.center[1]==lane)):
                add_vehicle = False

        if add_vehicle:
            #get a speed for this vehicle
            vehicle_speed=speed if CONSTANT_SPEED else random.uniform(*interval_changing_speed)
             
            # select a random vehicle image
            image = random.choice(vehicle_images)
            vehicle = Vehicle(image, -(max_vehiculs_width * random.uniform(1,2.5) + 2), lane, vehicle_speed)
            vehicle_group.add(vehicle)
        

# sprite groups
vehicle_group = pygame.sprite.Group()


# load the vehicle images
image_filenames = ['pickup_truck.png', 'semi_trailer.png', 'taxi.png', 'van.png', 'car.png']
vehicle_images = []
for image_filename in image_filenames:
    image = pygame.image.load('images/' + image_filename)
    vehicle_images.append(image)
    

# game loop
running = True
while running:
    # add to temps
    temps += coef_changing_simulation_speed

    clock.tick(fps)
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        elif event.type == KEYDOWN:

            if event.key == K_UP :
                if coef_changing_simulation_speed < 20:
                    coef_changing_simulation_speed*=2
            elif event.key == K_DOWN :
                if coef_changing_simulation_speed > 0.5:
                    coef_changing_simulation_speed/=2
            
            # saving graph
            elif event.key == K_s:
                # for the second lane: freinage des vehicules
                if simulation_case == 2: 
                    my_graph.create_graph_freinage_case(graph_list_temps,
                                                        graph_list_bouchons_longs)
                # for the third lane: changement de ligne
                elif simulation_case == 3: 
                    my_graph.create_graph_changing_lanes_case(graph_list_nbr_of_lanes_changing,
                                                              graph_list_taux_embouteillage)
    
    # draw the grass
    screen.fill(green)
    
    # draw the road
    pygame.draw.rect(screen, gray, road)
    
    # draw the edge markers
    pygame.draw.rect(screen, yellow, left_edge_marker)
    pygame.draw.rect(screen, yellow, right_edge_marker)
    
    # draw the lane markers
    for x in range(marker_height * -2 +20, int(width *1.2), marker_height * 2):
        pygame.draw.rect(screen, white, (x + lane_marker_move_x, top_lane + 45,  marker_height, marker_width))
        pygame.draw.rect(screen, white, (x + lane_marker_move_x, center_lane + 45,  marker_height, marker_width))
    
    # add a vehicle
    add_vehicle(vehicle_group,vehicle_images)

    # make the vehicles move
    min_speed, max_speed= 100,0 
    for vehicle in vehicle_group:
        min_speed= min(min_speed,vehicle.speed)
        max_speed= max(max_speed,vehicle.speed)
        vehicle.rect.x += vehicle.speed * coef_changing_simulation_speed
        vehicle.update_delay_before_rechanging_lane(delay_before_rechanging_lane)
        #check if the vehicle is stoped or not
        vehicle.update_speed_state(delay_before_vehicle_reboting)


        # remove vehicle once it goes off screen
        if vehicle.rect.left >= width:
            vehicle.kill()
    
    # change a random vehicle lane if CHANGE_LANE== True
    if CHANGE_LANE and vehicle_group.sprites():
        random_vehicle= random.choice(vehicle_group.sprites())
        if random_vehicle.is_allowed_to_change_lane:
            if random_vehicle.changing_lane(vehicle_group, lanes, probability_of_changing_lane, screen): 
                nbr_of_lanes_changing+=1

    
    # stop a random vehicle if STOP_VEHICLES== True
    if STOP_VEHICLES:
        if random.random() < probability_of_stoping_vehicles:
            v=random.choice(vehicle_group.sprites())
            if v.rect.left > 30 : v.speed = 0
    
    # display the temps
    temps_lbl = font.render('Temps: ' + str(temps // temps_unit ) , True, white)
    temps_lbl_rect = temps_lbl.get_rect()
    temps_lbl_rect.center = (70, 35)
    screen.blit(temps_lbl, temps_lbl_rect)

    # display the nbr_vehicle
    nbr_vehicle_lbl = font.render('Vehicles: ' + str(len(vehicle_group)), True, white)
    nbr_vehicle_lbl_rect = nbr_vehicle_lbl.get_rect()
    nbr_vehicle_lbl_rect.center = (260, 35)
    screen.blit(nbr_vehicle_lbl, nbr_vehicle_lbl_rect)

    # display the min_speed
    min_speed_lbl = font.render(f'Min speed: {min_speed:.2f}', True, white)
    min_speed_lbl_rect = min_speed_lbl.get_rect()
    min_speed_lbl_rect.center = (450, 35)
    screen.blit(min_speed_lbl, min_speed_lbl_rect)

    # display the max_speed
    max_speed_lbl = font.render(f'Max speed: {max_speed:.2f}', True, white)
    max_speed_lbl_rect = max_speed_lbl.get_rect()
    max_speed_lbl_rect.center = (640, 35)
    screen.blit(max_speed_lbl, max_speed_lbl_rect)

    # display conjuction
    " calcul du taux d'embouteillage "
    if vehicle_group.sprites(): taux_embouteillage= float(f'{ 0.334*len(vehicle_group)* vehicle_group.sprites()[0].rect.width/ width:.2f}')
    else:                       taux_embouteillage= 0

    max_speed_lbl = font.render(f'Conjuction: {taux_embouteillage:.2f}', True, white)
    max_speed_lbl_rect = max_speed_lbl.get_rect()
    max_speed_lbl_rect.center = (830, 35)
    screen.blit(max_speed_lbl, max_speed_lbl_rect)

    # display the simulation_speed
    simulation_speed_lbl = font.render(f' Acceleration:  x {coef_changing_simulation_speed:.2f}', True, white)
    simulation_speed_lbl_rect = simulation_speed_lbl.get_rect()
    simulation_speed_lbl_rect.center = (1020, 35)
    screen.blit(simulation_speed_lbl, simulation_speed_lbl_rect)


    # check if there's a head on collision
    # if True, change the incoming vehicle's speed
    for vehicle1 in vehicle_group:
        for vehicle2 in vehicle_group:
            if pygame.sprite.collide_rect(vehicle1, vehicle2) and vehicle1!=vehicle2:
                if vehicle1.rect.right< vehicle2.rect.right :
                    vehicle1.speed = vehicle2.speed
                    if vehicle1.speed: vehicle1.rect.x-= step_backword
                    else:              vehicle1.rect.x-= step_backword/1.3
                else : 
                    vehicle2.speed = vehicle1.speed
                    if vehicle2.speed: vehicle2.rect.x-= step_backword
                    else:              vehicle2.rect.x-= step_backword/1.3
    
    ### updating graph ###
    # 1. for the second lane: freinage des vehicules
    if simulation_case == 2: 
        graph_list_temps.append(temps)
        for i in range(3):
            lane= lanes[i]
            nbr_vehicles_in_lane = len([v for v in vehicle_group if v.rect.center[1] == lane])
            graph_list_bouchons_longs[i].append(nbr_vehicles_in_lane)

    # 2. for the third lane: changement de ligne
    elif simulation_case == 3:  
        graph_list_nbr_of_lanes_changing.append(nbr_of_lanes_changing)
        graph_list_taux_embouteillage.append(taux_embouteillage)

    # draw the vehicles
    vehicle_group.draw(screen)          
    pygame.display.update()

pygame.quit()