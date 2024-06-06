import os
import re
import random
from math import *
# from kivy_garden.mapview.utils import clamp
import time


from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout


from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Line
from kivy.graphics.transformation import Matrix
from kivy.graphics.context_instructions import Translate, Scale
from kivy.garden.mapview import MapView, MapLayer


from kivy.uix.gridlayout import GridLayout 
from kivy.uix.popup import Popup 
from kivy.uix.label import Label 
from kivy.uix.checkbox import CheckBox
from kivy.config import Config 
from kivy.uix.boxlayout import BoxLayout

from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

import gpxpy
import gpxpy.gpx

from plyer import gps
from plyer import vibrator

import geopy.distance

import numpy as np

global gpx_points
gpx_points = [] #gpx_examples/DrunkenMoonLake.gpx


global platform_info
platform_info = ""

global gps_loc
gps_loc = None

global gps_functionality
gps_functionality = False

global vibration_distance
vibration_distance = 100

global vibrate_at_distance
vibrate_at_distance = False


global current_distance
current_distance = 0


class GPSMapView(MapView):
    def start_tracking(self):
        try:
            gps.configure(on_location=self.on_location_update)
            gps.start(minTime=1000, minDistance=0)
            
            global gps_functionality
            gps_functionality = True

            self.gps_marker = MapMarker(lat=0, lon=0)
            self.add_marker(gps_marker)


        except NotImplementedError:
            print("GPS support is not implemented on your platform.")
            gps_loc = None


    def stop_tracking(self):
        gps.stop()

    def on_location_update(self, **kwargs):
        lat = kwargs.get('lat')
        lon = kwargs.get('lon')

        global gps_loc
        gps_loc = [lat, lon]

        # # Center the map on the current location
        # self.center_on(lat, lon)
        # Add a marker at the current location
        self.gps_marker.lat = lat
        self.gps_marker.lon = lon

def get_distance_gps_and_trail():
    global gpx_points
    global gps_loc

    if gps_loc != None and len(gpx_points) > 0:
        distances = []
        for pt in gpx_points:
            distances.append(geopy.distance.geodesic(gps_loc, pt).m)
        return np.min(np.array(distances))
    else:
        return -1

def vibrate_device(*args):
    global vibrate_at_distance
    global vibration_distance
    global current_distance
    # Vibrate the device for one second
    distance = get_distance_gps_and_trail()
    current_distance = distance

    if distance > 0 and vibrate_at_distance:
        if distance <= vibration_distance:
            vibrator.vibrate(1)

 
