import math
import gdal
import osr
from haversine import haversine
# from pyproj import Proj, transform
import pyproj
form indcies import *


def reproject_dataset ( dataset, \
            epsg_from=4326, epsg_to=3857 ):
    """
    A sample function to reproject and resample a GDAL dataset from within 
    Python. The idea here is to reproject from one system to another, as well
    as to change the pixel size. The procedure is slightly long-winded, but
    goes like this:
    
    1. Set up the two Spatial Reference systems.
    2. Open the original dataset, and get the geotransform
    3. Calculate bounds of new geotransform by projecting the UL corners 
    4. Calculate the number of pixels with the new projection & spacing
    5. Create an in-memory raster dataset
    6. Perform the projection
    """
    # Define the UK googmerc, see <http://spatialreference.org/ref/epsg/27700/>
    googmerc = osr.SpatialReference ()
    googmerc.ImportFromEPSG ( epsg_to )
    wgs84 = osr.SpatialReference ()
    wgs84.ImportFromEPSG ( epsg_from )
    tx = osr.CoordinateTransformation ( wgs84, googmerc )
    # Up to here, all  the projection have been defined, as well as a 
    # transformation from the from to the  to :)
    # We now open the dataset
    g = gdal.Open ( dataset, gdal.GA_ReadOnly )
   
   
    src_datatype = g.GetRasterBand(1).DataType
 
    pixel_meters = get_pixel_meters(g)
    pixel_spacing = pixel_meters[0]
    
    
    # Get the Geotransform vector
    geo_t = g.GetGeoTransform ()
    print "\nstarting transform"
    print geo_t
    print
    x_size = g.RasterXSize # Raster xsize
    y_size = g.RasterYSize # Raster ysize
    # Work out the boundaries of the new dataset in the target projection
    (ulx, uly, ulz ) = tx.TransformPoint( geo_t[0], geo_t[3])
    (lrx, lry, lrz ) = tx.TransformPoint( geo_t[0] + geo_t[1]*x_size, \
                                          geo_t[3] + geo_t[5]*y_size )
        
    print "upper right"                                  
    print ulx, uly, ulz
    print "\nlower left"
    print lrx, lry, lrz
    print
    # See how using 27700 and WGS84 introduces a z-value!
    # Now, we create an in-memory raster
    mem_drv = gdal.GetDriverByName( 'MEM' )
    # The size of the raster is given the new projection and pixel spacing
    # Using the values we calculated above. Also, setting it to store one band
    # and to use Float32 data type.
    
    # dst = mem_driver.Create('', dst_dim[PX], dst_dim[PY], 1, src_datatype)
    
    print "%s %s %s" % (int((lrx - ulx)/pixel_spacing), int((uly - lry)/pixel_spacing), src_datatype )
    dest = mem_drv.Create('', int((lrx - ulx)/pixel_spacing), \
            int((uly - lry)/pixel_spacing), 1, src_datatype)
    # Calculate the new geotransform
    new_geo = ( ulx, pixel_spacing, geo_t[2], \
                uly, geo_t[4], -pixel_spacing )
    print "\nnew transform"
    print new_geo
    
    # Set the geotransform
    dest.SetGeoTransform( new_geo )
    dest.SetProjection ( googmerc.ExportToWkt() )
    # Perform the projection/resampling 
    res = gdal.ReprojectImage( g, dest, \
                wgs84.ExportToWkt(), googmerc.ExportToWkt(), \
                gdal.GRA_Bilinear )
    return dest

