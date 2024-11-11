# main.py
import inspect

import customtkinter as ctk
import tkinter as tk

from PIL.ImageOps import expand

from recherche import SearchWidget
from dataframe import create_dataframe
from pseudo_carte import PseudoCarte

class MainApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.data = create_dataframe("BD_EAE_faunique_Quebec.csv")
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()-75}+{-10}+{0}")
        self.title("Aqua-Inva")
        self.carte = PseudoCarte(data=self.data, master=self)
        self.graph = None
        self.create_menu()
        self.show_accueil()
        self.rowconfigure(0, weight=1)

    def show_accueil(self):
        self.clear_main_frame()
        search_widget = SearchWidget(self.data, master=self)
        search_widget.grid(row=0, column=0, padx=10, sticky="nsew")
        self.carte.grid(row=0, column=1, padx=10, sticky="nsew")

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=5)
        self.columnconfigure(2, weight=0)

    def show_graph(self):
        self.clear_main_frame()
        graph_func = self.carte.get_graph_function()
        if not graph_func:
            label = ctk.CTkLabel(self, text="Aucune donnée n'a été sélectionnée", font=ctk.CTkFont(size=20))
            label.grid(row=0, column=1, padx=10, sticky="nsew")
            self.columnconfigure(0, weight=1)
            self.columnconfigure(1, weight=1)
            self.columnconfigure(2, weight=1)
            return
        graph = graph_func(master=self)
        graph.grid(row=0, column=0, padx=10, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=0)
        # self.create_menu()

    def create_menu(self):
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)
        menu_bar.add_command(label="Accueil", command=self.show_accueil)
        menu_bar.add_command(label="Graph", command=self.show_graph)

    def clear_main_frame(self):
        for widget in self.winfo_children():
            if  isinstance(widget, PseudoCarte):
                widget.grid_remove()
            else:
                widget.destroy()
        self.create_menu()


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()