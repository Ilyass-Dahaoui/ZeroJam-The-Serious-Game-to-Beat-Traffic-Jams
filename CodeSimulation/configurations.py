""" 
REMARQUES :  1. to save graphs, tap 's'


    premier cas: vitesse constante ==>  CONSTANT_SPEED=True   
                                        CHANGE_LANE=False  
                                        STOP_VEHICLES=False

    deuxieme cas: freinage des vehicules ==> CONSTANT_SPEED=False  
                                            CHANGE_LANE=False  
                                            STOP_VEHICLES=True

    troisieme cas: changement de ligne ==>  CONSTANT_SPEED=False  
                                            CHANGE_LANE=True  
                                            STOP_VEHICLES=False

"""

### parameters of the window ### 
width = 1300
height = 500

### game settings ### 
speed = 2

# speed configuration
CONSTANT_SPEED= 0
''' 
if CONSTANT_SPEED==True then the vehicule's speed will be a random value in the interval 
                                [speed-alpha_changing_speed,speed+alpha_changing_speed] '''
alpha_changing_speed = 2
interval_changing_speed=(max(2,speed-alpha_changing_speed),max(4,speed+alpha_changing_speed))

# changing lanes configuration
CHANGE_LANE= 0
probability_of_changing_lane= 0.05
delay_before_rechanging_lane= 400 # units 

# freinage configuration
STOP_VEHICLES= 1
probability_of_stoping_vehicles= 0.01
delay_before_vehicle_reboting= 100 # units 