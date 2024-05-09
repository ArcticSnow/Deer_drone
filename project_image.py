'''
Script to project image on DEM
S. Filhol
'''

import glob
import exiftool
from pyproj import Transformer
import geopandas as gpd
import pandas as pd
import ypr2okp
import numpy as np
from projimdem import projection as pr
import click, os

# ignore pandas warnings
import warnings
warnings.filterwarnings("ignore")

@click.command()
@click.option('--path', default='./', help='Path to project folder')
@click.option('--meta_csv', default='metadata_img.csv', help='Name of metadata csv table extracted from exif')
@click.option('--viewshed_file', default='None', help='Path to project folder')
@click.option('--target_epsg', default=25833, help='EPSG code of the target coordinate (to match DEM)')
@click.option('--yaw-correction', default=0.0, help='Correction angle for yaw in degrees')
def project_img(path, meta_csv, viewshed_file, target_epsg, yaw_correction):
    print('==== PROJECTING IMAGES TO DEM =====')
    flist = glob.glob(path + 'dems/.tif')
    flist.sort()
    
    if os.path.isfile(path + meta_csv):
        df = pd.read_csv(path + meta_csv, index_col=0)
    else:
        print('ERROR: No metadata_csv file')
        exit()
    if viewshed_file != 'None':
        viewshed_file = path+viewshed_file
    else:
        viewshed_file = None
    
    for i, row in df.iterrows():
        print('---> Projecting image ', i, ' out of ', df.shape[0])

        dem_local = path + 'dems/dem_clip_' + row.img_name.split('/')[-1].split('.')[0] + '.tif'
        #viewshed_file = None #path_to_dems + 'viewshed_' + row.img_name.split('/')[-1].split('.')[0] + '.tif'
        image_file = row.img_name
        output_file = path + 'proj_img/' + 'proj_img_' + row.img_name.split('/')[-1].split('.')[0] + '.tif'

        #print(row.omega, row.phi, row.kappa)
        #rot_matrix = rot_matrix_from_angles((90-row.omega)*np.pi/180,row.phi*np.pi/180,row.kappa*np.pi/180)
        rot_matrix = rot_matrix_from_angles((90+row.gimbal_pitch)*np.pi/180, row.gimbal_roll*np.pi/180,(row.gimbal_yaw + yaw_correction)*np.pi/180)

        cam_param = [[row.X, row.Y, row.elevation], 
                     rot_matrix, 
                     row.focal_length, 
                     [0,0],
                     [0,0,0,0,0,0,0,0,0,0,0,0]
                    ]

        laerdal_proj = pr.Projection(dem_file=dem_local,
                                     viewshed_file=viewshed_file,
                                     image_file=image_file,
                                     cam_param=cam_param,
                                     output_file=output_file)
        laerdal_proj.project_img_to_DEM(return_raster=True, epsg=target_epsg)
        laerdal_proj = None
    print('\n===> done')
        
def rot_matrix_from_angles(omega, phi, kappa):
        '''
        Rotation matrix from angles following Micmac convention
        '''
        RX = np.array([[1,0,0],
                 [0, np.cos(omega), -np.sin(omega)],
                 [0, np.sin(omega), np.cos(omega)]])    
        RY = np.array([[np.cos(phi), 0, np.sin(phi)],
                 [0,1,0],    
                 [-np.sin(phi), 0, np.cos(phi)]])
        RZ = np.array([[np.cos(kappa),-np.sin(kappa),0],
                 [np.sin(kappa), np.cos(kappa),0],
                 [0,0,1]])
        M = RX.dot(RY.dot(RZ))#.dot(np.array([[1,0,0],[0,-1,0],[0,0,-1]]))
        return M
    
if __name__ == '__main__':
    project_img()