#Le fichier main

import customtkinter as ctk
import tkinter as tk
from recherche import SearchWidget
from dataframe import create_dataframe
from pseudo_carte import PseudoCarte

class MainApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.data = create_dataframe("BD_EAE_faunique_Quebec.csv")
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+{-10}+{0}")
        self.title("Application pêche invasive")
        self.carte = PseudoCarte(data=self.data, master=self)
        self.carte.grid()
        self.searchWidget = SearchWidget(self.data, master=self)
        self.searchWidget.grid()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()