def reproject_and_scale_dataset ( dataset, \
            epsg_from=4326, epsg_to=3857 ):
    """
    A sample function to reproject and resample a GDAL dataset from within 
    Python. The idea here is to reproject from one system to another, as well
    as to change the pixel size. The procedure is slightly long-winded, but
    goes like this:
    
    1. Set up the two Spatial Reference systems.
    2. Open the original dataset, and get the geotransform
    3. Calculate bounds of new geotransform by projecting the UL corners 
    4. Calculate the number of pixels with the new projection & spacing
    5. Create an in-memory raster dataset
    6. Perform the projection
    """
    # Define the UK go

    resize_ratio = .5
    
    googmerc = osr.SpatialReference ()
    googmerc.ImportFromEPSG ( epsg_to )
    wgs84 = osr.SpatialReference ()
    # wgs84.ImportFromEPSG ( epsg_from )
    
    
    # Up to here, all  the projection have been defined, as well as a 
    # transformation from the from to the  to :)
    # We now open the dataset
    g = gdal.Open ( dataset, gdal.GA_ReadOnly )
   
    wgs84.ImportFromWkt(g.GetProjection())
    tx = osr.CoordinateTransformation ( wgs84, googmerc )
    
    src_datatype = g.GetRasterBand(1).DataType
 
    pixel_meters = get_pixel_meters(g)
    pixel_spacing = pixel_meters[0  ]
    
    
    # Get the Geotransform vector
    geo_t = g.GetGeoTransform ()
    print "\nstarting transform"
    print geo_t
    x_size = g.RasterXSize # Raster xsize
    y_size = g.RasterYSize # Raster ysize
    # Work out the boundaries of the new dataset in the target projection
    (ulx, uly, ulz ) = tx.TransformPoint( geo_t[0], geo_t[3])
    (lrx, lry, lrz ) = tx.TransformPoint( geo_t[0] + geo_t[1]*x_size, \
                                          geo_t[3] + geo_t[5]*y_size )
                                          
    print ulx, uly, ulz
    print lrx, lry, lrz
    # See how using 27700 and WGS84 introduces a z-value!
    # Now, we create an in-memory raster
    mem_drv = gdal.GetDriverByName( 'MEM' )
    # The size of the raster is given the new projection and pixel spacing
    # Using the values we calculated above. Also, setting it to store one band
    # and to use Float32 data type.
    
    # dst = mem_driver.Create('', dst_dim[PX], dst_dim[PY], 1, src_datatype)
    
    print "%s %s %s" % (int((lrx - ulx)/pixel_spacing), int((uly - lry)/pixel_spacing), src_datatype )
    dest_x = int((resize_ratio *(lrx - ulx)) / pixel_spacing)
    dest_y = int((resize_ratio *(uly-lry)/pixel_spacing))
    dest = mem_drv.Create('', dest_x, \
            dest_y, 1, src_datatype)
    # Calculate the new geotransform
    new_geo = ( ulx, pixel_spacing / resize_ratio, geo_t[2], \
                uly, geo_t[4], -pixel_spacing/resize_ratio )
    print "\nnew transform"
    print new_geo
    
    # Set the geotransform
    dest.SetGeoTransform( new_geo )
    dest.SetProjection ( googmerc.ExportToWkt() )
    # Perform the projection/resampling 
    res = gdal.ReprojectImage( g, dest, \
                wgs84.ExportToWkt(), googmerc.ExportToWkt(), \
                gdal.GRA_Bilinear )
    return dest

def get_reprojected_stuff( nwx, nwy, sex, sey):
    inProj = pyproj.Proj(init='epsg:4326')
    outProj = pyproj.Proj(init='epsg:3857')
    x1,y1 = -11705274.6374,4826473.6922
    newnwx, newnwy = pyproj.transform(inProj,outProj,nwx,nwy)
    newsex, newsey = pyproj.transform(inProj,outProj,sex,sey)
    return newnwx, newnwy, newsex, newsey
    
