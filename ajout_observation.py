#Groupe-Widget d'ajout d'observation et ses fonctionnalités

import customtkinter as ctk
import tkinter as tk
from datetime import date

#Classe principale
class addObsWidget(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.configure(fg_color="transparent")
        self.create_widgets()


    def create_widgets(self):
        self.mainButton = ctk.CTkButton(self, text="Ajouter observation", command=self.clickedAdd, width=30)
        self.mainButton.pack()

    def clickedAdd(self):
        ajd = date.today()
        print(ajd)

