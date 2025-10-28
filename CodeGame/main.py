import math
import time
import random
import pygame
import sys
from typing import List, Dict
from minimap import Minimap


WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 700

roadW = 2000  # road width (left to right)
segL = 200 # segment length (top to bottom)
camD = 0.84  # camera depth
show_N_seg = 300
roadLanes=3 # nbr of road's lanes
score= init_score =100
nbr_cars= 100


point_for_respecting_regles_de_circulation=5
point_for_no_respecting_regles_de_circulation=-10
''' configurations du feu de circulation'''
i_feu_rouge1=300 # la place du feu_rouge1
i_feu_rouge2=800 # la place du feu_rouge2
TIMER_FEU_ROUGE = pygame.USEREVENT + 1
intervale_feu_rouge=6000 # in seconds
def change_feu_de_circulation( traffic_signals,lines):
    for i in (i_feu_rouge1, i_feu_rouge2):
        feu=lines[i].sprites[-1][0]
        if feu ==  traffic_signals['feu_rouge']:
            lines[i].sprites[-1][0]= traffic_signals['feu_vert']
        else: 
            lines[i].sprites[-1][0]= traffic_signals['feu_rouge']

#traffic signals: speed limit panels {position, speed_limit}
speed_limit_panels={
    10: 20,
    120: 30, 
    230: 10,
    360: 40,
    500: 10,
    600: 30,
    850: 40,
    1000: 50,
    1200: 30,
    1400: 60
}
speed_limit_panels_positions= sorted(speed_limit_panels.keys(), reverse= True)
def calc_max_speed(player_position):
    player_position+= 12
    max_speed = 20
    for pos in speed_limit_panels_positions:
        if player_position > pos:
            max_speed= speed_limit_panels[pos]
            break
    return max_speed
    
def update_score_speed_limit_panels(max_speed_respected):
    global score
    if max_speed_respected : score += 1
    else : score-=5

changing_score_verification={i_feu_rouge1:0,
                             i_feu_rouge2:0 } 
                                # pour chaque traffic signal, on vérifie si le plalyer a dépasser le
                                # et donc le score a changer ou non, cela est pour eviter de modifer
                                # le score plusieurs fois
def update_score_feu_rouge(player_position,lines,traffic_signals,pas_per_move):
    global score
    for i in (i_feu_rouge1, i_feu_rouge2):
        if i-16 <= player_position <= i-12+pas_per_move  and changing_score_verification[i]==0:
            if lines[i].sprites[-1][0]== traffic_signals['feu_rouge']:
                score+= point_for_no_respecting_regles_de_circulation
            else : 
                score+= point_for_respecting_regles_de_circulation
            changing_score_verification[i]=600//pas_per_move

passage_des_pietons_positions=[
    (56,60),
    (602,605),
]
decalage_pieton= 2 # how much distance, nous allons le décaler du milieu de a et b
pieton_start=-20
pieton_stop= 20
pieton_speedY = 0.8
pieton_state=0 #indicate wich img, we will use
PIETON_UPDATE_STATE_TIMER = pygame.USEREVENT + 2
pieton_update_state_interval = 500 # en ms
passage_pieton_bornes = (-5,5) # indicate if the pieton is in the passage or not
time_before_updating_score_for_passage_des_pietons=[0]*len(passage_des_pietons_positions)
def update_pieton_state(lines, imgs_pieton):
    global pieton_state
    nbr_pieton_state= len(imgs_pieton)
    if pieton_state >= nbr_pieton_state:
        pieton_state = 0
    for a,b in passage_des_pietons_positions:
        i= (a+b)//2 +decalage_pieton
        line=lines[i]
        line.pieton= imgs_pieton[pieton_state]
        line.pietonX+= pieton_speedY
        if line.pietonX >= pieton_stop:
            line.pietonX= pieton_start  
    pieton_state +=1 

def update_score_for_passage_des_pietons(player_position, lines, pas_per_move):
    player_position+= 9
    global score

    for n in range(len(time_before_updating_score_for_passage_des_pietons)):
        if time_before_updating_score_for_passage_des_pietons[n]>0:
            time_before_updating_score_for_passage_des_pietons[n]-=1

    for n_pos,(a,b) in enumerate(passage_des_pietons_positions):
        i= (a+b)//2 +decalage_pieton 
        if all((i-5<= player_position <= i+4 +pas_per_move, 
               passage_pieton_bornes[0]<=lines[i].pietonX<=passage_pieton_bornes[1],
               time_before_updating_score_for_passage_des_pietons[n_pos]==0)):
            score-=10
            time_before_updating_score_for_passage_des_pietons[n_pos]=600// pas_per_move

