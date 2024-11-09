# Fichier pour la pseudo carte

import customtkinter as ctk
import tkinter as tk
import fiona
import shapely
from shapely.geometry import shape, Polygon, MultiPolygon, Point
from fonction import map_range

color = ["blue", "red", "indigo", "yellow", "purple", "orange", "brown", "pink", "teal", "plum", "coral", "orchid",
         "lime", "skyblue", "navy", "darkgreen", "yellowgreen"]

poly_id_to_reg = {0: 11, 1: 2, 2: 10, 3: 17, 4: 14, 5: 7, 6: 15, 7: 16, 8: 8, 9: 6, 10: 5, 11: 13, 12: 1, 13: 12, 14: 4,
                  15: 3, 16: 9, 17: 9, 18: 9}

region_info = {
    1: "Bas-Saint-Laurent",
    2: "Saguenay-Lac-Saint-Jean",
    3: "Capitale-Nationale",
    4: "Mauricie",
    5: "Estrie",
    6: "Montréal",
    7: "Outaouais",
    8: "Abitibi-Témiscamingue",
    9: "Côte-Nord",
    10: "Nord-du-Québec",
    11: "Gaspésie-Îles-de-la-Madeleine",
    12: "Chaudière-Appalaches",
    13: "Laval",
    14: "Lanaudière",
    15: "Laurentides",
    16: "Montérégie",
    17: "Centre-du-Québec"
}


