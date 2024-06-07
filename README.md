# Trailing Your Trail
## Project Overview

The objective of this project is to develop a mobile
application for both Android and iOS platforms, utilizing Python.
The app is designed to import hiking and biking trail routes in the
form of GPX files. It features an intuitive alert system that notifies
users through vibration feedback when they stray from their
designated route. This innovative functionality ensures that users
can remain focused on their outdoor activities without the
necessity of frequent visual checks on their device. 

## How to run
The code is contained in main.py file.
### Running the code on PC
```bash
conda create -n kivy_env python=3.9 conda-forge::kivy conda-forge::kivy-garden conda-forge::plyer conda-forge::gpxpy numpy conda-forge::geopy
conda activate kivy_env
garden install mapview

python main.py
```

### Running the code on Android using Buildozer (Linux or WSL needed)
```bash
buildozer installation: https://buildozer.readthedocs.io/en/latest/installation.html
export PATH=$PATH:~/.local/bin/
buildozer init
buildozer android debug deploy run
```