dark_grass = pygame.Color(0, 154, 0)
light_grass = pygame.Color(16, 200, 16)
white_rumble = pygame.Color(255, 255, 255)
black_rumble = pygame.Color(0, 0, 0)
dark_road = pygame.Color(105, 105, 105)
light_road = pygame.Color(107, 107, 107)


class Line:
    def __init__(self, i):
        self.i = i
        self.x = self.y = self.z = 0.0  # game position (3D space)
        self.X = self.Y = self.W = 0.0  # game position (2D projection)
        self.scale = 0.0  # scale from camera position
        self.curve = 0.0  # curve radius
        self.clip = 0.0  # correct sprite Y position
        self.sprites: List[ List(pygame.surface, float) ] = [] # [ (sprite, 'spriteX')  ] # spriteX=sprite position X
        self.sprite_rects: List[ pygame.Rect ] = [] 

        self.pieton: pygame.surface = None
        self.pietonX = 0.0

        self.car1: pygame.surface = None
        self.carX1 = 0.0
        self.car2: pygame.surface = None
        self.carX2 = 0.0
        self.car3: pygame.surface = None
        self.carX3 = 0.0

        self.grass_color: pygame.Color = "black"
        self.rumble_color: pygame.Color = "black"
        self.road_color: pygame.Color = "black"

    def project(self, camX: int, camY: int, camZ: int):
        self.scale = camD / (self.z - camZ)
        self.X = (1 + self.scale * (self.x - camX)) * WINDOW_WIDTH / 2
        self.Y = (1 - self.scale * (self.y - camY)) * WINDOW_HEIGHT / 2
        self.W = self.scale * roadW * WINDOW_WIDTH / 2

    def drawSprites(self, draw_surface: pygame.Surface):
        # draw pieton if he exists
        self.drawPieton(draw_surface)

        # draw car if it exists
        self.drawCars(draw_surface)

        if self.sprites==[]:
            return
        
        for sprite, spriteX in self.sprites:
            w = sprite.get_width()
            h = sprite.get_height()
            destX = self.X + self.scale * spriteX * WINDOW_WIDTH / 2
            destY = self.Y + 4
            destW = w * self.W / 266
            destH = h * self.W / 266

            destX += destW * spriteX
            destY += destH * -1

            clipH = destY + destH - self.clip
            if clipH < 0:
                clipH = 0
            if clipH >= destH:
                return

            # avoid scalling up images which causes lag
            if destW > w:
                return

            # mask the sprite if below ground (clipH)
            scaled_sprite = pygame.transform.scale(sprite, (destW, destH))
            crop_surface = scaled_sprite.subsurface(0, 0, destW, destH - clipH)

            draw_surface.blit(crop_surface, (destX, destY))
    
    def drawPieton(self, draw_surface: pygame.Surface):
        if self.pieton is None:
            return
        
        w = self.pieton.get_width()
        h = self.pieton.get_height()
        destX = self.X + self.scale * self.pietonX * WINDOW_WIDTH / 2
        destY = self.Y + 4
        destW = w * self.W / 266
        destH = h * self.W / 266

        destX += destW * self.pietonX
        destY += destH * -1

        clipH = destY + destH - self.clip
        if clipH < 0:
            clipH = 0
        if clipH >= destH:
            return

        # avoid scalling up images which causes lag
        if destW > w:
            return

        # mask the pieton if below ground (clipH)
        scaled_pieton = pygame.transform.scale(self.pieton, (destW, destH))
        crop_surface = scaled_pieton.subsurface(0, 0, destW, destH - clipH)

        draw_surface.blit(crop_surface, (destX, destY))

    def drawCar(self, draw_surface: pygame.Surface, car, carX):
        if car is None:
            return
        
        w = car.get_width()
        h = car.get_height()
        destX = self.X + self.scale * carX * WINDOW_WIDTH / 2
        destY = self.Y + 4
        destW = w * self.W / 266
        destH = h * self.W / 266

        destX += destW * carX
        destY += destH * -1

        clipH = destY + destH - self.clip
        if clipH < 0:
            clipH = 0
        if clipH >= destH:
            return

        # avoid scalling up images which causes lag
        if destW > w:
            return

        # mask the car if below ground (clipH)
        scaled_car = pygame.transform.scale(car, (destW, destH))
        crop_surface = scaled_car.subsurface(0, 0, destW, destH - clipH)

        draw_surface.blit(crop_surface, (destX, destY))

    def drawCars(self, draw_surface: pygame.Surface):
        for car, carX in [(self.car1, self.carX1),
                          (self.car2, self.carX2),
                          (self.car3, self.carX3)]: self.drawCar(draw_surface, car, carX)

