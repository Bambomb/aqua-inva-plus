#Groupe-Widget de recherche et ses fonctionnalités

import customtkinter as ctk
import tkinter as tk
import numpy as np
import pandas as pd

#Classe principale 
class SearchWidget(ctk.CTkFrame):
    def __init__(self, data, master=None):
        super().__init__(master)
        self.master = master

        self.content = tk.StringVar()
        self.content.trace("w", lambda name, index,mode, var=self.content: self.changed(var))
        self.datasearch = data.drop(columns=['habitat','type_observation'], errors='ignore').to_numpy()
        indexlist = data[:].reset_index(drop=False)["index"].to_numpy().reshape(-1, 1)
        self.datasearch = np.concatenate((self.datasearch, indexlist), axis=1)
        self.label_collection = []
        self.text = ""
        self.spec = None
        self.x = 0
        self.y = 0
        self.max = False
        self.nb_page = 1
        self.filter_list = []
        self.data_index = 0
        self.checked = ctk.BooleanVar()
        self.configure(height=self.master.winfo_screenheight()-200,width=5, bg_color="white",fg_color="white")
        # self.configure(width=5)
        self.create_widgets()

    #Fonction qui recherche dans le dataframe
    def search(self, text, side):
        results=[]

        if self.text!="" and self.text!=" ": #S'assure qu'il y a une entrée dans le champ
            if(side==0): #Si la recherche est lancée à partir d'un changement de texte, relancer la recherche à partir du début du dataframe
                self.x=0
                self.y=0
                self.nb_page = 1
                self.max = False

            if(side>=0): #Si la recherche se fait en avant
                i = 0
                #self.y=0
                for line in self.datasearch[self.y:]: #Parcoure chaque ligne du dataframe
                    i+=1
                    j = 0
                    if(self.follows_filters(line)):
                        for case in line: #Parcoure chaque case de la ligne
                            case = str(case) #Transforme en string pour le upper()
                            j+=1
                            if text.upper() in case.upper(): #Si la recherche se trouve dans la case
                                results.append(line)
                                if(len(results)>=20): #Limite à 20 résultats
                                    self.x+=j
                                    self.y+=i
                                    self.display(results)
                                    return

                self.max = True     
                self.display(results)

    #Fonction event callback du widget entry qui réagit quand le texte change
    def changed(self, event):
        self.text = event.get()
        if (self.text!="" and self.text!=" ") or len(self.filter_list)>0: self.search(self.text, 0) #S'assure qu'il y a une entrée dans le champ
        else:
            self.labelpage.configure(text="-")
            self.max = True 
            self.resultats.destroy()
            self.frame()

    #Création des widgets
    def create_widgets(self):
        self.grid(row=0, column=0, padx=20, pady=5, sticky="n")
        self.pack_propagate(0)
        
        #Label recherche
        self.uplabel = ctk.CTkLabel(self, text = "Rechercher :                    ", bg_color="white",text_color="black")
        self.uplabel.pack(side=tk.TOP)

        #Entry du champ de recherche
        self.champ = ctk.CTkEntry(self, placeholder_text="Rechercher", textvariable=self.content, bg_color="white",text_color="black",fg_color="white")
        self.champ.pack()
        self.champ.bind("<Return>", command=self.enter) #Bind la commande entrée à l'entry pour que quand on appuie sur entrée ça appelle la fonction

        #Crée le frame de résultats
        self.frame()

        #Frame du menu pour changer de page
        self.pagemenu = ctk.CTkFrame(self, bg_color="white",fg_color="white")
        self.pagemenu.pack(side=tk.BOTTOM)

        #Bouton pour retourner au début
        self.buttonleft = ctk.CTkButton(self.pagemenu, text="|<-", command=self.gauche, width=30)
        self.buttonleft.grid(row=0, column=0, sticky="n", padx=20)

        #Bouton pour aller à la page suivante
        self.buttonright = ctk.CTkButton(self.pagemenu, text="->", command=self.droite, width=30)
        self.buttonright.grid(row=0, column=2, sticky="n", padx=20)

        #Label qui affiche le numéro de page
        self.labelpage = ctk.CTkLabel(self.pagemenu, text = 1, bg_color="white",fg_color="white",text_color="black")
        self.labelpage.grid(row=0, column=1, sticky="n", padx=5)

        #Label qui affiche infos supplémentaires
        self.displaylabel = ctk.CTkLabel(self.master, text=None, compound="left", justify="left", anchor="w",fg_color="white")
        self.displaylabel.configure(text="Date : AAAA-MM-JJ\nPlan d'eau :\nRégion : \nLatitude : Y, Longitude X\nNom latin :\nEspèce :", bg_color="white",text_color="black")
        self.displaylabel.grid(row=0, column=1, sticky="n", padx=5)

        #Frame qui contient les filtres
        self.filter_frame = ctk.CTkFrame(self, height=2)
        self.filter_frame.pack(side=tk.TOP)

        #Checkbox pour marquer ou démarquer une observation
        self.check = ctk.CTkCheckBox(self.displaylabel, text="Marqué", command=self.check_change_state, variable=self.checked)
        self.check.grid(row=2)
        self.check.configure(state=ctk.DISABLED)

    #Fonction event callback quand le checkmark est cliqué, alors l'état change
    def check_change_state(self):
        if(self.checked.get()==True): #Si le checkmark est désormais coché, il faut ajouter une marque à la ligne
            self.master.data.loc[self.data_index, "marque"]="Marque"

        elif(self.checked.get()==False): #Si le checkmark est désormais décoché, il faaut retirer la marque de la ligne
            self.master.data.loc[self.data_index, "marque"]="-"

        #Code volé de ajout_observation
        try: self.master.data.to_csv("BD_EAE_faunique_Quebec.scsv", index=False, sep=';',encoding='latin1') #Sauvegarde
        except Exception as e: #Si pandas ne peut pas sauvegarder le dataframe dans le csv, ça veut dire que le csv est ouvert ailleurs
            self.master.addObs.popup("Erreur", "Le fichier de données est ouvert ailleurs, veuillez le fermer")

        self.reloadData() #Recharger le dataframe
        self.search(self.content.get(),0) #Rafraîchir le displayresult


    #Fonction d'affichage des résultats
    def display(self, results):
        #Protection du checkbox
        self.check.configure(state=ctk.DISABLED)

        #Rafraîchissement
        self.master.carte.del_waypoint()
        self.resultats.destroy()
        if(self.max==False):
            self.labelpage.configure(text=self.nb_page)
            self.buttonright.configure(state=tk.ACTIVE)
        else: 
            self.labelpage.configure(text="Max")
            self.buttonright.configure(state=tk.DISABLED)

        self.label_collection=[]
        self.frame()

        #Crée un widget label pour chacun des résultats
        index = 0
        for i, result in enumerate(results):
            for j, case in enumerate(result):
                 if str(self.text).upper() in str(case).upper():
                     index = j
            reslab = ResultLabel(smalltext=result[index], bigtext = result, supermaster=self, master=self.resultats)
            self.label_collection.append(reslab)
            self.label_collection[i].pack(expand=True,side=tk.TOP)

    #Fonction qui crée le frame des résultats
    def frame(self):
        self.resultats = ctk.CTkFrame(self, width=280, height=1000, border_width=2, border_color="black", bg_color="white",fg_color="gray75")
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

    #Fonction qui rafraîchit le dataframe
    def reloadData(self):
        self.datasearch = self.master.data.drop(columns=['habitat','type_observation']).to_numpy()
        indexlist = self.master.data[:].reset_index(drop=False)["index"].to_numpy().reshape(-1, 1)
        self.datasearch = np.concatenate((self.datasearch, indexlist), axis=1)

    #Fonction qui affiche les informations détaillées du résultat cliqué dans le label
    def displayresult(self, line):
        self.data_index=line[9]
        tab = ""
        tab += "Date : "+ str(line[0])+ "\n"
        tab += "Plan d'eau : "+ str(line[1])+ "\n"
        tab += "Région : "+ str(line[2])+ "\n"
        tab += "Latitude : "+ str(line[3])+ ", Longitude : "+ str(line[4])+"\n"
        tab += "Groupe : "+ str(line[5])+"\n"
        tab += "Nom latin : "+ str(line[6])+ "\n"
        tab += "Espèce : "+ str(line[7])
        self.displaylabel.configure(text=tab,text_color="black")
        self.check.configure(state=ctk.NORMAL)
        if(str(line[8])=="Marque"):self.checked.set(True)
        else:self.checked.set(False)


    #Fonction event callback quand on appuie sur entrée pour ajouter un filtre
    def enter(self, event):
        if(self.content.get()=="" or self.content.get() == " "):return #Ne pas ajouter de filtre si le champ est vide
        else: 
            self.add_filter(self.content.get())
            self.content.set("")

    #Fonction qui ajoute un filtre
    def add_filter(self, text):
        self.filter_list.append(Filtre(text, id=len(self.filter_list),supermaster=self,master=self.filter_frame)) #Crée un filtre et l'ajoute dans la liste
        temp_widget = self.filter_list[-1]
        temp_widget.grid(row=0, column=len(self.filter_list)) #Affiche le label du filtre

    #Fonction pour enlever un filtre dans la liste
    def remove_filter(self, id):
        self.filter_list.pop(id)
        self.filter_reset_ids() #Met à jour l'attribut id des filtres selon leurs nouveaux index
        if(id==0):self.filter_frame.configure(height=2) #S'il n'y a plus de filtre, cacher le frame
        self.search(self.text, 0)

    #Met à jour l'attribut id des filtres selon leurs nouveaux index
    def filter_reset_ids(self):
        for id, filter in enumerate(self.filter_list):
            filter.set_id(id)

    #Fonction qui renvoie un bool pour vérifier si la ligne convient aux filtres entrés
    def follows_filters(self, line):
        for filter in self.filter_list: #Pour chaque filtre dans la liste
            filter_real = False 
            for case in line: #Pour chaque case dans la ligne
                if str(filter.text).upper() in str(case).upper(): filter_real = True #Est-ce que le filtre convient à la case
            if filter_real==False: return False #S'il est toujours faux après avoir été comparé à chaque case, alors le filtre ne convient pas à la ligne, donc faux
        return True

