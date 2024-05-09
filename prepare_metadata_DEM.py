import click, glob, os, sys
import exiftool
import ypr2okp
import pandas as pd
from pyproj import Transformer
import numpy as np

@click.command()
@click.option('--path', default='./', help='Path to project folder')
@click.option('--dem_file', default='dem.tif', help='name of the reference dem (Geotiff file)')
@click.option('--img_files', default='*.JPG', help='name of the reference dem (Geotiff file)')
@click.option('--focal_length', default=0, type=float, help='Focal length in mm, if 0 (default) it tries to extract value from EXIF')
@click.option('--sensor_scale', default=5472/13.2, help='nb of pixel per mm of the sensor')
@click.option('--meta_csv', default='metadata_img.csv', help='Name of metadata csv table extracted from exif')
@click.option('--target_epsg', default=25833, help='EPSG code of the target coordinate (to match DEM)')
@click.option('--clip_buffer', default=70, help='buffer size for clipping the DEM around the drone position')
@click.option('--takeoff_alt', default=-100, help='Altitude of the take off location')
def gdal_clip_cmds(path, dem_file, img_files, focal_length, sensor_scale, meta_csv, target_epsg, clip_buffer, takeoff_alt):
    if not os.path.isdir(path):
        sys.exit('ERROR: Workign directory not existing')
    if os.path.isfile(path + meta_csv):
        df = pd.read_csv(path + meta_csv, index_col=0)
    elif not os.path.isfile(path + meta_csv):
        df = extract_metadata(path, img_files, meta_csv, sensor_scale, target_epsg, focal_length, takeoff_alt)
    else:
        sys.exit('ERROR: ', meta_csv, ' does not exist')
    
    print('-> Writing bash commands to clip rasters')
    with open(path + 'gdal_clip_dem.sh', 'w') as f:
        for i, row in df.iterrows():
            output_clip_file = path + 'dems/dem_clip_' + row.img_name.split('/')[-1].split('.')[0] + '.tif'
            cmd_clip = 'gdal_translate -projwin ' + str(np.round(row.X,2)-clip_buffer) + ' ' + str(np.round(row.Y,2)+clip_buffer)  + ' ' + str(np.round(row.X,2)+clip_buffer) + ' ' + str(np.round(row.Y,2)-clip_buffer) + ' -of GTiff ' + path + dem_file +' '+ output_clip_file
            f.writelines(cmd_clip+'\n')
    print('done')

def extract_metadata(path, img_files, meta_csv, sensor_scale, target_epsg, focal_length, takeoff_alt):
    print('-> Extracting metadata from images')
    df = pd.DataFrame()
    if not os.path.isfile(path+meta_csv):
        flist = glob.glob(path + 'img/' + img_files)
        flist.sort()
        
        for file in flist:
            # 1. open image
            with exiftool.ExifTool() as et:
                metadata = et.get_metadata(file)

            roll = float(metadata['XMP:GimbalRollDegree'])# + float(metadata['XMP:FlightRollDegree'])
            pitch = float(metadata['XMP:GimbalPitchDegree'])# + float(metadata['XMP:FlightPitchDegree'])
            yaw = float(metadata['XMP:GimbalYawDegree'])# + float(metadata['XMP:FlightYawDegree'])
            omega, phi, kappa = ypr2okp.ypr2opk(yaw, pitch, roll)
            
            if focal_length==0:
                FoC = float(metadata['EXIF:FocalLength'])
            else:
                FoC = focal_length
            
            def compute_absolute_altitude(gps_alt, rel_alt, toff_alt=-100):
                if toff_alt < 0:
                    return gps_alt
                else:
                
                    return toff_alt + rel_alt
                
            loc_dict = {
                'img_name': file,
                'timestamp': pd.to_datetime(metadata['EXIF:DateTimeOriginal'], format='%Y:%m:%d %H:%M:%S'),
                'northing': float(metadata['EXIF:GPSLatitude']),
                'easting' : float(metadata['EXIF:GPSLongitude']),
                'GPSelevation': float(metadata['EXIF:GPSAltitude']),
                'sensor_width': int(metadata['EXIF:ExifImageWidth']),
                'sensor_height': int(metadata['EXIF:ExifImageHeight']),
                'focal_length': FoC*sensor_scale,
                'relative_altitude': float(metadata['XMP:RelativeAltitude']),
                'elevation':compute_absolute_altitude(float(metadata['EXIF:GPSAltitude']),
                                                     float(metadata['XMP:RelativeAltitude']),
                                                     takeoff_alt),
                'gimbal_roll': float(metadata['XMP:GimbalRollDegree']),
                'gimbal_pitch': float(metadata['XMP:GimbalPitchDegree']),
                'gimbal_yaw': float(metadata['XMP:GimbalYawDegree']),
                'flight_yaw': float(metadata['XMP:FlightYawDegree']),
                'flight_roll': float(metadata['XMP:FlightRollDegree']),
                'flight_pitch': float(metadata['XMP:FlightPitchDegree']),
                'omega' : omega,
                'phi':phi,
                'kappa':kappa
                }
            df = df.append(loc_dict, ignore_index=True)

        transformer = Transformer.from_crs("epsg:4326", "epsg:"+str(target_epsg), always_xy=True)
        df['X'], df['Y'] = transformer.transform(df.easting, df.northing)
        df.to_csv(path + meta_csv)
    else:
        df = pd.read_csv(path + meta_csv, index_col=0)
    print('done')
    return df


if __name__ == '__main__':
    gdal_clip_cmds()