from dbm import error

import matplotlib.pyplot as plt
from customtkinter import CTkFrame, CTkFont
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pandas.core.interchange.dataframe_protocol import DataFrame

from pseudo_carte import region_info

from fonction import getDistanceFromLatLonInKm
import pandas as pd
import customtkinter as ctk


# def graph_from_radius(master,data,center,radius):
#     x, y = center
#
#     wanted_data = pd.DataFrame()
#
#     for i in range(0, data.shape[0]):
#         element = data.iloc[i]
#         lon, lat = element["latitude"], element["longitude"]
#         if getDistanceFromLatLonInKm(x, y, lon, lat) <= radius:
#             wanted_data.append(element, ignore_index=True)
#
#     GraphEvolution(wanted_data,master)
#
#
# def graph_from_region(master,data,region_id):
#     wanted_data = pd.concat([pd.DataFrame(),data.iloc[[0]]],ignore_index=True)
#     region = region_info[region_id]
#
#     for i in range(0,data.shape[0]):
#         element = data.iloc[i]
#         if element["region"] == region:
#             # item = [sec for first,sec in element.items()]
#             # wanted_data = wanted_data.concat(element)
#             wanted_data = pd.concat([wanted_data, data.iloc[[i]]], ignore_index=True)
#
#     GraphEvolution(wanted_data,master)


class GraphEvolution(CTkFrame):
    def __init__(self, data: pd.DataFrame, center: tuple[float, float] = None, radius: float = None,
                 region_id: int = None, master=None):
        super().__init__(master)
        self.frame = (CTkFrame(master))
        self.frame.pack(fill="both", expand=1)

        wanted_data = pd.DataFrame(columns=data.columns)
        if (center and radius is not None) and region_id is None:
            x, y = center
            for i in range(0, data.shape[0]):
                element = data.iloc[i]
                lon, lat = element["latitude"], element["longitude"]
                if getDistanceFromLatLonInKm(x, y, lon, lat) <= radius:
                    if wanted_data.empty:
                        wanted_data = data.iloc[[i]]
                    else:
                        wanted_data = pd.concat([wanted_data, data.iloc[[i]]], ignore_index=True)
        elif region_id is not None and (center is None and radius is None):
            region = region_info[region_id]
            for i in range(0, data.shape[0]):
                element = data.iloc[i]
                if element["region"] == region:
                    if wanted_data.empty:
                        wanted_data = data.iloc[[i]]
                    else:
                        wanted_data = pd.concat([wanted_data, data.iloc[[i]]], ignore_index=True)
        else:
            raise ValueError("Nécésite un centre et un rayon ou un id de région")

        self.data = wanted_data
        self.create_graph()

    def create_graph(self):
        print("Graph created")
        plt.figure(figsize=(5, 4))

        data = {}
        for line in self.data['nom_commun']:
            if line not in data:
                data[line] = 1
            else:
                data[line] += 1
        if not data:
            text = ctk.CTkLabel(self.frame, text="Aucune donnée à afficher pour cette région",font=CTkFont(size=20))
            text.pack(expand=True)
            return


        #pie that shows the number of each species as number of occurences
        plt.pie(data.values(), labels=[value for value in data.keys()])
        plt.legend([f"{key} : {value}" for key, value in data.items()], bbox_to_anchor=(1.15, 1), loc='upper left')
        plt.title('Nombre d\'observation des espèces dans la région sélectionnée')

        self.canvas = FigureCanvasTkAgg(plt.gcf(), master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=1)
        pass


if __name__ == "__main__":
    from dataframe import create_dataframe

    app = ctk.CTk()
    app.geometry(f"{app.winfo_screenwidth()}x{app.winfo_screenheight()}+{0}+{0}")
    app.title("Application pêche invasive")
    datas = create_dataframe("BD_EAE_faunique_Quebec.csv")

    # from_region = GraphEvolution(datas, 1, app)

    # Test graph_from_radius
    # GraphEvolution(data=datas, center=(45.5, -73.5),radius=5, master=app)
    #
    # Test graph_from_region
    # GraphEvolution(data=datas, region_id=9, master=app)
    #
    app.mainloop()
