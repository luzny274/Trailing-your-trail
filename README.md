# Trailing Your Trail
application to provide vibration notification when deviating from target trail.
# How to run
The code is contained in main.py file.
## Running the code on pc
```bash
conda create -n kivy_env python=3.9 conda-forge::kivy conda-forge::kivy-garden conda-forge::plyer conda-forge::gpxpy numpy conda-forge::geopy
conda activate kivy_env
garden install mapview

python main.py
```

## Running the code on Android using Buildozer (Linux or WSL needed)
```bash
buildozer installation: https://buildozer.readthedocs.io/en/latest/installation.html
export PATH=$PATH:~/.local/bin/
buildozer init
buildozer android debug deploy run
```