def reproject_then_scale_dataset ( dataset, \
            epsg_from=4326, epsg_to=3857 ):
    """
    A sample function to reproject and resample a GDAL dataset from within 
    Python. The idea here is to reproject from one system to another, as well
    as to change the pixel size. The procedure is slightly long-winded, but
    goes like this:
    
    1. Set up the two Spatial Reference systems.
    2. Open the original dataset, and get the geotransform
    3. Calculate bounds of new geotransform by projecting the UL corners 
    4. Calculate the number of pixels with the new projection & spacing
    5. Create an in-memory raster dataset
    6. Perform the projection
    """
    # Define the UK googmerc, see <http://spatialreference.org/ref/epsg/27700/>
    
    googmerc = osr.SpatialReference ()
    googmerc.ImportFromEPSG ( epsg_to )
    wgs84 = osr.SpatialReference ()
    wgs84.ImportFromEPSG ( epsg_from )
    tx = osr.CoordinateTransformation ( wgs84, googmerc )
    # Up to here, all  the projection have been defined, as well as a 
    # transformation from the from to the  to :)
    # We now open the dataset
    g = gdal.Open ( dataset, gdal.GA_ReadOnly )
   
   
    src_datatype = g.GetRasterBand(1).DataType
 
    pixel_meters = get_pixel_meters(g)
    pixel_spacing = pixel_meters[0]
    
    
    # Get the Geotransform vector
    geo_t = g.GetGeoTransform ()
    print "\nstarting transform"
    print geo_t
    print
    x_size = g.RasterXSize # Raster xsize
    y_size = g.RasterYSize # Raster ysize
    
    orig_bound = (geo_t[0], 
                   geo_t[3], 
                   geo_t[0] + (geo_t[1] * x_size), 
                   geo_t[3] + (geo_t[5] * x_size))
    
    # Work out the boundaries of the new dataset in the target projection
    (ulx, uly, ulz ) = tx.TransformPoint( geo_t[0], geo_t[3])
    (lrx, lry, lrz ) = tx.TransformPoint( geo_t[0] + geo_t[1]*x_size, \
                                          geo_t[3] + geo_t[5]*y_size )
    tx_bound = (ulx, uly, lrx, lry)
                                         
    print "\n#####"
    print "orig x  |  orig y"
    print "%s  |  %s" % ((geo_t[1] * x_size) , (geo_t[5] * y_size))
    print (geo_t[1] * x_size) / (geo_t[5] * y_size)
    orig_ratio = abs((geo_t[1] * x_size) / (geo_t[5] * y_size))
    
    print "\n  tx x  |    tx y"
    print "%s  |  %s" % ((ulx - lrx) , (uly-lry))
    print (ulx - lrx) / (uly-lry)
    tx_ratio =  abs((ulx - lrx) / (uly-lry))
    
    
    print orig_ratio, tx_ratio
    
    return                                     
                                          
    # See how using 27700 and WGS84 introduces a z-value!
    # Now, we create an in-memory raster
    mem_drv = gdal.GetDriverByName( 'MEM' )
    # The size of the raster is given the new projection and pixel spacing
    # Using the values we calculated above. Also, setting it to store one band
    # and to use Float32 data type.
    
    # dst = mem_driver.Create('', dst_dim[PX], dst_dim[PY], 1, src_datatype)
    
    print "%s %s %s" % (int((lrx - ulx)/pixel_spacing), int((uly - lry)/pixel_spacing), src_datatype )
    dest = mem_drv.Create('', int((lrx - ulx)/pixel_spacing), \
            int((uly - lry)/pixel_spacing), 1, src_datatype)
    # Calculate the new geotransform
    new_geo = ( ulx, pixel_spacing, geo_t[2], \
                uly, geo_t[4], -pixel_spacing )
    print "\nnew transform"
    print new_geo
    
    # Set the geotransform
    dest.SetGeoTransform( new_geo )
    dest.SetProjection ( googmerc.ExportToWkt() )
    # Perform the projection/resampling 
    res = gdal.ReprojectImage( g, dest, \
                wgs84.ExportToWkt(), googmerc.ExportToWkt(), \
                gdal.GRA_Bilinear )
                
    scaled_dest = mem_drv.Create('', )            
                
    return dest
   
   
    
