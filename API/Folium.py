from folium import *
import json
import requests
from shapely.geometry import *

orange = '#ff7800'
reverse_search = 'https://nominatim.openstreetmap.org/reverse?format=json&lat={}&lon={}'
geojson_search = 'https://nominatim.openstreetmap.org/search?q={}&polygon_geojson=1&format=json'
id_geo_search = 'http://polygons.openstreetmap.fr/get_geojson.py?id={}'

class TweetMap:
    def __init__(self, coordinates, zoom, admin_level, tiles = 'Stamen Toner'):
        self.admin_level = admin_level
        self.osmap = Map(location = coordinates, zoom_start = zoom, tiles = tiles)

    def addMarker(self, coordinates, color = 'red', text = 'You are here'):
        Marker(coordinates, popup = text, icon = Icon(color = color)).add_to(self.osmap)

    def addLayer(self, GeoJsonData):
        GeoJson(GeoJsonData).add_to(self.osmap)

    def get_city_center(self, coordinates):
        data = requests.get(reverse_search.format(coordinates[0], coordinates[1]))
        data_json = data.json()
        if 'error' in data_json.keys():
            return None
        return [float(data_json['lon']), float(data_json['lat'])]

    def get_osm_geometry(self, coordinates):
        data = requests.get(reverse_search.format(coordinates[0], coordinates[1]))
        data_json = data.json()

        address_elements = data_json['address'].keys()

        place = None

        if 'city' in address_elements:
            place = data_json['address']['city']

        elif 'town' in address_elements:
            place = data_json['address']['town']

        elif 'suburb' in address_elements:
            place = data_json['address']['suburb']

        elif 'village' in address_elements:
            place = data_json['address']['village']

        elif 'hamlet' in address_elements:
            place = data_json['address']['hamlet']

        if place is not None:
            country = data_json['address']['country']
            data = requests.get(geojson_search.format(place + '+' + country))
            print(geojson_search.format(place + '+' + country))
            print(data, '\n')
            try:
                data_json = data.json()[0]

                osm_id = data_json['osm_id']

                geojson = data_json['geojson']


                return self.get_osm_id_geometry(osm_id)
            # return geojson
            except:
                pass

        return None

    def get_osm_id_geometry(self, osm_id):
        data = requests.get(id_geo_search.format(osm_id))
        return data.json()

    def coor_in_polygon(self, coordinates, polygon):
        point = Point(coordinates)
        polygon = Polygon(polygon)
        return polygon.contains(point)

    def middle_point(self, coordinates):
        lattitude, longitude = 0, 0

        for values in coordinates:
            lattitude += float(values[0])
            longitude += float(values[1])

        lattitude = lattitude / len(coordinates)
        longitude = longitude / len(coordinates)

        return [lattitude, longitude]


    def json_data(self):
        cpt = 0
        with open('folium_data.json', 'r') as json_file:
            data = json.load(json_file)

        for coordinates in data[:200]:
            print('Data {}/{}'.format(cpt, len(data) - 1))

            coor = self.get_city_center(self.middle_point(coordinates['coordinates'][0]))

            if coor is not None:
                geojson = self.get_osm_geometry(coor)
                if geojson:
                    print('DONE')
                    self.addLayer(geojson)
                else:
                    self.addMarker(coor, 'red', 'Coordinates :' + str(coor))
            cpt += 1


    def export(self, name="index.html"):
        self.osmap.save(name)

osmap = TweetMap([45.91974, 6.15737], 2, 9, tiles ='Stamen Toner')

# with open('folium_data.json', 'r') as json_file:
#     data = json.load(json_file)
# for coordinates in data:
#     point = middle_point(coordinates['coordinates'][0])
#     Marker([point[1], point[0]], popup='<i>' + str(point) + '</i>').add_to(osmap)
#     Rectangle([coordinates['coordinates'][0][0][::-1], coordinates['coordinates'][0][2][::-1]], color = '#ff7800', fill = True, fill_color = '#ff7800', fill_opacity = 0.3).add_to(osmap)

osmap.json_data()
osmap.save("index.html")