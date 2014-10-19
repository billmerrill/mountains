import gdal

scalar = 2
dataset_file = "mto.tif"
# dataset_file = "mtr-sq.tif"
dst_filename = "scaled-image.tif"

src = gdal.Open ( dataset_file )
src_geoxform = src.GetGeoTransform()
src_datatype = src.GetRasterBand(1).DataType

dst_dim = [int(src.RasterXSize/scalar), int(src.RasterYSize/scalar)]
dst_pixel_spacing = [ src_geoxform[1] * scalar, src_geoxform[5]* scalar]

mem_driver = gdal.GetDriverByName( 'MEM' )
dst = mem_driver.Create('', dst_dim[0], dst_dim[1],
     1, src_datatype)

dst_geoxform = (src_geoxform[0], #ulx
                 dst_pixel_spacing[0],
                 src_geoxform[2],
                 src_geoxform[3], #uly
                 src_geoxform[4],
                 dst_pixel_spacing[1])
                 
dst.SetGeoTransform(dst_geoxform)
dst.SetProjection(src.GetProjection())
res = gdal.ReprojectImage(src , dst,
            src.GetProjection(), 
            dst.GetProjection(), 
            gdal.GRA_Bilinear)

gtiff_driver = gdal.GetDriverByName('GTiff')
output_file = gtiff_driver.CreateCopy(dst_filename, dst)
output_file.SetGeoTransform(dst_geoxform)
output_file.SetProjection(dst.GetProjection())

src = None
dst = None
output_file = None

# dst_ds = drv.Create( dst_filename, output_pixel_dim[0], output_pixel_dim[1],1,
#                      raster_band.DataType )
# wkt = output.GetProjection()
# if wkt != '':
#     dst_ds.SetProjection( wkt )
# dst_ds.SetGeoTransform( src_ds.GetGeoTransform() )
# 
# dstband = dst_ds.GetRasterBand(1)
# CopyBand( srcband, dstband )