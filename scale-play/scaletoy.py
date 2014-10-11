import time 
import glob
import os
import gdal
import osr
import numpy as np

start_time_script = time.clock()

# path_ras='C:/rasters/'

# for rasterfile in glob.glob(os.path.join(path_ras,'*.tif')):
# rasterfile_name=str(rasterfile[rasterfile.find('IMG'):rasterfile.find('.tif')])

rasterfile_name = "mto.tif"


print 'Processing:'+ ' ' + str(rasterfile_name)

ds = gdal.Open(rasterfile_name,gdal.GA_ReadOnly)
ds_xform = ds.GetGeoTransform()

print ds_xform

ds_driver = gdal.GetDriverByName('Gtiff')
srs = osr.SpatialReference()
srs.ImportFromEPSG(26716)

ds_array = ds.ReadAsArray()

sz = ds_array.itemsize

print 'This is the size of the neighbourhood:' + ' ' + str(sz)

h,w = ds_array.shape

print 'This is the size of the Array:' + ' ' + str(h) + ' ' + str(w)

bh, bw = 2,2

shape = (h/bh, w/bw, bh, bw)

print 'This is the new shape of the Array:' + ' ' + str(shape)

strides = sz*np.array([w*bh,bw,w,1])

blocks = np.lib.stride_tricks.as_strided(ds_array,shape=shape,strides=strides)

resized_array = ds_driver.Create(rasterfile_name + '_resized_to_52m.tif',shape[1],shape[0],1,gdal.GDT_Float32)
resized_array.SetGeoTransform((ds_xform[0],ds_xform[1]*2,ds_xform[2],ds_xform[3],ds_xform[4],ds_xform[5]*2))
# resized_array.SetProjection(srs.ExportToWkt())
band = resized_array.GetRasterBand(1)

zero_array = np.zeros([shape[0],shape[1]],dtype=np.float32)

print 'I start calculations using neighbourhood'
start_time_blocks = time.clock()

for i in xrange(len(blocks)):
    for j in xrange(len(blocks[i])):

        zero_array[i][j] = np.mean(blocks[i][j])

print 'I finished calculations and I am going to write the new array'

band.WriteArray(zero_array)

end_time_blocks = time.clock() - start_time_blocks

print 'Image Processed for:' + ' ' + str(end_time_blocks) + 'seconds' + '\n'

end_time = time.clock() - start_time_script
print 'Program ran for: ' + str(end_time) + 'seconds'