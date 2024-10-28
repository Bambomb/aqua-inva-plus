#Widget de recherche et ses fonctionnalités

import customtkinter as ctk

class SearchWidget(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.create_widgets()

    def changed(self, text):
        print("Changé")

    def create_widgets(self):
        self.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.champ = ctk.CTkEntry(self, placeholder_text="Rechercher")
        self.champ.grid(row=0, column=0, pady=(10,10))
        self.champ.bind('<<Modified>>', self.changed)



