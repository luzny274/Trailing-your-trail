from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.image import Image
from kivy.uix.scatter import Scatter
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Line
import gpxpy
import matplotlib.pyplot as plt
import os

class TrailingYourTrail(App):
    def build(self):
        self.title = 'Trailing Your Trail'
        layout = BoxLayout(orientation='vertical')

        # File chooser to select GPX files
        self.file_chooser = FileChooserIconView(on_selection=self.load_gpx_file)
        layout.add_widget(self.file_chooser)

        # Label to show loaded GPX file path
        self.file_label = Label(text='No file selected')
        layout.add_widget(self.file_label)

        # Button to start planning route
        plan_button = Button(text='Plan Route', on_press=self.plan_route)
        layout.add_widget(plan_button)

        # Layout to display the map
        self.map_layout = FloatLayout()
        layout.add_widget(self.map_layout)

        return layout

    def load_gpx_file(self, filechooser, selection):
        if selection:
            self.file_label.text = f'Selected: {selection[0]}'
            self.gpx_file_path = selection[0]

    def plan_route(self, instance):
        if not hasattr(self, 'gpx_file_path'):
            self.file_label.text = 'No file selected'
            return

        # Load and parse the GPX file
        with open(self.gpx_file_path, 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)
            self.points = [(point.latitude, point.longitude) for track in gpx.tracks for segment in track.segments for point in segment.points]

        # Plot the route using matplotlib and save as an image
        lats, lons = zip(*self.points)
        plt.figure(figsize=(8, 8))
        plt.plot(lons, lats, marker='o', color='blue')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.title('Route')
        plt.grid()
        plt.savefig('route.png')
        plt.close()

        # Display the route image in the Kivy app
        self.show_route_image('route.png')

    def show_route_image(self, image_path):
        self.map_layout.clear_widgets()
        scatter = Scatter()
        img = Image(source=image_path)
        scatter.add_widget(img)
        self.map_layout.add_widget(scatter)

if __name__ == '__main__':
    TrailingYourTrail().run()