class Car:
    def __init__(self, lines, img, positionX, positionLine, speed, cars_positions_X):
        self.img= img
        self.positionLine= positionLine
        self.positionX= positionX
        self.lane= cars_positions_X.index(positionX)+1
        self.speed= speed # how lines the car will be pass in each iteration
        self.lines= lines

        lines[positionLine].car= img
        lines[positionLine].carX= positionX

    def move(self):
        #removing the car from the current line
        current_line= self.lines[self.positionLine]
        

        #adding speed
        newPositionLine = self.speed+self.positionLine
        if newPositionLine >= len(self.lines) :
            newPositionLine=0
        
        next_line=self.lines[(newPositionLine+4)%len(self.lines) ]
        if getattr(next_line,f'car{self.lane}') is None or getattr(next_line,f'carX{self.lane}')!=self.positionX:
            setattr(current_line,f'car{self.lane}', None)
            setattr(current_line,f'carX{self.lane}', 0.0)
        
            self.positionLine= newPositionLine
            new_line= self.lines[newPositionLine]
            setattr(new_line,f'car{self.lane}', self.img)
            setattr(new_line,f'carX{self.lane}', self.positionX)
        




def drawQuad(
    surface: pygame.Surface,
    color: pygame.Color,
    x1: int,
    y1: int,
    w1: int,
    x2: int,
    y2: int,
    w2: int,
):
    pygame.draw.polygon(
        surface, color, [(x1 - w1, y1), (x2 - w2, y2), (x2 + w2, y2), (x1 + w1, y1)]
    )


