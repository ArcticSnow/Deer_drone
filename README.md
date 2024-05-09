# README.md
Collection of tools to project drone images on DEMs (with no prior photogrammetric processing). This is written within the Master thesis of Julie Bommerlund at IBV UiO, trying to estimate deer population from drone imagery in mountainous and forested terrain.

The tool uses drone GPS location with camera properties to project roughly images on a DEM. Projection method is based on the internally written Python library [Projimdem](https://github.com/luc-girod/ProjectImageToDEM).

Author: S. Filhol.

## Usage

Organize your project as follow:
- myproject/
    - dems/
    - img/
    - proj_img/*.JPG
    - dem.tif

```
conda activate livox
# or a Python VE with pandas, numpy pyexiftool, pyproj, click, projimdem

# set the parameters in process_project.sh
nano process_project.sh

# execute script
bash process_project.sh
```

### DEM preparation

1. To download a DEM for Norway go to [Hoydedata.no](https://hoydedata.no/)
2. Interpolate DEM to higher resolution (here to 10cm) `gdal_translate -projwin xmin ymax xmax ymin -of GTiff -tr 0.1 0.1 input.tif OUTPUT.tif`

## Camera Specs
### DJI Mavic 2 Pro
- RGB camera
- Foc=10.3mm
- sensor size: 13.2*8.8mm, 5,472 × 3,648px

### DJI Mavic 2 Entreprise dual
- RGB camera:
    - 4056x3040 12.3 MPx
    - Focal length: 4.5 mm
    - sensor size: 7.18x4.55 mm
- [Thermal camera](https://coptrz.com/thermal-drone-comparison-the-mavic-2-enterprise-dual-vs-a-zenmuse-xt2-solution/):
    - 160x120 Px (real), 640x480 Px (interpolated)
    - Focal length: 0.458072 mm
    - sensor size: 1.92x1.44 mm
    - Field of view: 57 deg