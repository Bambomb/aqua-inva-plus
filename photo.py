#Widget de photos

import requests
import customtkinter as ctk
import tkinter as tk
import pyWikiCommons as wiki

from PIL import Image, ImageTk
from io import BytesIO

class Photo(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master=master
        self.configure(width=10, height=10, bg_color="#d0e4f5")

        #Widget label qui contiendra la photo
        self.photo = ctk.CTkLabel(self, text="", image=None, height=1, width=1, bg_color="#d0e4f5")
        self.photo.pack()

        #Pour ne pas oublier l'image
        self.image = None

    #Définit la photo qui à afficher
    def set_photo(self, speclat:str, specfr:str, size):

        #Afficher un texte de chargement
        self.photo.configure(text="Chargement...", image=ctk.CTkImage(light_image=Image.open("blanc.png"), size=(1,1)))

        #Les deux urls permmetant la recherche
        srch_urls = [
        f"https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=pageimages&generator=search&gsrsearch={speclat}&gsrlimit=1&pithumbsize=500",
        f"https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=pageimages&generator=search&gsrsearch={specfr}&gsrlimit=1&pithumbsize=500"
        ]

        #Pour chacun des deux urls
        for url in srch_urls:
            
            #Requête de l'url pour la recherche
            response = requests.get(url) #La requête
            data=response.json() #Charger en json

            #Aller chercher les pages des résultats de recherche
            pages = data.get('query', {}).get('pages', {})

            #Si la requête de la recherche a échoué, vider le label
            if(not pages or len(pages)<1):self.photo.configure(text="", image=ctk.CTkImage(light_image=Image.open("blanc.png"), size=(1,1)))
            else: #Sinon, si elle a fonctionné

                #Pour chaque page trouvée
                for id, page in pages.items():
                    
                    #Vérifier si la page correspond bien à l'espèce
                    if('thumbnail' in page and (speclat.split(" ")[0] in page['title'] or speclat.split(" ")[1] in page['title'])):
                        img_url = page['thumbnail']['source'] #Aller chercher l'url de l'image dans le résultat de la recherche
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'} #Headers pour que Wikimedia ne me bloque pas parce que sinon il pense que je suis un intrus for some reason
                        response = requests.get(img_url, headers=headers) #Faire une requête de l'url

                        #Si la requête de l'image a fonctionné
                        if response.status_code == 200:
                            
                            img_data = Image.open(BytesIO(response.content)) #Ouverture de l'url de l'image
                            
                            image = ctk.CTkImage(img_data, size=(img_data.width//(1/size), img_data.height//(1/size))) #Création de l'image
                            self.image=image #Pour ne pas oublier l'image
                            self.photo.configure(image=image, text="") #Plaçage de l'image dans le label
                            return

                        #Si la requête de l'image a échoué, indiquer l'échec
                        else:self.photo.configure(text="Échec de requête : Réponse échouée", image=ctk.CTkImage(light_image=Image.open("blanc.png"), size=(1,1)))

                    #Si la page ne correspond pas à l'espèce, vider le label
                    else:self.photo.configure(text="", image=ctk.CTkImage(light_image=Image.open("blanc.png"), size=(1,1)))

    #Va get le secret à partir du fichier
    def secret(self):
        with open('secret.txt', 'r', encoding="utf-8") as p:
            return p.read()
        


