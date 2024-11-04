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
        self.create_widgets()

    def search(self, text):
        results=[]
        for line in self.data:
            if(line==text):
                results.append(line)
        self.display(results)

    def changed(self, event):
        text = event.get()
        self.search(text)

    def create_widgets(self):
        self.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.champ = ctk.CTkEntry(self, placeholder_text="Rechercher", textvariable=self.content)
        self.champ.grid(row=0, column=0, pady=(10,10))

    def display(self, results):
        for result in results:
            print(result)

   

    
