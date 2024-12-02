#Groupe-Widget du graphique d'évolution d'une espèce selon le temps

import customtkinter as ctk
import tkinter as tk
import numpy as np
import pandas as pd

from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg) 

from pseudo_carte import PseudoCarte
from recherche import SearchWidget
from fonction import getDistanceFromLatLonInKm
from photo import Photo

#Classe principale
class GraphiqueEvolution(ctk.CTkFrame):
    def __init__(self, spec, data:pd.DataFrame, master=None):
        super().__init__(master)
        self.master=master
        self.spec = spec
        self.data = data
        self.canvas=None

        #Trouver n'importe quelle ligne du dataframe qui correspond à l'espèce afin d'avoir des informations supplémentaires sur celle-ci
        self.ex_line = self.data.loc[0, :]
        i = 0
        while(self.ex_line["especes"]!=self.spec and i<8131): #Tant que l'espèce ne correspond pas, continuer à chercher
            self.ex_line=self.data.loc[i, :]
            i+=1

        self.data = self.data.drop(columns=["groupe"]).copy()

        #Transformer la date en ne conservant que l'année pour chaque ligne
        for i, case in enumerate(self.data['date']):
            annee=case[0:4]
            self.data.loc[i, 'date'] = annee

        #Déterminer les années minimale et maximale du dataframe
        self.annee_min = int(self.data['date'].min())
        self.annee_max = int(self.data['date'].max())

        #Continuer la construction du graphique
        self.construct()

    #Continue la construction de la classe
    def construct(self, filter=None, filtertype=None):

        #Filtrer le dataframe selon l'espèce et selon les filtres, s'il y en a
        if(filtertype=="radius"):#Si le type de filtre est radius, il faut vérifier différement que par comparaison directe
            x, y, radius = filter #Déstructuration du filtre tuple pour avoir les coordonnées x et y du centre du rayon donné, ainsi que radius, la longueur du rayon
            data_spec=self.radius_filtered(df = self.data, x = x, y = y, radius = radius)
        elif(filter):data_spec=self.data[(self.data["especes"]==self.spec) & (self.data[filtertype]==filter)] #Si un filtre est défini, la case correspondant au type de filtre doit correspondre au filtre
        else:data_spec=self.data[self.data["especes"]==self.spec] #Masque pour filtrer selon l'espèce en argument

        self.data_count = data_spec.groupby("date").size().reset_index() #Compte le nombre d'apparition de l'espèce pour la date
        self.data_count['date']=pd.to_numeric(self.data_count['date']) #Transforme les dates de string à nombre pour les comparer après avec le numpy

        dicto = {'annee':[],'quantite':[]} #Création d'un dictionnaire pour ensuite créer un dataframe neuf
        self.data_info = pd.DataFrame(dicto).copy() #Création d'un dataframe neuf parce que c'est plus pratique
        self.data_info['annee']=np.arange(self.annee_min,self.annee_max,1) #Toutes les années de 1900 à 2024
        self.data_info = self.data_info.copy()

        #Pour chaque année de 1900 à 2024, comparer avec le dataframe originel pour voir s'il y a une valeur (nombre d'observations) cette année là où s'il n'y a pas d'observations
        #Et selon le résultat assigner la valeur dans le dataframe neuf
        for i, case in enumerate(self.data_info['annee']):
            val_pr_annee = self.data_count[self.data_count['date']==int(case)].reset_index() #Masque pour filtrer seulement la valeur à l'année i
            if(val_pr_annee.empty==False): self.data_info.loc[i, "quantite"] = val_pr_annee.loc[0,0] #Si le dataframe n'est pas vide, alors extirper sa valeur
            else: self.data_info.loc[i, "quantite"] = 0 #Si le dataframe est vide, alors il n'y a pas d'observations cette année-là, il faut donc assigner 0

        #Création et affichage du graphique
        #S'il y a un filtre, le communiquer au graphique. Sinon, indiquer qu'il n'y en a pas
        if(filter and filtertype=="region"): self.create_graph("en "+str(filter)) 
        elif(filter and filtertype=="nom_plan_eau"): self.create_graph("au "+str(filter))
        elif(filter and filtertype=="radius"): self.create_graph("dans le rayon spécifié")
        else: self.create_graph() 

        #Créer les autres widgets
        self.create_widgets()

    #Fonction qui crée et affiche le graphique dans la page
    def create_graph(self, filter="au Québec"):
        #Création de la figure
        self.frame = Figure(figsize = (15, 30))

        #Assignement des axes selon le nouveau dataframe
        x = self.data_info["annee"]
        y = self.data_info["quantite"]

        #Création du plot
        plot = self.frame.add_subplot(111) #Ça je sais pas à quoi ça sert
        plot.plot(x,y, "-o", color="green", label=f"Nombre d'observations de {self.spec} pour l'année")
        plot.set_xlabel("Années")
        plot.set_ylabel(f"Nombre d'observations de de {self.spec}")
        plot.set_xticks(np.arange(self.annee_min,self.annee_max,5))
        plot.set_label(f"Nombre d'observations de {self.spec} pour l'année")
        plot.set_title(f"Nombre d'observations de {self.spec} {filter} selon le temps")
        plot.legend(loc="upper left")
        plot.grid()

        self.canvas = FigureCanvasTkAgg(self.frame, master=self)
        self.canvas.draw()

        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    #Fonction de création et d'affichage des widgets
    def create_widgets(self):

        #Label d'informations supplémentaires
        self.info_label = ctk.CTkLabel(self)
        txt = ""
        txt += "Groupe : "+ str(self.ex_line["groupe"])+"\n"
        txt += "Nom latin : "+ str(self.ex_line["especes"])+ "\n"
        txt += "Espèce : "+ str(self.ex_line["nom_commun"])
        self.info_label.configure(text=txt, bg_color="white")
        self.info_label.place(x=0, y=20)

        #Photo de l'espèce
        self.photo = Photo(self)
        self.photo.place(x=0, y=100)
        self.photo.set_photo(self.ex_line["especes"], self.ex_line["nom_commun"], size=0.3)
        self.photo.configure(width=100, height=100)

        #Frame pour les boutons pour ajouter des filtres
        self.addfilterframe = ctk.CTkFrame(self, width=150, bg_color="white", fg_color="white")
        self.addfilterframe.place(x=1365, y=0)

        #Label
        self.filterlabel = ctk.CTkLabel(self.addfilterframe, text="Filtres")
        self.filterlabel.grid(row=0, padx=10, pady=5)

        #Bouton ajouter filtre région
        self.addregionbutton = ctk.CTkButton(self.addfilterframe, text="Ajouter région")
        self.addregionbutton.configure(command=lambda: self.show_map(mode="region"))
        self.addregionbutton.grid(row=1, padx=10, pady=5)

        #Bouton ajouter filtre plan d'eau
        self.addeaubutton = ctk.CTkButton(self.addfilterframe, text="Ajouter étendue d'eau", command=self.show_search)
        self.addeaubutton.grid(row=2, padx=0, pady=5)

        #Bouton ajouter filtre rayon
        self.radiusbutton = ctk.CTkButton(self.addfilterframe, text="Ajouter rayon")
        self.radiusbutton.configure(command=lambda: self.show_map(mode="radius"))
        self.radiusbutton.grid(row=3, padx=0, pady=5)

    #Afficher la carte temporaire pour choisir la région à utiliser comme filtre
    def show_map(self, mode):

        #Faire la place pour la carte
        self.swap_screen()
        
        #Carte temporaire
        self.maplabel = ctk.CTkLabel(self.midframe)
        self.maplabel.pack()
        self.tempmap = PseudoCarte(None, master=self.midframe)
        self.tempmap.pack(expand=True, fill="both")
        
        #Ajouter un waypoint à la position donnée par l'IP
        self.tempmap.set_waypoint(self.master.loc[1], self.master.loc[0])

        #Selon le mode en argument
        if(mode=="region"):
            self.addeaubutton.configure(state=tk.DISABLED)
            self.radiusbutton.configure(state=tk.DISABLED)
            self.maplabel.configure(text="Choisissez une région")
            self.tempmap.click_var.set("Info")
            self.tempmap.click_info.configure(state=tk.NORMAL)
            self.tempmap.click_region.configure(state=tk.DISABLED)
            self.tempmap.click_rayon.configure(state=tk.DISABLED)

            self.addregionbutton.configure(command=self.add_filter_region) #Remapper le bouton

        elif(mode=="radius"):
            self.addeaubutton.configure(state=tk.DISABLED)
            self.addregionbutton.configure(state=tk.DISABLED)
            self.maplabel.configure(text="Sélectionnez un rayon")
            self.tempmap.click_var.set("Rayon-nograph")
            self.tempmap.click_rayon.configure(state=tk.DISABLED)
            self.tempmap.click_info.configure(state=tk.DISABLED)
            self.tempmap.click_region.configure(state=tk.DISABLED)

            self.radiusbutton.configure(command=self.add_filter_radius) #Remapper le bouton

    def show_search(self):
        #Faire la place pour la recherche temporaire
        self.swap_screen()

        #Recherche temporaire
        self.srchlabel = ctk.CTkLabel(self, text="Sélectionnez une étendue d'eau")
        self.srchlabel.place(x=410, y=160)
        self.tempsearch = SearchWidget(data=self.master.data, master=self.midframe)
        self.tempsearch.grid(row=0,column=0, sticky="nsew")
        self.tempsearch.displaylabel.configure(width=2, font=("Arial",1))

        #Remapper le bouton
        self.addregionbutton.configure(state=tk.DISABLED)
        self.radiusbutton.configure(state=tk.DISABLED)
        self.addeaubutton.configure(command=self.add_filter_eau)
        

    #Reconstruit l'instance en y ajoutant le filtre de région
    def add_filter_region(self):
        self.construct(filter=self.tempmap.region, filtertype="region")

    #Reconstruit l'instance en y ajoutant le filtre de plan d'eau
    def add_filter_eau(self):
        self.construct(filter=self.tempsearch.eau, filtertype="nom_plan_eau")

    #Reconstruit l'instance en y ajoutant le filtre de rayon
    def add_filter_radius(self):
        self.construct(filter=(self.tempmap.x, self.tempmap.y, self.tempmap.radius), filtertype="radius")

    #Enlève le graphique pour plutôt placer un frame qui contiendra un widget temporaire
    def swap_screen(self):
        #Enlever le graphique de l'affichage
        self.canvas.get_tk_widget().destroy()
        self.canvas=None

        #Frame pour afficher le widget temporaire
        self.srchlabel = None
        self.midframe = ctk.CTkFrame(self, width=300, height=300)
        self.midframe.place(relx=0.25, rely=0.25, relwidth=0.5, relheight=0.5)
        self.midframe.columnconfigure(0,weight=8)
        self.midframe.columnconfigure(1,weight=16)
        self.midframe.rowconfigure(0,weight=1)

    #Pseudo-masque pour filtrer les données selon l'espèce ET le filtre de rayon
    def radius_filtered(self, df:pd.DataFrame, x, y, radius):
        #Code un peu volé à Adam dans graph-evolution mais amélioré parce que je déteste concatenate et en plus c'est plus optimisé comme ça :D
        filt_data = pd.DataFrame(columns=df.columns)
        for i in range(0, df.shape[0]):
            line = df.loc[i]
            if (getDistanceFromLatLonInKm(x, y, line["longitude"], line["latitude"]) <= radius) and line["especes"]==self.spec:
                filt_data.loc[len(filt_data)] = line
        return filt_data