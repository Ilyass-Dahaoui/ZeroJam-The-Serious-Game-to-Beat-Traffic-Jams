import os
import matplotlib.pyplot as plt
folder_name= 'graphs'
graphe_color ='black'

class Graphe:
    def __init__(self):
        self.path= None
        self.folder_creation()

    def folder_creation(self):
        path=rf'.\{folder_name}'
        if not os.path.exists(path): 
            os.mkdir(path)

        n=0
        while True:
            n+=1
            path = rf'.\{folder_name}\simulation{n}'
            if not os.path.exists(path): 
                os.mkdir(path)
                self.path = path
                break

    
    def create_graph_changing_lanes_case(self, nbr_of_lanes_changing, taux_embouteillage):
        # figure 
        fig, ax = plt.subplots(nrows=1, ncols=1,figsize=(8,6))
        ax.set_title( "Taux d'embouteillage en fct du nombre de changement de voies", color= graphe_color, family='Algerian')
        ax.set_xlabel("Nombre de changement de voies", color= graphe_color, family='Arial')
        ax.set_ylabel("Taux d'embouteillage", color= graphe_color, family='Arial')
        ax.plot(nbr_of_lanes_changing, taux_embouteillage, color='red')
        
        self.graph_style(ax)
        fig.savefig(rf"{self.path}\changing_lanes_case.png")
    
    def create_graph_freinage_case(self, temps, bouchons_longs):
        # bouchons_longs will contain tree lists. Each list will contains bouchons of the specific lane
        #lanes's colors
        top_lane_color = 'red'
        center_lane_color = 'green'
        buttom_lane_color = 'yellow'
        lanes_colors= [top_lane_color, center_lane_color, buttom_lane_color]

                ######## figure 1: une courbe solid et deux courbes dotted #########
        fig, ax = plt.subplots(nrows=1, ncols=1,figsize=(8,6))
        ax.set_title( "Longueur des bouchons en fct du temps", color= graphe_color, family='Algerian')
        ax.set_xlabel("Temps", color= graphe_color, family='Arial')
        ax.set_ylabel("Longueur des bouchons", color= graphe_color, family='Arial')
        ax.plot(temps, bouchons_longs[0], color=top_lane_color, label="Top lane")
        ax.plot(temps, bouchons_longs[1], color=center_lane_color, label="Center lane" , linestyle="dotted")
        ax.plot(temps, bouchons_longs[2], color=buttom_lane_color, label="Bottom lane" , linestyle="dotted")

        leg=self.graph_style(ax)
        leg.texts[0].set_color(top_lane_color)
        leg.texts[1].set_color(center_lane_color)
        leg.texts[2].set_color(buttom_lane_color)
        fig.savefig(rf"{self.path}\freinage_case1.png")

                ######## figure 2: une seule courbe soli, 1 ax + for top lane #########
        fig, ax = plt.subplots(nrows=1, ncols=1,figsize=(8,6))
        ax.set_title( "Longueur des bouchons en fct du temps pour la voie 1", color= graphe_color, family='Algerian')
        ax.set_xlabel("Temps", color= graphe_color, family='Arial')
        ax.set_ylabel("Longueur des bouchons", color= graphe_color, family='Arial')
        ax.plot(temps, bouchons_longs[0], color=top_lane_color)
        self.graph_style(ax, False)
        fig.savefig(rf"{self.path}\freinage_case2.png")

                ######## figure 3: trois courbes, trois axes #########
        fig, axes = plt.subplots(nrows=3, ncols=1,figsize=(8,6))
        # Ajout d'un titre à la figure
        fig.suptitle("Longueur des bouchons en fct du temps")
        axes_lbls=[ "Top lane", "Center lane", "Bottom lane" ]

        for n_ax in range(len(axes)):
            ax=axes[n_ax]	
            ax.set_title( f"{axes_lbls[n_ax]}", color= graphe_color, family='Algerian')
            ax.set_xlabel("Temps", color= graphe_color, family='Arial')
            ax.set_ylabel("Longueur", color= graphe_color, family='Arial')
            ax.set_ylim(0,20)
            ax.plot(temps, bouchons_longs[n_ax], color= lanes_colors[n_ax], label= axes_lbls[n_ax])
            self.graph_style(ax, False)

        # Ajustement des marges entre les axes
        plt.subplots_adjust(hspace=1)
        fig.savefig(rf"{self.path}\freinage_case3.png")
        

    def graph_style(self, ax, show_legend=True):
        ax.grid(False)
        ax.spines['top'].set_color( graphe_color)
        ax.spines['bottom'].set_color( graphe_color)
        ax.spines['left'].set_color( graphe_color)
        ax.spines['right'].set_color( graphe_color)
        ax.tick_params(colors= graphe_color)

        if show_legend:
            leg = plt.legend(loc='best', frameon=False)
            return leg
       