class MapViewApp(App):
    mapview = None
 
    def __init__(self, **kwargs):
        super(MapViewApp, self).__init__(**kwargs)
        self.title = "Trailing Your Trail"
        Clock.schedule_once(self.post, 0)
        Clock.schedule_once(lambda a: setattr(self.mapview,'zoom',self.mapview.zoom+1), 1)

        vibration_interval = 10
        Clock.schedule_interval(vibrate_device, vibration_interval)

        self.gpx_path = None
 
    def build(self):
        layout = BoxLayout(orientation='vertical')
        return layout
 
    def post(self, *args):
        layout = FloatLayout()
        # 25.018925,121.537605
        self.mapview = GPSMapView(zoom=20, lat=25.018925, lon=121.537605)
        self.mapview.start_tracking()

        self.line = LineMapLayer(self.mapview)
        self.mapview.add_layer(self.line, mode="scatter")  # window scatter
        layout.add_widget(self.mapview)
        
        self.root.add_widget(layout)
        b = BoxLayout(orientation='horizontal',height='32dp',size_hint_y=None)
        b.add_widget(Button(text="Settings",on_press=self.settings_popup))
        self.root.add_widget(b)

        
    def settings_popup(self, instance):
        layout = GridLayout(cols = 1, padding = 10) 
    

        ## GPX loading
        popupLabel = Label(text = "GPX path:") 
        if self.gpx_path == None:
            self.textinput = TextInput(text='GPX path')
        else:
            self.textinput = TextInput(text=self.gpx_path)

        explorer_button = Button(text='Browse files') # Not available on windows
        explorer_button.bind(on_release=self.open_file_explorer)

        loadButton = Button(text = "Load GPX", size_hint_y=None, height=50)
        loadButton.bind(on_release=self.loadGPX)
        closeButton = Button(text = "Close", size_hint_y=None, height=50)

        horizontal_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)

        horizontal_layout.add_widget(popupLabel) 
        horizontal_layout.add_widget(self.textinput) 
        horizontal_layout.add_widget(explorer_button) 
        
        self.infoLabel = Label(text = "Loaded GPX: " + str(self.gpx_path), size_hint_y=None, height=50) 
        
        global gps_functionality
        if not gps_functionality :
            self.infoLabel.text +="\nGPS support is not implemented on your platform."

        ## Vibrations
        vibLabel = Label(text = "Vibration settings:", size_hint_y=None, height=50)
        horizontal_layout2 = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
        vib2Label = Label(text = "Vibrate at distance (m):", size_hint_y=None, height=50)
        
        global current_distance
        currDistLabel = Label(text = "Current distance from trail: " + str(current_distance), size_hint_y=None, height=50) 

        global vibrate_at_distance
        self.checkbox = CheckBox(active=vibrate_at_distance)
        self.checkbox.bind(active=self.on_checkbox_active)

        
        global vibration_distance
        self.textinput_m = TextInput(text=str(vibration_distance))
        self.textinput_m.bind(text=self.on_vib_text_change)


        horizontal_layout2.add_widget(self.checkbox)
        horizontal_layout2.add_widget(vib2Label)
        horizontal_layout2.add_widget(self.textinput_m)

        
        
        layout.add_widget(horizontal_layout)  
        layout.add_widget(loadButton)   
        layout.add_widget(self.infoLabel)   
        layout.add_widget(Widget())    
        layout.add_widget(vibLabel)   
        layout.add_widget(horizontal_layout2)  
        layout.add_widget(currDistLabel)  
        layout.add_widget(Widget())    
        layout.add_widget(closeButton)        

        # Instantiate the modal popup and display 
        self.popup = Popup(title ='Settings', 
                        content = layout)   
        self.popup.open()    

        # Attach close button press with popup.dismiss action 
        closeButton.bind(on_press = self.popup_dismiss)    

    def on_checkbox_active(self, checkbox, value):
        global vibrate_at_distance
        vibrate_at_distance = value

    def on_vib_text_change(self, instance, value):
        global vibration_distance

        numbers_in_text = [int(s) for s in re.findall(r"\d+", value)]
        if len(numbers_in_text)> 0:
            vibration_distance = numbers_in_text[0]
        else:
            vibration_distance = 100

        self.textinput_m.text = str(vibration_distance)


    def popup_dismiss(self, instance):
        self.popup.dismiss(instance)
        
        if len(gpx_points) > 0:
            pt = gpx_points[0]
            # print("here")
            # self.mapview.lat = pt[0]
            # self.mapview.lon = pt[1]
            # self.mapview.do_update(0)
            # self.line.reposition()
            # self.line.draw_line()

            self.mapview.center_on(pt[0], pt[1])
            # Clock.schedule_once(lambda a: [setattr(self.mapview,'zoom',self.mapview.zoom+500), print("here2")], 1)


    def open_file_explorer(self, instance):
        # This will open the file explorer and allow the user to pick a file
        file_path = filechooser.open_file(title="Pick a file..")
        if file_path:
            print(f'Selected file: {file_path[0]}')
            self.textinput.text = file_path[0]
            # You can now use the file_path for further processing
            
    def loadGPX(self, instance):
        global gps_functionality
        

        if os.path.isfile(self.textinput.text):
            gpx_file = open(self.textinput.text, 'r', encoding='utf-8', errors='ignore')
            gpx = gpxpy.parse(gpx_file)

            global gpx_points
            gpx_points = []

            for track in gpx.tracks:
                for segment in track.segments:
                    for point in segment.points:
                        print(f'Point at ({point.latitude},{point.longitude}) -> {point.elevation}')
                        gpx_points.append([point.latitude, point.longitude])

            for waypoint in gpx.waypoints:
                print(f'waypoint {waypoint.name} -> ({waypoint.latitude},{waypoint.longitude})')

            for route in gpx.routes:
                print('Route:')
                for point in route.points:
                    print(f'Point at ({point.latitude},{point.longitude}) -> {point.elevtion}')

            self.gpx_path = self.textinput.text
            self.infoLabel.text = "Loaded GPX: " + str(self.gpx_path)   
                     
            if not gps_functionality :
                self.infoLabel.text +="\nGPS support is not implemented on your platform."

        else:
            self.gpx_path = None
            self.infoLabel.text = "Loaded GPX: Requested file not found"

            if not gps_functionality :
                self.infoLabel.text +="\nGPS support is not implemented on your platform."
 
 
 
