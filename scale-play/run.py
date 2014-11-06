import math
import gdal
import osr
from haversine import haversine


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
    
def get_pixel_meters(dataset):
    ''' get the length in meters of each pixel, x and y '''
    geotransform = dataset.GetGeoTransform()
    x_size_deg = geotransform[1]
    y_size_deg = geotransform[5]
    x_size_m = haversine((0,0),(x_size_deg, 0)) * 1000
    y_size_m = haversine((0,0), (0, y_size_deg)) * 1000
    return (math.copysign(x_size_m, x_size_deg), math.copysign(y_size_m, y_size_deg))
    
def experiment():
    reprojected_dataset = reproject_and_scale_dataset ( "mtr-sq-4326.tif")
    # This is a GDAL object. We can read it
    reprojected_data = reprojected_dataset.ReadAsArray ()
    # Let's save it as a GeoTIFF.
    driver = gdal.GetDriverByName ( "GTiff" )
    dst_ds = driver.CreateCopy( "mtr-sq-3857.tif", reprojected_dataset, 0 )
    dst_ds = None # Flush the dataset to disk

experiment()