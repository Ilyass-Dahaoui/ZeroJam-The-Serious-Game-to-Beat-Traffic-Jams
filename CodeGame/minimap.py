import pygame
import math
from numpy import linspace

class Minimap:
    def __init__(self, window_width, window_height ):
        self.radius = window_width / 12
        self.x = 3 * self.radius / 2
        self.y = window_height - 3 * self.radius / 2

        self.nbr_road_lines= 28 # représente le nombre des lines à afficher dans le minimap devant et derrière the player's car
        self.start_road_lines = 20
        self.road_length = self.radius / self.nbr_road_lines
        self.player_car_radius= player_car_length = self.road_length*1.04
        
        #self.car_rect = pygame.Rect(self.x , self.y - player_car_length/2, player_car_length, player_car_length)
        self.car_rect= None # si None, the car will be represented by a circle


        self.background_color = pygame.Color("black")
        self.road_color = pygame.Color(128, 128, 128)
        self.player_color = pygame.Color("red")
        self.cars_color = pygame.Color("white")

    def get_line_curve(self, i):
        line_curve = 0
        if 300 < i < 700:
            line_curve = 0.5

        if i > 1100:
            line_curve = -0.7
        return line_curve
    
    def draw2(self, screen, carPosition, lines):
        nbr_lines= len(lines)
        pygame.draw.circle(screen, self.background_color, (self.x, self.y), self.radius)


        front_x, front_y = self.x, self.y - self.road_length / 2
        back_x, back_y = self.x, self.y + self.road_length / 2

        current_x, current_y = front_x, front_y
        next_x, next_y = 0, 0
        running_angle = 0

        # render track in front of car
        for i in range(0,self.start_road_lines+ 0):
            i= (carPosition +i)% nbr_lines
            angle = self.get_line_curve(i)
            
            next_x, next_y = current_x + self.road_length * math.sin(running_angle ), current_y - self.road_length * math.cos(running_angle )
            color= self.road_color
            pygame.draw.line(screen, color , (current_x  -4, current_y), (next_x -4, next_y), 3)  
            pygame.draw.line(screen, color , (current_x , current_y), (next_x, next_y), 3)  
            pygame.draw.line(screen, color , (current_x  +4.5, current_y), (next_x +4.5, next_y), 3)  
            if lines[i].car is not None :
                color= self.cars_color 
                pygame.draw.circle(screen, self.cars_color, ((current_x+next_x)/2, (current_y+next_y)/2), self.player_car_radius)

            current_x, current_y = next_x, next_y
            running_angle += angle/40
        
        current_x, current_y = back_x, back_y
        next_x, next_y = 0, 0
        running_angle = 0

        # render track behind car
        for i in range(0,self.nbr_road_lines+0):
            i= ( carPosition -i )% nbr_lines
            angle = self.get_line_curve(i)
             
            next_x, next_y = current_x + self.road_length * math.sin(running_angle ), current_y + self.road_length * math.cos(running_angle )
            color= self.road_color
            pygame.draw.line(screen, color , (current_x  -4, current_y), (next_x -4, next_y), 3)  
            pygame.draw.line(screen, color , (current_x , current_y), (next_x, next_y), 3)  
            pygame.draw.line(screen, color , (current_x  +4.5, current_y), (next_x +4.5, next_y), 3)  
            if lines[i].car is not None:
                positions_X= (-1.8,-0.48,0.65 )
                _current_x= current_x + { 0: -4, 1:0, 2: 4.5}[positions_X.index(lines[i].carX)]
                color= self.cars_color 
                pygame.draw.circle(screen, self.cars_color, (_current_x, current_y), self.player_car_radius)
                #pygame.draw.circle(screen, self.cars_color, ((current_x+next_x)/2, (current_y+next_y)/2), self.player_car_radius)
            current_x, current_y = next_x, next_y
            running_angle += angle/40

        if self.car_rect is None:
            pygame.draw.circle(screen, self.player_color, (self.x, self.y), self.player_car_radius)
        else: 
            pygame.draw.rect(screen, self.player_color, self.car_rect)

    def draw(self, screen, carPosition, carX, lines):
        pygame.draw.circle(screen, self.background_color, (self.x, self.y), self.radius)
        b=2.8
        a=self.radius*0.8
        X= linspace(self.x -self.radius/2 , self.x+self.radius/2, 1600)
        Y= list(map(lambda t: self.y+a*math.cos(t/b) , X))

        for i in range(len(X)-1):
            pygame.draw.line(screen, self.road_color , ( X[i] , Y[i]), (X[i+1], Y[i+1]) , 3)
            for ii in range(1,4):
                if getattr(lines[i],f'car{ii}') is not None and getattr(lines[i],f'carX{ii}') == carX:
                    pygame.draw.circle(screen, self.cars_color, (X[i] , Y[i]), self.player_car_radius*1.2)
            
            if i== carPosition: pygame.draw.circle(screen, self.player_color, (X[i] , Y[i]), self.player_car_radius*1.2)


            




    