class LineMapLayer(MapLayer):
    def __init__(self, mapview, **kwargs):
        super(LineMapLayer, self).__init__(**kwargs)
        self.zoom = 0
        self.mapview = mapview
        
        geo_dover   = [51.126251, 1.327067]
        geo_calais  = [50.959086, 1.827652]
        
        self.draw_line()
    
    def reposition(self):
        mapview = self.mapview
        
        #: Must redraw when the zoom changes 
        #: as the scatter transform resets for the new tiles
        if (self.zoom != mapview.zoom):
            self.draw_line()
            
    def get_x(self, lon):
        """Get the x position on the map using this map source's projection
        (0, 0) is located at the top left.
        """
        # return clamp(lon, MIN_LONGITUDE, MAX_LONGITUDE)
        return lon
 

    def get_y(self, lat):
        """Get the y position on the map using this map source's projection
        (0, 0) is located at the top left.
        """
        # lat = clamp(-lat, MIN_LATITUDE, MAX_LATITUDE)
        lat = -lat
        lat = lat * pi / 180.
        return ((1.0 - log(tan(lat) + 1.0 / cos(lat)) / pi))
    
    def draw_line(self, *args):
        mapview = self.mapview
        self.zoom = mapview.zoom
       
        # When zooming we must undo the current scatter transform
        # or the animation distorts it
        scatter = mapview._scatter
        map_source = mapview.map_source
        sx,sy,ss = scatter.x, scatter.y, scatter.scale
        vx,vy,vs = mapview.viewport_pos[0], mapview.viewport_pos[1], mapview.scale
        
        # Account for map source tile size and mapview zoom
        ms = pow(2.0,mapview.zoom) * map_source.dp_tile_size

        global gpx_points
        
        #: Since lat is not a linear transform we must compute manually 
        line_points = []
        # for lat,lon in self.coordinates:
        for lat,lon in gpx_points:
            line_points.extend((self.get_x(lon),self.get_y(lat)))
            #line_points.extend(mapview.get_window_xy_from(lat,lon,mapview.zoom))
        
         
        with self.canvas:
            # Clear old line
            self.canvas.clear()

            if len(line_points) > 0:
            
                # Undo the scatter animation transform
                Scale(1/ss,1/ss,1)
                Translate(-sx,-sy)
                
                # Apply the get window xy from transforms
                Scale(vs,vs,1)
                Translate(-vx,-vy)
                
                # Apply the what we can factor out
                # of the mapsource long,lat to x,y conversion
                Scale(ms/360.0,ms/2.0,1)
                Translate(180,0)
                
                # Draw new
                Color(1, 0, 0, 1)
                Line(points=line_points, width=12/ms, joint="round",joint_precision=100)
                Line(points=line_points, width=1)#, joint="round",joint_precision=100)
        
            

MapViewApp().run()