class GameWindow:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Jeu sérieux: HIZAZ")
        self.window_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.time.set_timer(TIMER_FEU_ROUGE, intervale_feu_rouge) 
        pygame.time.set_timer(PIETON_UPDATE_STATE_TIMER, pieton_update_state_interval) 
        self.clock = pygame.time.Clock()
        self.last_time = time.time()
        self.dt = 0

        #score label
        self.lbl_police = pygame.font.Font(None, 36)
        self.lbl_police_for_game_over = pygame.font.Font(None, 60)
        self.lbl_color= (0,0,0)
        self.score_lbl_position = (20, 20)
        self.current_speed_lbl_position = (180, 20)
        self.max_speed_lbl_position = (400, 20)

        # background
        self.background_image_for_game_over = pygame.image.load("images/game_over.jpg").convert_alpha()
        self.background_image_for_game_over = pygame.transform.scale(
            self.background_image_for_game_over, (WINDOW_WIDTH, WINDOW_HEIGHT)
        )
        self.background_image = pygame.image.load("images/bg.png").convert_alpha()
        self.background_image = pygame.transform.scale(
            self.background_image, (WINDOW_WIDTH, self.background_image.get_height())
        )
        self.background_surface = pygame.Surface(
            (self.background_image.get_width() * 3, self.background_image.get_height())
        )
        self.background_surface.blit(self.background_image, (0, 0))
        self.background_surface.blit(
            self.background_image, (self.background_image.get_width(), 0)
        )
        self.background_surface.blit(
            self.background_image, (self.background_image.get_width() * 2, 0)
        )
        self.background_rect = self.background_surface.get_rect(
            topleft=(-self.background_image.get_width(), 0)
        )
        self.window_surface.blit(self.background_surface, self.background_rect)

        # sprites
        self.sprites: List[pygame.Surface] = [ pygame.image.load(f"images/trees/{i}.png").convert_alpha()
                                              for i in range(6) ]
        
        self.left_building: List[pygame.Surface] = [ pygame.image.load(f"images/left_building/{i}.png").convert_alpha()
                                                    for i in range(15) ]
        self.right_building: List[pygame.Surface] = [ pygame.image.load(f"images/right_building/{i}.png").convert_alpha()
                                                    for i in range(15) ]

        self.pieton_imgs: List[pygame.Surface] = [ pygame.transform.scale(pygame.image.load(f"images/pieton/{i}.png").convert_alpha(),(60,120))
                                                    for i in range(1,9) ]
        fr=pygame.image.load(f"images/traffic_signals/feu_rouge.png").convert_alpha()
        scale=0.6
        size=(fr.get_width()*scale, fr.get_height()*scale )
        self.traffic_signals: Dict[pygame.Surface] = { 
                            'feu_rouge':pygame.transform.scale(fr,size),
                            'feu_vert':pygame.transform.scale(pygame.image.load(f"images/traffic_signals/feu_vert.png").convert_alpha(),size),
                            'feu_orange':pygame.transform.scale(pygame.image.load(f"images/traffic_signals/feu_orange.png").convert_alpha(),size)}
        
        panneau=pygame.image.load(f"images/traffic_signals/speed_limit_10.png").convert_alpha()
        size=(panneau.get_width()*0.3, panneau.get_height()*0.2 )
        self.traffic_signals['speed_limit_10']=pygame.transform.scale(panneau,size)
        for i in range(2,10):
           self.traffic_signals[f'speed_limit_{i}0']= pygame.transform.scale(pygame.image.load(f"images/traffic_signals/speed_limit_{i}0.png").convert_alpha(),size)
        

        self.player: pygame.Surface=pygame.image.load(f"images/player.png").convert_alpha()
        scale=0.30
        size= (self.player.get_width()*scale, self.player.get_height()*scale)
        self.player=pygame.transform.scale(self.player, size )

        self.cars_imgs : List[pygame.Surface] = [ pygame.transform.scale(pygame.image.load(f"images/cars/{i}.png").convert_alpha(),(size[0]*0.55,size[1]*0.55))
                                                 for i in range(8) ]
        self.cars : List[Car] =[] # we will fill it later

        self.minimap= Minimap(WINDOW_WIDTH,WINDOW_HEIGHT)
        

            
    def run(self):
        
        # create road lines for each segment
        lines: List[Line] = []
        for i in range(1600):
            line = Line(i)
            line.z = (
                i * segL + 0.00001
            )  # adding a small value avoids Line.project() errors

            # change color at every other 3 lines (int floor division)
            grass_color = light_grass if (i // 3) % 2 else dark_grass
            rumble_color = white_rumble if (i // 3) % 2 else black_rumble
            road_color = light_road if (i // 3) % 2 else dark_road

            line.grass_color = grass_color
            line.rumble_color = rumble_color
            line.road_color = road_color

            # right curve
            if 300 < i < 700:
                line.curve = 0.5
            # uphill and downhill
            if i > 750:
                line.y = math.sin(i / 30.0) * 1500

            # left curve
            if i > 1100:
                line.curve = -0.7

            # Sprites segments
            if i < 300 and i % 40 == 0:
                spriteX = -1.2
                sprite = self.sprites[4]
                line.sprites.append([sprite, spriteX])

            if i % 19 == 0:
                spriteX = 2.0
                sprite = self.sprites[5]
                line.sprites.append([sprite, spriteX])

            if i > 300 and i % 20 == 0:
                spriteX = -0.7
                sprite = self.sprites[3]
                line.sprites.append([sprite, spriteX])

            if i > 800 and i % 20 == 0:
                spriteX = -1.2
                sprite = self.sprites[0]
                line.sprites.append([sprite, spriteX])

            if i%17==0:
                spriteX = -1.9
                sprite = random.choice(self.left_building)
                line.sprites.append([sprite, spriteX])
            
            if i%19==0:
                spriteX = 1.5
                sprite = random.choice(self.right_building)
                line.sprites.append([sprite, spriteX])
            
            if i in speed_limit_panels:
                spriteX=0.8
                sprite= self.traffic_signals[f'speed_limit_{speed_limit_panels[i]}']
                line.sprites.append([sprite, spriteX])
            
            for a,b in passage_des_pietons_positions:
                if i== (a+b)//2 + decalage_pieton:
                    line.pieton = self.pieton_imgs[0]
                    line.pietonX= pieton_start # -20 to 20
            
            if i in (i_feu_rouge1, i_feu_rouge2): # il doit être tjrs le dernier à append
                spriteX=3
                sprite= self.traffic_signals['feu_rouge']
                line.sprites.append([sprite, spriteX])
            
            
            lines.append(line)

        #fill cars list
        Nn = len(lines)-2 # to avoid indice out of range
        position_line0= Nn//nbr_cars
        # distribuer la distance entre les voiture regulièrement
        cars_positions_line= [ position_line0*i for i in range(1,1+nbr_cars)]
        cars_positions_X= (-1.8,-0.48,0.65 )
        speeds= range(2,3) # 
        for i in range(nbr_cars):
            car= Car(lines,
                     random.choice(self.cars_imgs),
                     random.choice( cars_positions_X ), # choice a random lane: voie
                     cars_positions_line[i] , # choice a position line
                     random.choice(speeds), # choice a speed
                     cars_positions_X
                    )
            self.cars.append(car)

        N = len(lines)
        pos = 0
        playerX = 0  # player start at the center of the road
        playerY = 1500  # camera height offset
        speed = 0
        global score
        nbr_changing_lanes=0
        init_max_speed = 20 # to verify if the max speed is changed or not
        max_speed_respected : bool = True # if the max speed is respected all the sous-way,
                                          # we will add a score to the player, else we will 
                                          # soustract from it
        while True:
            self.dt = time.time() - self.last_time
            self.last_time = time.time()
            self.window_surface.fill((105, 205, 4))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type== TIMER_FEU_ROUGE and score>0:
                    change_feu_de_circulation(self.traffic_signals,lines)

                if event.type== PIETON_UPDATE_STATE_TIMER and score>0:
                    update_pieton_state(lines, self.pieton_imgs)

            if score <=0:  # check game over
                self.window_surface.blit(self.background_image_for_game_over, (0,0))
                self.window_surface.blit(self.lbl_police_for_game_over.render(f"GAME OVER", 
                                    True, (255,0,0)), (WINDOW_WIDTH//2 - 120,
                                                            20))
                self.window_surface.blit(self.lbl_police.render(f"Press the spacebar to replay ...", 
                                    True, (0,0,0)), (WINDOW_WIDTH//2 - 170,
                                                            80))
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    score=init_score
                    nbr_changing_lanes=0
                    max_speed_respected= True
                pygame.display.update()
                self.clock.tick(60)
                continue

            speed = 0
            acceleration = 1
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                speed += segL  # it has to be N integer times the segment length
            if keys[pygame.K_DOWN]:
                speed -= segL  # it has to be N integer times the segment length
            if keys[pygame.K_RIGHT]:
                playerX += 100
                nbr_changing_lanes+=1
                if nbr_changing_lanes>20: 
                    score-=1
                    nbr_changing_lanes=0
            if keys[pygame.K_LEFT]:
                playerX -= 100
                nbr_changing_lanes+=1
                if nbr_changing_lanes>20: 
                    score-=1
                    nbr_changing_lanes=0


            # avoid camera going below ground
            if playerY < 500:
                playerY = 500
            # acceleration
            for i in range(1,10):
                if keys[getattr(pygame,f'K_{i}')]:
                    acceleration=i

            speed*=acceleration # it has to be N integer times the segment length
            pos += speed

            # loop the circut from start to finish
            while pos >= N * segL:
                pos -= N * segL
            while pos < 0:
                pos += N * segL
            startPos = pos // segL


            ### moving cars ######################################################
            ######################################################################
            positions_X= (-2000, -400, 800 )
            for ipos in range(2,-1,-1):
                if playerX > positions_X[ipos] :
                    posX= ipos
                    break
            
            cars_positions_X= (-1.8,-0.48,0.65 )
            for car in self.cars:
                if car.positionX == cars_positions_X[posX] and car.positionLine in [ (startPos-i)%N for i in range(30)]:
                    continue

                car.move()



            #updating the player's score
            for key, value in changing_score_verification.items():
                if value>0:
                    changing_score_verification[key]-=1
            
            update_score_feu_rouge(startPos, lines, self.traffic_signals,speed//segL)


            x = dx = 0.0  # curve offset on x axis

            camH = lines[startPos].y + playerY
            maxy = WINDOW_HEIGHT

            if speed > 0:
                self.background_rect.x -= lines[startPos].curve * 2
            elif speed < 0:
                self.background_rect.x += lines[startPos].curve * 2

            if self.background_rect.right < WINDOW_WIDTH:
                self.background_rect.x = -WINDOW_WIDTH
            elif self.background_rect.left > 0:
                self.background_rect.x = -WINDOW_WIDTH

            self.window_surface.blit(self.background_surface, self.background_rect)
            

            # draw road
            for n in range(startPos, startPos + show_N_seg):
                current = lines[n % N]
                # loop the circut from start to finish = pos - (N * segL if n >= N else 0)
                current.project(playerX - x, camH, pos - (N * segL if n >= N else 0))
                x += dx
                dx += current.curve

                current.clip = maxy

                # don't draw "above ground"
                if current.Y >= maxy:
                    continue
                maxy = current.Y

                prev = lines[(n - 1) % N]  # previous line

                drawQuad(
                    self.window_surface,
                    current.grass_color,
                    0,
                    prev.Y,
                    WINDOW_WIDTH,
                    0,
                    current.Y,
                    WINDOW_WIDTH,
                )
                drawQuad(
                    self.window_surface,
                    current.rumble_color,
                    prev.X,
                    prev.Y,
                    prev.W * 1.2,
                    current.X,
                    current.Y,
                    current.W * 1.2,
                )
                drawQuad(
                    self.window_surface,
                    current.road_color,
                    prev.X,
                    prev.Y,
                    prev.W,
                    current.X,
                    current.Y,
                    current.W,
                )
                #draw lanes
                _roadLanes= roadLanes
                for a,b in passage_des_pietons_positions: # to draw passages des pietons
                    if a<= n <=b:
                        _roadLanes=10 
                        

                w1=current.W 
                w2=prev.W
                x1=current.X
                x2=prev.X 
                y1=current.Y
                y2=prev.Y
                line_w1 = (w1/20) / 2
                line_w2 = (w2/20) / 2
                
                lane_w1 = (w1*2) / _roadLanes
                lane_w2 = (w2*2) / _roadLanes
                
                lane_x1 = x1 - w1
                lane_x2 = x2 - w2
                
                for i in range(1,_roadLanes):
                    color_lane= dark_road if current.road_color==dark_road else white_rumble
                    if _roadLanes!= roadLanes: color_lane= white_rumble
                    lane_x1 += lane_w1
                    lane_x2 += lane_w2
                    pygame.draw.polygon(self.window_surface, color_lane, 
                        [(lane_x1-line_w1, y1),(lane_x2-line_w2, y2), (lane_x2+line_w2, y2),
                          (lane_x1+line_w1, y1)
                        ] )
                
                #draw player
                self.window_surface.blit(self.player, ((WINDOW_WIDTH-self.player.get_width())//2,
                                                       WINDOW_HEIGHT-self.player.get_height()))


            # draw sprites
            for n in range(startPos + show_N_seg, startPos + 1, -1):
                lines[n % N].drawSprites(self.window_surface)
            
            # draw labels
            current_speed=10*speed//segL
            max_speed= calc_max_speed(startPos)
            if init_max_speed!= max_speed:
                init_max_speed = max_speed
                # change score 
                update_score_speed_limit_panels(max_speed_respected)
                max_speed_respected = True

            # if the max speed is respected, the lbl will be in green else in red
            if current_speed <= max_speed:
                color_max_speed= (0,255,0)
            else:
                color_max_speed = (255,0,0)
                max_speed_respected= False

            update_score_for_passage_des_pietons(startPos, lines, speed//segL)
            self.window_surface.blit(self.lbl_police.render(f"Score: {score}", 
                                    True, self.lbl_color), self.score_lbl_position)
            self.window_surface.blit(self.lbl_police.render(f"Speed: {current_speed} km/h", 
                                    True, self.lbl_color), self.current_speed_lbl_position)
            self.window_surface.blit(self.lbl_police.render(f"Max speed: {max_speed} km/h", 
                                    True, color_max_speed ), self.max_speed_lbl_position)

            positions_X= (-2000, -400, 800 )
            for ipos in range(2,-1,-1):
                if playerX > positions_X[ipos] :
                    posX= ipos
                    break
            cars_positions_X= (-1.8,-0.48,0.65 )
            self.minimap.draw(self.window_surface, startPos, cars_positions_X[posX], lines)

            pygame.display.update()
            self.clock.tick(60)


if __name__ == "__main__":
    game = GameWindow()
    game.run()
