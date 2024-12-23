# main.py
import customtkinter as ctk
import tkinter as tk
import geocoder

from recherche import SearchWidget
from dataframe import create_dataframe
from pseudo_carte import PseudoCarte
from ajout_observation import addObsWidget
from evo_graph import GraphiqueEvolution

class MainApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()-75}+{-10}+{0}")
        self.configure(fg_color="white")
        self.data = create_dataframe("BD_EAE_faunique_Quebec.scsv")
        self.title("Aqua-Inva")
        self.carte = PseudoCarte(data=self.data, master=self)
        self.graph = None
        self.loc = geocoder.ip('me').latlng
        self.create_menu()
        self.show_accueil()
        self.rowconfigure(0, weight=1)


    def show_accueil(self):
        self.clear_main_frame()
        self.search_widget = SearchWidget(self.data, carte=self.carte, master=self)
        self.search_widget.grid(row=0, column=0, padx=10, sticky="nsew")
        self.carte.grid(row=0, column=1, padx=10, sticky="nsew")
        self.addObs = addObsWidget(master=self)
        self.addObs.place(x=1450, y=60, anchor='ne')

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=5)
        self.columnconfigure(2, weight=0)

        #Ajouter un waypoint à la position donnée par l'IP
        self.carte.set_waypoint(self.loc[1], self.loc[0])

    def show_graph(self):
        self.clear_main_frame()
        graph_func = self.carte.get_graph_function()
        if not graph_func:
            label = ctk.CTkLabel(self, text="Aucune donnée n'a été sélectionnée", font=ctk.CTkFont(size=20),text_color="black")
            label.grid(row=0, column=1, padx=10, sticky="nsew")
            self.columnconfigure(0, weight=1)
            self.columnconfigure(1, weight=1)
            self.columnconfigure(2, weight=1)
            return
        label = ctk.CTkLabel(self, text="Chargement...", font=ctk.CTkFont(size=20),text_color="black")
        label.place(x=self.winfo_width() / 2.5, y=self.winfo_height() / 3, anchor='center')
        self.update()
        graph = graph_func(master=self)
        graph.grid(row=0, column=0, padx=10, sticky="nsew")
        label.destroy()
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=0)
        # self.create_menu()

    def show_evo(self):
        #Code volé à Adam:
        self.clear_main_frame()
        spec = self.search_widget.spec
        if not spec:
            label = ctk.CTkLabel(self, text="Aucune espèce n'a été sélectionnée", font=ctk.CTkFont(size=20),text_color="black")
            label.grid(row=0, column=1, padx=10, sticky="nsew")
            self.columnconfigure(0, weight=1)
            self.columnconfigure(1, weight=1)
            self.columnconfigure(2, weight=1)
            return
        
        label = ctk.CTkLabel(self, text="Chargement...", font=ctk.CTkFont(size=20),text_color="black")
        label.place(x=self.winfo_width() / 2.5, y=self.winfo_height() / 3, anchor='center')
        self.update()

        graph = GraphiqueEvolution(spec, self.data, master=self)
        graph.grid(row=0, column=0, padx=10, sticky="nsew")
        label.destroy()
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=0)

    #Fonction pour changer le fichier de data
    def change_file(self):
        new_file = tk.filedialog.askopenfilename() #File-dialog
        #Essayer de créer le dataframe, si ça marche pas, alors le fichier est pas bon
        try: self.data = create_dataframe(new_file)
        except: 
            #Popup d'erreur
            self.addObs.popup("Erreur", "Le fichier n'est pas un fichier de données valide pour Aqua-Inva, ou contient des différences")
            return
        self.search_widget.reloadData() #Recharger le dataframe

    def create_menu(self):
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)
        menu_bar.add_command(label="Accueil", command=self.show_accueil)
        menu_bar.add_command(label="Proportions", command=self.show_graph)
        menu_bar.add_command(label="Évolutions", command=self.show_evo)
        menu_bar.add_command(label="Fichier", command=self.change_file)

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