#Classe de un label résultat
class ResultLabel(ctk.CTkLabel):
    def __init__(self, smalltext, bigtext, supermaster, master=None):
        super().__init__(master)
        self.master = master
        self.supermaster = supermaster
        self.smalltext = smalltext
        self.bigtext = bigtext

        self.configure(text=smalltext, fg_color="white", width=197,text_color="black")
        i=0
        self.bind("<ButtonRelease-1>", command=lambda event:self.on_res_click(self.bigtext))

    def on_res_click(self, line):
        self.supermaster.displayresult(line)
        self.supermaster.spec=line[6]
        try:line4=float(line[4])
        except Exception as e:
            self.supermaster.master.carte.del_waypoint()
            return
        self.supermaster.master.carte.set_waypoint(line[4],line[3])

#Class du label de filtre
class Filtre(ctk.CTkFrame):
    def __init__(self, text, id, supermaster, master=None):
        super().__init__(master)
        self.master = master
        self.supermaster = supermaster
        self.text = text
        self.id = id
        self.configure(fg_color="#3b8ed0")

        self.create_widgets()

    #Création des widgets
    def create_widgets(self):
        label_text = ctk.CTkLabel(self, text=self.text, text_color="white")
        label_text.grid(row=0, column=0, padx=5)

        x_button = ctk.CTkLabel(self, text="x", text_color="white")
        x_button.bind("<ButtonRelease-1>", lambda event:self.remove_filter()) #Bind la fonction de suppression au bouton x
        x_button.grid(row=0, column=1, padx=5)

    #Pour se supprimer soi-même
    def remove_filter(self):
        self.supermaster.remove_filter(self.id) #Informe le supermaster que le filtre doit être supprimé de la liste
        self.destroy()

    def set_id(self,id):
        self.id=id

    
