import pygame
import random

class Vehicle(pygame.sprite.Sprite):
    
    def __init__(self, image, x, y, speed):
        pygame.sprite.Sprite.__init__(self)
        
        # scale the image down so it's not wider than the lane
        image_scale = 100 / image.get_rect().width
        new_width = image.get_rect().width * image_scale
        new_height = image.get_rect().height * image_scale
        self.image = pygame.transform.scale(image, (new_width, new_height))
        
        self.speed= speed
        self.init_speed= speed
        self.dalay_before_vehicle_reboting=0

        self.is_allowed_to_change_lane= True
        self.delay_before_rechanging_lane=0
        
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
    
    def changing_lane(self,vehicle_group,lanes,probability, screen):
        if random.random() < probability and self.speed and self.rect.left > 30:
            pas=0
            if self.rect.center[1] == lanes[0]:
                pas= 100
            elif self.rect.center[1] == lanes[1]:
                pas= random.choice((100,-100))
            elif self.rect.center[1] == lanes[2]:
                pas= -100
            self.rect.y +=pas

            for vehicle in vehicle_group:
                if pygame.sprite.collide_rect(self, vehicle) and self!=vehicle:
                    self.rect.y -=pas
                    break
            else:
                self.is_allowed_to_change_lane= False
                self.rect.y -= pas
                init_lane= self.rect.center[1]
                self.speed=0
                for v in vehicle_group:
                    if all((v!=self, 
                           v.rect.center[1]==init_lane,
                           1.3*v.rect.width > self.rect.left-v.rect.right > 0)):
                        if v.speed > 1.5: v.speed*=0.5 

                p=6
                signe_pas= 1 if pas > 0 else -1
                while pas :
                    if abs(pas)> p: 
                        self.rect.y += p * signe_pas
                        pas-= p* signe_pas
                    else : 
                        self.rect.y += pas
                        pas=0
                    vehicle_group.draw(screen)
                    pygame.display.update(self)
                    pygame.time.delay(3)
                
                return True
        return False

    def update_delay_before_rechanging_lane(self,delay):
        if not self.is_allowed_to_change_lane:
            self.delay_before_rechanging_lane+=1

            if self.delay_before_rechanging_lane > delay:
                self.delay_before_rechanging_lane=0
                self.is_allowed_to_change_lane= True

    def update_speed_state(self, delay):
        #check if the vehicle is stoped or not
            if self.speed == 0:
                self.dalay_before_vehicle_reboting+=1
                if self.dalay_before_vehicle_reboting > delay:
                    self.speed = self.init_speed *0.7
                    self.dalay_before_vehicle_reboting=0
    
    
