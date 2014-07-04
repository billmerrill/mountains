import math
import struct
import gdal
import gdalconst
from haversine import haversine
from indicies import *
from mesh import Mesh

def get_pixel_meters(dataset):
    ''' get the length in meters of each pixel, x and y '''
    geotransform = dataset.GetGeoTransform()
    x_size_deg = geotransform[1]
    y_size_deg = geotransform[5]
    x_size_m = haversine((0,0),(x_size_deg, 0)) * 1000
    y_size_m = haversine((0,0), (0, y_size_deg)) * 1000
    return (math.copysign(x_size_m, x_size_deg), math.copysign(y_size_m, y_size_deg))


# for i in range(0, sample_height):
#     scanline = band.ReadRaster( 0, i*sample_scale, band.XSize, 1, \
#         band.XSize, 1, gdal.GDT_Float32 )
#     scanline = struct.unpack('f' * band.XSize, scanline)
#     emap.append(scanline[::sample_scale])


def make_point(x,y,z):
    ''' maybe we'll do something more interesting here '''
    return [x,y,z]
    
def sample_mesh_in_meters(build_config, dataset):
    ''' generates a mesh with points scaled to meters of lat, lon, and elevation
        based on the elevation unit in the input, meters to start '''
    sample_rate = build_config['sample_rate']
    band = dataset.GetRasterBand(1)

    sample_ysize = dataset.RasterYSize / sample_rate 
    sample_xsize = dataset.RasterXSize / sample_rate
    
    pixel_meters = get_pixel_meters(dataset)
    
    elevation_mesh = Mesh(sample_xsize, sample_ysize)
    
    for i in range(0, sample_ysize):
        scanline = band.ReadRaster(0, i * sample_rate, band.XSize, 1,
            band.XSize, 1, gdal.GDT_Float32) 
        elevations = struct.unpack ('f' * band.XSize, scanline)
        points = []
        for j in range(0, sample_xsize):
            points.append( make_point(sample_rate * pixel_meters[PX] * j,
                                    sample_rate * pixel_meters[PY] * i,
                                    elevations[j] ))
        elevation_mesh.add_row(points)
        
    return elevation_mesh
    
    
def scale_mesh_to_output(build_config, in_mesh):
    x_data_max = in_mesh.get_data_x_size()
    y_data_max = in_mesh.get_data_y_size()
    
    output_x = build_config.get('x_output_max', None)
    
    output_ratio = output_x / x_data_max
    
    scaled_mesh = Mesh()
    scaled_mesh.copy(in_mesh, 
                     scalar=[output_ratio, output_ratio, output_ratio], 
                     translate=[0,0,0])
   
    return scaled_mesh
    
