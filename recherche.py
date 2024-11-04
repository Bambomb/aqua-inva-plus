#Widget de recherche et ses fonctionnalités

import customtkinter as ctk
import tkinter as tk

class SearchWidget(ctk.CTkFrame):
    def __init__(self, data, master=None):
        super().__init__(master)
        self.master = master
        self.content = tk.StringVar()
        self.content.trace("w", lambda name, index,mode, var=self.content: self.changed(var))
        self.data = data
        self.label_collection = []
        self.configure(height=self.master.winfo_screenheight()-200)
        self.create_widgets()

#faire que ça marche et enlever certaines colonnes pour la recherche
    def search(self, text):
        results=[]
        for column in self.data:
            print(self.data[column])
            for line in self.data[column]:
                print("line",line)
                if text.upper() in line.upper():results.append(line)
        self.display(results)

#Ajouter un délai??
    def changed(self, event):
        text = event.get()
        if text!="" and text!=" ": self.search(text)
        else:
            self.resultats.destroy()
            self.frame()

    def create_widgets(self):
        self.grid(row=0, column=0, padx=20, pady=20, sticky="n")
        self.pack_propagate(0)

        self.champ = ctk.CTkEntry(self, placeholder_text="Rechercher", textvariable=self.content)
        self.champ.pack()

        self.frame()

    def display(self, results):
        self.resultats.destroy()
        self.label_collection=[]
        self.frame()

        for i, result in enumerate(results):
            self.label_collection.append(ctk.CTkLabel(self.resultats, text=result, fg_color="white", width=197))
            self.label_collection[i].pack(expand=True,side=tk.TOP)

    def frame(self):
        self.resultats = ctk.CTkFrame(self, width=200, height=1000, border_width=2, border_color="black")
        self.resultats.pack_propagate(0)
        self.resultats.pack(expand=1,fill="both")

   

    
