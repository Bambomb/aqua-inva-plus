#Le fichier main

import customtkinter as ctk
import tkinter as tk
from dataframe import create_dataframe

class MainApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.data = create_dataframe("BD_EAE_faunique_Quebec.csv")
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+{-10}+{0}")
        self.title("Application pêche invasive")

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()