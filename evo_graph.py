#Groupe-Widget du graphique d'évolution d'une espèce selon le temps

import customtkinter as ctk
import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,  
NavigationToolbar2Tk) 

#Classe principale
class GraphiqueEvolution(ctk.CTkFrame):
    def __init__(self, spec, data:pd.DataFrame, master=None):
        super().__init__(master)
        self.master=master
        self.spec = spec
        self.data = data

        #Trouver n'importe quelle ligne du dataframe qui correspond à l'espèce afin d'avoir des informations supplémentaires sur celle-ci
        self.ex_line = self.data.loc[0, :]
        i = 0
        while(self.ex_line["especes"]!=self.spec and i<8131): #Tant que l'espèce ne correspond pas, continuer à chercher
            self.ex_line=self.data.loc[i, :]
            i+=1

        self.data = self.data.drop(columns=["latitude","longitude","groupe"]).copy()

        #Transformer la date en ne conservant que l'année pour chaque ligne
        for i, case in enumerate(self.data['date']):
            annee=case[0:4]
            self.data.loc[i, 'date'] = annee

        self.annee_min = int(self.data['date'].min())
        self.annee_max = int(self.data['date'].max())

        data_spec=self.data[self.data["especes"]==spec] #Masque pour filtrer selon l'espèce en argument
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

        self.create_graph()
        self.create_widgets()

    #Fonction qui crée et affiche le graphique dans la page
    def create_graph(self):
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
        plot.set_title(f"Nombre d'observations de {self.spec} selon le temps")
        plot.legend(loc="upper left")
        plot.grid()

        canvas = FigureCanvasTkAgg(self.frame, master=self)
        canvas.draw()

        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def create_widgets(self):

        self.info_label = ctk.CTkLabel(self)
        txt = ""
        txt += "Groupe : "+ str(self.ex_line["groupe"])+"\n"
        txt += "Nom latin : "+ str(self.ex_line["especes"])+ "\n"
        txt += "Espèce : "+ str(self.ex_line["nom_commun"])
        self.info_label.configure(text=txt, bg_color="white")
        self.info_label.place(x=0, y=20)