def resize_and_scale_scratch(dataset_name):
    raster_max_output_edge = 50
    input_dataset = gdal.Open (dataset_name, gdal.GA_ReadOnly)
    
    input_x_size = input_dataset.RasterXSize
    input_y_size = input_dataset.RasterYSize
    input_datatype = input_dataset.GetRasterBand(1).DataType
    
    input_xform = input_dataset.GetGeoTransform()
    input_bounds = (input_xform[0], 
                   input_xform[3], 
                   input_xform[0] + (input_xform[1] * input_x_size), 
                   input_xform[3] + (input_xform[5] * input_y_size))

    # output_bounds = transform_projection(input_bounds) 
    goog_merc = osr.SpatialReference()
    goog_merc.ImportFromEPSG (3857)
    wgs84 = osr.SpatialReference()
    wgs84.ImportFromEPSG (4326)
    tx = osr.CoordinateTransformation ( wgs84, goog_merc )
    (ulx, uly, ulz ) = tx.TransformPoint(input_bounds[BULX], input_bounds[BULY])
    (lrx, lry, lrz ) = tx.TransformPoint(input_bounds[BLRX] input_bounds[BLRY])
    output_bounds = (ulx, uly, lrx, lry) 
    
    # input_x2y_ratio = abs((input_xform[1] * input_x_size) / (input_xform[5] * input_y_size))
    # output_x2y_ratio = abs((output_bounds[BULX] - output_bounds[BLRX]) / (output_bounds[BULY] - output_bounds[BLRY]))
    
    (output_x_size, output_y_size) = get_output_raster_size(raster_max_output_edge, output_bounds)
    
    output_pixel_spacing = ( ((output_bounds[BULX] - output_bounds[BLRX]) / 
                               output_x_size),
                             ((output_bounds[BULY] - output_bounds[BLRY]) / 
                               output_Y_size))
        
    output_xform = (output_bounds[BULX], 
                    output_pixel_spacing[PX]
                    input_xform[2],
                    output_bounds[BULY]
                    input_xform[4]
                    output_pixel_spacing[PY])

    mem_drv = gdal.GetDriverByName( 'MEM' )
    output_dataset = mem_drv.Create('', output_x_size, output_y_size, 
        1, input_datatype)
    output_dataset.SetGeoTransform(output_xform)
    output_dataset.SetProjection ( goog_merc.ExportToWkt() )

    res = gdal.ReprojectImage(input_dataset, output_dataset, 
                wgs84.ExportToWkt(), googmerc.ExportToWkt(), 
                gdal.GRA_Bilinear)

def get_output_raster_size(r_max, bounds):
    x_r, y_r = 0
    x_g = abs(output_bounds[BULX] - output_bounds[BLRX]) 
    y_g = abs(output_bounds[BULY] - output_bounds[BLRY])
    
    if x_g > y_g:
        x_r = r_amx
        y_r = x_r * (y_g / x_g)
    else:
        y_r = y_max
        x_r = y_r * (x_g / y_g)
        
    return (int(x_r), int(y_r))
   
    
def transform_projection(input_bounds):
    goog_merc = osr.SpatialReference ()
    goog_merc.ImportFromEPSG ( epsg_to )
    wgs84 = osr.SpatialReference ()
    wgs84.ImportFromEPSG ( epsg_from )
    tx = osr.CoordinateTransformation ( wgs84, goog_merc )
    (ulx, uly, ulz ) = tx.TransformPoint(input_bounds[BULX], input_bounds[BULY])
    (lrx, lry, lrz ) = tx.TransformPoint(input_bounds[BLRX] input_bounds[BLRY])
    
    return (ulx, uly, lrx, lry)   

    
    
def get_pixel_meters(dataset):
    ''' get the length in meters of each pixel, x and y '''
    geotransform = dataset.GetGeoTransform()
    x_size_deg = geotransform[1]
    y_size_deg = geotransform[5]
    x_size_m = haversine((0,0),(x_size_deg, 0)) * 1000
    y_size_m = haversine((0,0), (0, y_size_deg)) * 1000
    return (math.copysign(x_size_m, x_size_deg), math.copysign(y_size_m, y_size_deg))
    
def experiment():
    reprojected_dataset = reproject_then_scale_dataset ( "mtr-sq-4326.tif")
    # This is a GDAL object. We can read it
    reprojected_data = reprojected_dataset.ReadAsArray ()
    # Let's save it as a GeoTIFF.
    driver = gdal.GetDriverByName ( "GTiff" )
    dst_ds = driver.CreateCopy( "mtr-sq-3857.tif", reprojected_dataset, 0 )
    dst_ds = None # Flush the dataset to disk

experiment()