# Pseudo 3D game in Python : jeu sérieux

How to play this game:
    - to move forward, press the up key
    - to move back, press the down key
    - to move left, press the left key
    - to move right, press the right key

    - if you want to change the speed, press a number between 1 and 9 :
            1 <==> 10km/h
            2 <==> 20km/h
            3 <==> 30km/h
            4 <==> 40km/h
            5 <==> 50km/h
            6 <==> 60km/h
            7 <==> 70km/h
            8 <==> 80km/h
            9 <==> 90km/h

            the default value is 1 <==> 10km/h
    
How to calculate the score :
    - if you pass while the 'feu' is 'rouge' : score -=10
    - if you pass while the 'feu' is 'vert' : score +=5

    - if you pass while the 'pieton' is in the 'passage' : score -=10
    
    - if you exceed the max speed : score -= 5
    - if you respect the max speed : score +=1

    - if you change the lane (voie) : score -=1 for each 20*100=2000 transitions

Remarques :
    - to install pygame : type 'pip install pygame' in the cmd
    - the limit speed panel determines the max speed
    - if your score <= 0 ==> game over, press spacebar to repaly the game


ENJOY THE GAME ;) 

