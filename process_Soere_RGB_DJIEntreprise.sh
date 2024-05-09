#===================================
# Bash script to project DJI drone images onto DEM
# S. Filhol, Oct 2021

# ======= Input parameters =======

working_path=/media/arcticsnow/LaCie/Students/Julie_deer/data/Soere_Bjoerkum/process/20210408_Soere_Bjoerkum_RGB_60m_#2_crash/
dem_file=Soere_dem_clip_10cm.tif
takeoff_altitude=130
# ======= Drone Specific parameters =======

## --- DJI Mavic 2 Entreprise Dual RGB (12MPx) ---
## Focal length in mm
#FoC=4.5
FoC=5.5
## in Px/mm
FoC_scaling=564.9025
## buffer around image position in meters
clip_buffer=70
#yaw_corr=-18
yaw_corr=30

# --- DJI Mavic Dual Thermal (640*480 Px interpolated, real 160*120 Px) ---
# Focal length in mm
#FoC=1
# in Px/mm
#FoC_scaling=666.666
# buffer around image position in meters
#clip_buffer=50
#yaw_corr=-18

## --- DJI 2 Mavic Pro RGB(20MPx) ---
## Focal length in mm
#FoC=10.3
## in Px/mm
#FoC_scaling=414.5454  
## buffer around image position in meters
#clip_buffer=70
#yaw_corr=0




# ====== Script ==========

# extract meta and prepare dem for each image
python prepare_metadata_DEM.py --path $working_path --dem_file $dem_file --focal_length $FoC --sensor_scale $FoC_scaling --clip_buffer $clip_buffer --takeoff_alt $takeoff_altitude

# clip DEM around image center with gdal
bash $working_path"gdal_clip_dem.sh"

# Compute ortho photo (projection)
python project_image.py --path $working_path --yaw-correction $yaw_corr

# Remove clipped DEMs
#rm -r $working_path"dems/dem_clip*.tif"
