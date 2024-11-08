#Groupe-Widget de recherche et ses fonctionnalités

import customtkinter as ctk
import tkinter as tk
class SearchWidget(ctk.CTkFrame):
    def __init__(self, data, master=None):
        super().__init__(master)
        self.master = master
        self.content = tk.StringVar()
        self.content.trace("w", lambda name, index,mode, var=self.content: self.changed(var))
        self.data = data
        self.datasearch = self.data.drop(columns=['latitude','longitude','groupe'])
        self.label_collection = []
        self.text = ""
        self.x = 0
        self.y = 0
        self.max = False
        self.nb_page = 1
        self.configure(height=self.master.winfo_screenheight()-200)
        self.create_widgets()

    #Fonction qui recherche dans le dataframe
    def search(self, text, side):
        results=[]

        if(side==0): #Si la recherche est lancée à partir d'un changement de texte, relancer la recherche à partir du début du dataframe
            self.x=0
            self.y=0
            self.nb_page = 1
            self.max = False

        if(side>=0): #Si la recherche se fait en avant
            i = 0
            for column in self.datasearch[self.x:]:
                j = 0
                for case in self.datasearch[column][self.y:]:
                    case = str(case)
                    j+=1
                    if text.upper() in case.upper():
                        results.append(case)
                        print("x,y : ", self.x, ", ", self.y)
                        if(len(results)>=20):
                            self.x+=i
                            self.y+=j
                            self.display(results)
                            return
                i+=1
                #self.y=0

            self.max = True      
            self.display(results)

    #Fonction event callback du widget entry qui réagit quand le texte change
    def changed(self, event):
        self.text = event.get()
        if self.text!="" and self.text!=" ": self.search(self.text, 0)
        else:
            self.resultats.destroy()
            self.frame()

    #Création des widgets
    def create_widgets(self):
        self.grid(row=0, column=0, padx=20, pady=20, sticky="n")
        self.pack_propagate(0)

        self.champ = ctk.CTkEntry(self, placeholder_text="Rechercher", textvariable=self.content)
        self.champ.pack()

        self.frame()

        self.pagemenu = ctk.CTkFrame(self)
        self.pagemenu.pack(side=tk.BOTTOM)

        self.buttonleft = ctk.CTkButton(self.pagemenu, text="|<-", command=self.gauche, width=30)
        self.buttonleft.grid(row=0, column=0, sticky="n", padx=20)

        self.buttonright = ctk.CTkButton(self.pagemenu, text="->", command=self.droite, width=30)
        self.buttonright.grid(row=0, column=2, sticky="n", padx=20)

        self.labelpage = ctk.CTkLabel(self.pagemenu, text = 1)
        self.labelpage.grid(row=0, column=1, sticky="n", padx=5)

    #Fonction d'affichage des résultats
    def display(self, results):
        self.resultats.destroy()
        self.labelpage.configure(text=self.nb_page)
        self.label_collection=[]
        self.frame()

        for i, result in enumerate(results):
            self.label_collection.append(ctk.CTkLabel(self.resultats, text=result, fg_color="white", width=197))
            self.label_collection[i].pack(expand=True,side=tk.TOP)

    #Fonction qui crée le frame des résultats
    def frame(self):
        self.resultats = ctk.CTkFrame(self, width=200, height=1000, border_width=2, border_color="black")
        self.resultats.pack_propagate(0)
        self.resultats.pack(expand=1,fill="both")

    #Fonction event callback du bouton gauche
    def gauche(self):
        if(self.nb_page>1):
            self.nb_page = 1
            self.max = False
            self.search(self.text, 0)

    #Fonction event callback du bouton droite
    def droite(self):
        if(self.max==False):
            self.nb_page +=1
            self.search(self.text, 1)