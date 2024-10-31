# Fichier pour la pseudo carte

import customtkinter as ctk
import tkinter as tk
import fiona
import shapely
from shapely.geometry import shape, Polygon, MultiPolygon
from fonction import map_range

color = ["blue", "red", "indigo", "yellow", "purple", "orange", "brown", "pink", "teal", "plum", "coral", "orchid",
         "lime", "skyblue", "navy", "darkgreen", "yellowgreen"]

poly_id_to_reg = {0:11,1:2,2:10,3:17,4:14,5:7,6:15,7:16,8:8,9:6,10:5,11:13,12:1,13:12,14:4,15:3,16:9,17:9,18:9}

class PseudoCarte(ctk.CTkFrame):
    def __init__(self, data, master=None):
        super().__init__(master)

        self.canvas = ctk.CTkCanvas(self)
        self.canvas.pack(expand=True, fill='both')

        # Les polygones de la carte
        self.simplified_map = []
        self.real_polygons = []
        self.poly_color = []
        self.poly_id = []

        # Calcule les limites de la carte (pour le scaling)
        self.max_x = 0
        self.min_x = 0
        self.max_y = 0
        self.min_y = 0

        # Calcule scale et offset des polygones
        self.scale = 0
        self.min_scale = 0
        self.max_scale = 0
        self.offset_x = 0
        self.offset_y = 0

        with fiona.open("quebec_region_SHP/simplified_map.shp") as data:
            for feature in data:
                recent_poly = []

                geom = shape(feature['geometry'])
                if isinstance(geom, Polygon):
                    exterior_coords = list(geom.exterior.coords)
                    # self.polygons.append(exterior_coords)
                    recent_poly.append(exterior_coords)
                    self.poly_color.append(color[int(feature['properties']['RES_CO_REG']) - 1])
                elif isinstance(geom, MultiPolygon):
                    for poly in geom.geoms:
                        exterior_coords = list(poly.exterior.coords)
                        # self.polygons.append(exterior_coords)
                        recent_poly.append(exterior_coords)
                        self.poly_color.append(color[int(feature['properties']['RES_CO_REG']) - 1])

                # créer les polygones
                for poly in recent_poly:
                    self.real_polygons.append(Polygon(poly))

        self.save_simple_map()
        self.rezoom()
        self.draw()
        self.canvas.bind("<MouseWheel>", self.on_scroll)
        self.canvas.bind("<Motion>", self.moved)
        self.master.bind("<KeyPress>", self.key_pressed)

    def moved(self, event):
        #Pour afficher la carte en début
        print(self.winfo_screenwidth(),self.canvas.winfo_width(),self.master.winfo_width())
        self.rezoom()
        self.canvas.unbind("<Motion>")

    def key_pressed(self, event):
        if event.char == "c":
            self.rezoom()

    def rezoom(self,event=None):
        # Les limites de la carte (pour le scaling)
        self.max_x = -56.934926885456164
        self.min_x = -67.6669728073233
        self.max_y = 62.58246570128598
        self.min_y = 44.99135832579372
        # Calcule agrandissement et déplacement des polygones
        scale_x = self.canvas.winfo_width() / (self.max_x - self.min_x)
        scale_y = self.canvas.winfo_height() / (self.max_y - self.min_y)
        self.scale = min(scale_x, scale_y) * 0.8  #Marge de bordure
        self.min_scale = self.scale
        self.max_scale = 1120
        self.offset_x = (self.canvas.winfo_width() - (self.max_x - self.min_x) * self.scale) / 2 + (self.max_x - self.min_x) * self.scale/1.5
        self.offset_y = (self.canvas.winfo_height() - (self.max_y - self.min_y) * self.scale) / 2
        self.draw()

    def save_simple_map(self):
        self.simplified_map = []
        for i, poly in enumerate(self.real_polygons):
            self.simplified_map.append(poly.simplify(0.001))

    def on_scroll(self, event):
        scale_factor = 1.1 if event.delta > 0 else 0.9
        if not(self.min_scale <= self.scale*scale_factor <= self.max_scale):
            scale_factor = 1
        self.scale*= scale_factor
        self.offset_x = (self.offset_x - event.x) * scale_factor + event.x
        self.offset_y = (self.offset_y - event.y) * scale_factor + event.y
        self.draw()

    def move_poly(self,poly):
        points=[]
        for x, y in poly.exterior.coords:
            # Agrandir et placer les polygones
            px = (x - self.min_x) * (self.scale - (self.scale / 100 * 35)) + self.offset_x
            py = (self.max_y - y) * self.scale + self.offset_y
            points.append((px, py))
        return points

    def draw(self):
        self.canvas.delete("all")
        screen = shapely.geometry.box(0, 0, self.canvas.winfo_width(), self.canvas.winfo_height())
        for i, poly in enumerate(self.simplified_map):

            simplification = map_range(self.scale, self.min_scale, self.max_scale, 0.08, 0.002)
            points = self.move_poly(poly.simplify(simplification))
            if Polygon(points).intersection(screen).is_empty:
                continue
            polygon_id =self.canvas.create_polygon(points, fill=self.poly_color[i], outline="black", width=2)
            self.canvas.tag_bind(polygon_id, "<Button-1>", lambda event, i=i: self.on_polygon_click(event, i))

    def on_polygon_click(self, event, polygon_index):
        print(f"Polygon {polygon_index} clicked is region {poly_id_to_reg[polygon_index]}")
        show_popup(polygon_index)


def show_popup(poly_id):
    # Non permanent
    popup = tk.Toplevel()
    popup.title("Popup Window")
    popup.geometry(f"300x200+{popup.winfo_screenwidth()//2-150}+{popup.winfo_screenheight()//2-100}")

    label = tk.Label(popup, text=f"Tu a cliqué sur la région administrative {poly_id_to_reg[poly_id]}")
    label.pack(pady=20)

    close_button = tk.Button(popup, text="Close", command=popup.destroy)
    close_button.pack(pady=10)

if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry(f"{app.winfo_screenwidth()}x{app.winfo_screenheight()}+{0}+{0}")
    app.title("Application pêche invasive")
    carte = PseudoCarte(app)
    carte.pack(expand=True, fill='both')
    app.mainloop()

