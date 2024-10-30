#Fichier pour la pseudo carte

import customtkinter as ctk
import tkinter as tk
import fiona
import shapely
from shapely.geometry import shape,Polygon,MultiPolygon

color = ["blue","red","white","yellow","purple","orange","brown","pink","grey","black","white","white","green","white","white","white","white"]
class PseudoCarte(ctk.CTkFrame):
    def __init__(self,data, master=None):
        super().__init__(master)

        self.canvas = ctk.CTkCanvas(self)
        self.canvas.pack(expand=True, fill='both')

        #Load region from file
        file = fiona.open("quebec_region_SHP/regio_s.shp")

        # Iterate over the features (records) in the Shapefile
        polygons=[]
        min_x, min_y, max_x, max_y = float("inf"), float("inf"), float("-inf"), float("-inf")

        for feature in file:
            if feature == file[2]:
                pass
            else:
                pass
                # continue
            geom = shape(feature['geometry'])
            if isinstance(geom, Polygon):
                exterior_coords = list(geom.exterior.coords)
                polygons.append(exterior_coords)
            elif isinstance(geom, MultiPolygon):
                for poly in geom.geoms:
                    exterior_coords = list(poly.exterior.coords)
                    polygons.append(exterior_coords)

            max_x = -56.934926885456164
            min_x = -67.6669728073233
            max_y = 62.58246570128598
            min_y = 44.99135832579372
            # print(min_x, min_y, max_x, max_y)
                # Calculate scale factor and offsets to center the polygons
            scale_x = self.canvas.winfo_screenwidth() / (max_x - min_x)
            scale_y = self.canvas.winfo_screenheight() / (max_y - min_y)
            scale = min(scale_x, scale_y) * 0.9  # Slight padding

            offset_x = (self.canvas.winfo_screenwidth() - (max_x - min_x) * scale) / 2+500
            offset_y = (self.canvas.winfo_screenwidth() - (max_y - min_y) * scale) / 2-300

            # Draw polygons on the canvas
            for poly in polygons:
                points = []
                for x, y in poly:
                    # Scale and offset points
                    px = (x - min_x) * (scale-(scale/100*35)) + offset_x
                    py = (max_y-y) * scale + offset_y
                    points.append((px, py))
                polygon = Polygon(points)
                polygon = polygon.simplify(5)
                curent_color = color[int(feature['properties']['RES_CO_REG'])-1]
                print(curent_color, int(feature['properties']['RES_CO_REG'])-1)
                real_points = [coord for point in polygon.exterior.coords for coord in point]
                self.canvas.create_polygon(real_points, fill=curent_color, outline="black", width=2)
                # return

if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry(f"{app.winfo_screenwidth()}x{app.winfo_screenheight()}+{-10}+{0}")
    app.title("Application pêche invasive")
    carte = PseudoCarte(app)
    carte.pack(expand=True, fill='both')
    app.mainloop()