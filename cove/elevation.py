import math
import struct
import gdal
import gdalconst
import pprint
from haversine import haversine
from indicies import *

class Elevation(object):

    def __init__(self, config):
        self.builder = config
        
    def load_dataset(self):
        self.dataset = gdal.Open(self.builder.get_src_file(), gdal.GA_ReadOnly)
        
    def get_pixel_meters(self):
        ''' get the length in meters of each pixel, x and y '''
        geotransform = self.dataset.GetGeoTransform()
        x_size_deg = geotransform[1]
        y_size_deg = geotransform[5]
        x_size_m = haversine((0,0),(x_size_deg, 0)) * 1000
        y_size_m = haversine((0,0), (0, y_size_deg)) * 1000
        return (math.copysign(x_size_m, x_size_deg), math.copysign(y_size_m, y_size_deg))

        
    def get_elevation_in_meters(self):
        sample_rate = self.builder.get_input_sample_rate()
        pixel_in_meters = self.get_pixel_meters()
        sample_ysize = self.dataset.RasterYSize / sample_rate 
        sample_xsize = self.dataset.RasterXSize / sample_rate
   
        elevation_matrix = []
        band = self.dataset.GetRasterBand(1)
        for i in range(0, sample_ysize):
            scanline = band.ReadRaster(0, i * sample_rate, band.XSize, 1,
                band.XSize, 1, gdal.GDT_Float32) 
            elevations = struct.unpack ('f' * band.XSize, scanline)
            points = []
            for j in range(0, sample_xsize):
                points.append( [sample_rate * pixel_in_meters[PX] * j,
                                        sample_rate * pixel_in_meters[PY] * i,
                                        elevations[j * sample_rate] ])
            elevation_matrix.append(points)    
            
        return elevation_matrix
    
    
    def display_summary(self):
        print 'Driver: ',self.dataset.GetDriver().ShortName,'/', \
             self.dataset.GetDriver().LongName
        print 'Size is ', self.dataset.RasterXSize,'x', self.dataset.RasterYSize, \
              'x',self.dataset.RasterCount
        print 'Projection is '
        pprint.pprint(self.dataset.GetProjection())

        if True:
            band =self.dataset.GetRasterBand(1)
            print 'Band Type=',gdal.GetDataTypeName(band.DataType)

            min = band.GetMinimum()
            max = band.GetMaximum()
            if min is None or max is None:
                (min,max) = band.ComputeRasterMinMax(1)
            print 'Min=%.3f, Max=%.3f' % (min,max)

            if band.GetOverviewCount() > 0:
                print 'Band has ', band.GetOverviewCount(), ' overviews.'
            else:
                print 'Band has no overviews'

            if not band.GetRasterColorTable() is None:
                print 'Band has a color table with ', \
                band.GetRasterColorTable().GetCount(), ' entries.'
            else:
                print 'Band has no color table'

        geotransform =self.dataset.GetGeoTransform()
        if not geotransform is None:
            print 'Origin = (',geotransform[0], ',',geotransform[3],')'
            print 'Pixel Size = (',geotransform[1], ',',geotransform[5],')'

      

        