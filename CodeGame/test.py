import matplotlib.pyplot as plt
import math as mt

'''

pressing c ==> reference = player's car
pressing r ==> reference = the road :
    1. courbe cosinus (pressing something else)
    2. courbe circle in cercle in cercle  ;) :)

- drawing 3 roads : the road will be changed if the player changes the lane
- possibility of focusing on a specific road : r + rigthKey or leftKey

- collision detection
- cars must respect traffic signals 

- adding the "taux d'embouteillage" option
- statistics : 
'''

fig,ax = plt.subplots()
X= range(1600)
a=2
b=60
Y= list(map(lambda t: a*mt.cos(t/b), X))
b=60
a=500
X2= list(map(lambda t: (t/a)*mt.sin(t/b) , X))
Y2= list(map(lambda t: (t/a)*mt.cos(t/b) , X))

#ax.plot(X, Y)
ax.plot(X2, Y2)

plt.show()