class PseudoCarte(ctk.CTkFrame):
    """
    Affiche une carte de la région de Québec Autocentrée et redimensionnable
    La carte apparait au premier mouvement de la souris
    Appeler *rezoom()* peu aider à afficher la carte en début
    *save_simple_map()* comme qualité maximal de la carte
    """

    def __init__(self, data, master=None):
        super().__init__(master)

        self.canvas = ctk.CTkCanvas(self)
        self.canvas.pack(expand=True, fill='both')

        # Les polygones de la carte
        self.real_polygons = []
        self.poly_color = []
        self.poly_region = []
        self.simplified_map = []
        self.poly_id = []

        # waypoint
        grandeur = 30
        circle = Point(0, -grandeur * 2.5).buffer(grandeur)
        triangle = Polygon([(-grandeur / 2, -grandeur * 2), (grandeur / 2, -grandeur * 2), (0, 0)])
        self.waypoint = circle.union(triangle)
        self.waypoint_color = "red"
        self.waypoint_pos = None

        # Les limites de la carte (pour le scaling)
        self.max_x = -56.934926885456164
        self.min_x = -79.76532426607646
        self.max_y = 62.58246570128598
        self.min_y = 44.99135832579372

        # Calcule scale et offset des polygones
        self.scale = 0
        self.min_scale = 0
        self.max_scale = 0
        self.offset_x = 0
        self.offset_y = 0
        self.move_center = ()
        self.old_pos = (0, 0)

        with fiona.open("quebec_region_SHP/simplified_map.shp") as data:
            for feature in data:
                recent_poly = []

                geom = shape(feature['geometry'])
                if isinstance(geom, Polygon):
                    exterior_coords = list(geom.exterior.coords)
                    recent_poly.append(exterior_coords)
                    self.poly_color.append(color[int(feature['properties']['RES_CO_REG']) - 1])
                    self.poly_region.append(feature['properties']['RES_CO_REG'])
                elif isinstance(geom, MultiPolygon):
                    for poly in geom.geoms:
                        exterior_coords = list(poly.exterior.coords)
                        recent_poly.append(exterior_coords)
                        self.poly_color.append(color[int(feature['properties']['RES_CO_REG']) - 1])
                        self.poly_region.append(feature['properties']['RES_CO_REG'])

                # créer les polygones
                for poly in recent_poly:
                    self.real_polygons.append(Polygon(poly))

        self.save_simple_map()
        self.rezoom()
        self.draw()
        self.master.bind("<KeyPress>", self.key_pressed)
        self.canvas.bind("<MouseWheel>", self.on_scroll)
        self.canvas.bind("<Motion>", self.moved)
        self.canvas.bind("<B1-Motion>", self.begin_drag)
        self.canvas.bind("<ButtonRelease-1>", self.end_drag)

    def begin_drag(self, event):
        self.canvas.unbind("<B1-Motion>")
        self.canvas.bind("<B1-Motion>", self.drag)
        self.move_center = (event.x, event.y)
        self.old_pos = (self.offset_x, self.offset_y)

    def drag(self, event):
        x, y = self.old_pos
        self.offset_x = x + (event.x - self.move_center[0])
        self.offset_y = y + (event.y - self.move_center[1])
        self.draw(simply=map_range(self.scale, self.min_scale, self.max_scale, 0.1, 0.01))

    def end_drag(self, event):
        self.canvas.unbind("<B1-Motion>")
        self.canvas.bind("<B1-Motion>", self.begin_drag)
        self.move_center = ()
        self.draw()

    def moved(self, event):
        # Pour afficher la carte en début si elle est pas déjà là
        self.rezoom()
        self.canvas.unbind("<Motion>")

    def key_pressed(self, event):
        if event.char == "c":
            self.rezoom()

    def rezoom(self):
        """Rezoom la carte pour qu'elle soit centrée et remplisse l'écran"""
        # Calcule agrandissement et déplacement des polygones
        scale_x = self.canvas.winfo_width() / (self.max_x - self.min_x)
        scale_y = self.canvas.winfo_height() / (self.max_y - self.min_y)
        self.scale = min(scale_x, scale_y) * 0.8  # Marge de bordure
        self.min_scale = self.scale
        self.max_scale = 1120
        self.offset_x = (self.canvas.winfo_width() / 2) - (self.max_x - self.min_x) * (
                    self.scale - (self.scale / 100 * 35)) / 2
        self.offset_y = (self.canvas.winfo_height() / 2) - (self.max_y - self.min_y) * self.scale / 2
        self.draw()

    def save_simple_map(self):
        """Sauvegarde une version simplifiée de la carte"""
        self.simplified_map = []
        for i, poly in enumerate(self.real_polygons):
            self.simplified_map.append(poly.simplify(0.001))

    def on_scroll(self, event):
        scale_factor = 1.1 if event.delta > 0 else 0.9
        if not (self.min_scale <= self.scale * scale_factor <= self.max_scale):
            scale_factor = 1
        self.scale *= scale_factor
        self.offset_x = (self.offset_x - event.x) * scale_factor + event.x
        self.offset_y = (self.offset_y - event.y) * scale_factor + event.y
        self.draw()

    def move_poly(self, poly):
        points = []
        for x, y in poly.exterior.coords:
            # Agrandir et placer les polygones
            px = (x - self.min_x) * (self.scale - (self.scale / 100 * 35)) + self.offset_x
            py = (self.max_y - y) * self.scale + self.offset_y
            points.append((px, py))
        return points

    def draw(self, clickable=True, simply=None):
        """Afficher la carte"""
        self.canvas.delete("all")
        screen = shapely.geometry.box(0, 0, self.canvas.winfo_width(), self.canvas.winfo_height())
        for i, poly in enumerate(self.simplified_map):

            simplification = map_range(self.scale, self.min_scale, self.max_scale, 0.08,
                                       0.002) if simply is None else simply
            points = self.move_poly(poly.simplify(simplification))
            if Polygon(points).intersection(screen).is_empty:
                continue
            polygon_id = self.canvas.create_polygon(points, fill=self.poly_color[i], outline="black", width=2)
            self.canvas.tag_bind(polygon_id, "<ButtonRelease-1>",
                                 lambda event, num=i: self.on_polygon_click(event, num))

        if self.waypoint_pos:
            points = []
            x, y = self.waypoint_pos
            x = (x - self.min_x) * (self.scale - (self.scale / 100 * 35)) + self.offset_x
            y = (self.max_y - y) * self.scale + self.offset_y
            for point in self.waypoint.exterior.coords:
                px, py = point
                px += x
                py += y
                points.append((px, py))

            self.canvas.create_polygon(points, fill=self.waypoint_color, outline="white", width=5)
            self.canvas.create_polygon(points, fill=self.waypoint_color, outline="black", width=2)

    def on_polygon_click(self, event, polygon_index):
        if not self.move_center:
            print(f"Polygon {polygon_index} clicked is region {poly_id_to_reg[polygon_index]}")
            show_popup(polygon_index)

    def set_waypoint(self, lat, lon):
        self.waypoint_pos = (lon, lat)
        self.draw()

    def del_waypoint(self):
        self.waypoint_pos = None
        self.draw()

def show_popup(poly_id):
    # Non permanent
    popup = tk.Toplevel()
    popup.title("Popup Window")
    popup.geometry(f"300x200+{popup.winfo_screenwidth() // 2 - 150}+{popup.winfo_screenheight() // 2 - 100}")

    label = tk.Label(popup,
                     text=f"Tu a cliqué sur la région administrative {poly_id_to_reg[poly_id]} \n Nom: {region_info[poly_id_to_reg[poly_id]]}")
    label.pack(pady=20)

    close_button = tk.Button(popup, text="Close", command=popup.destroy)
    close_button.pack(pady=10)


if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry(f"{app.winfo_screenwidth()}x{app.winfo_screenheight()}+{0}+{0}")
    app.title("Application pêche invasive")
    carte = PseudoCarte(app)
    carte.pack(expand=True, fill='both')
    carte.set_waypoint(45.439334, -73.806329)
    app.mainloop()
