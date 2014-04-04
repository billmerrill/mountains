import struct
import gdal
import gdalconst
import pprint
import math
import numpy

PX = 0
PY = 1
PZ = 2

def get_general_info(dataset):
    print 'Driver: ', dataset.GetDriver().ShortName,'/', \
          dataset.GetDriver().LongName
    print 'Size is ',dataset.RasterXSize,'x',dataset.RasterYSize, \
          'x',dataset.RasterCount
    print 'Projection is '
    pprint.pprint(dataset.GetProjection())

    geotransform = dataset.GetGeoTransform()
    if not geotransform is None:
        print 'Origin = (',geotransform[0], ',',geotransform[3],')'
        print 'Pixel Size = (',geotransform[1], ',',geotransform[5],')'


def get_map(dataset):
        band = dataset.GetRasterBand(1)
        avgs = []
        emap = []
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

        for i in range(0,719):
            scanline = band.ReadRaster( 0, i, band.XSize, 1, \
                band.XSize, 1, gdal.GDT_Float32 )

            # tuple_of_floats = struct.unpack('f' * band.XSize, scanline)
            emap.append(struct.unpack('f' * band.XSize, scanline))
            # avgs.append( math.fsum(tuple_of_floats) / len(tuple_of_floats))

        return emap


def compute_normal(triangle):
    Nraw = numpy.cross( numpy.subtract(triangle['a'], triangle['b']),
                               numpy.subtract(triangle['a'], triangle['c']) )
    hypo = math.sqrt(Nraw[PX]**2 + Nraw[PY]**2 + Nraw[PZ]**2)
    N = (Nraw[PX] / hypo,
         Nraw[PY] / hypo,
         Nraw[PZ] / hypo)
    return N

def hyp(v):
    return v[0]**2 + v[1]**2 + v[2]**2;


def write_triangle(sx,sy,triangle, normal):
    if not numpy.allclose([1.0], [hyp(normal)]):
        exit()

    print("%s,%s\nN(%s, %s, %s) %s\na(%s, %s, %s), b(%s, %s, %s), c(%s, %s, %s)\n\n" % (
            sx,sy,
            normal[0], normal[1], normal[2], hyp(normal),
            triangle['a'][PX], triangle['a'][PY], triangle['a'][PZ],
            triangle['b'][PX], triangle['b'][PY], triangle['b'][PZ],
            triangle['c'][PX], triangle['c'][PY], triangle['c'][PZ]))

def s2n(dataset):
    destination = "test-output-file.txt"
    band = dataset.GetRasterBand(1)
    emap = []

    for i in range(0, dataset.RasterYSize):
        scanline = band.ReadRaster( 0, i, band.XSize, 1, \
            band.XSize, 1, gdal.GDT_Float32 )
        emap.append(struct.unpack('f' * band.XSize, scanline))

    print len(emap)
    print len(emap[0])
    print emap[10][20]

    def make_pt(x,y):
        return (float(x),float(y),float(emap[y][x]))

    with open(destination, 'w') as dest_file:
        for sy in range(0, dataset.RasterYSize-1):
            for sx in range(0, dataset.RasterXSize-1):
                triangle = {'a':make_pt(sx,sy),
                            'b':make_pt(sx+1,sy+1),
                            'c':make_pt(sx+1,sy)}
                normal = compute_normal(triangle)

                write_triangle(sx,sy,triangle, normal)

                # t = triangle
                # print "V(%s,%s,%s) W(%s,%s,%s)" %  (t['b'][PX] - t['a'][PX], t['b'][PY] - t['a'][PY], t['b'][PZ] - t['a'][PZ],
                #         t['c'][PX] - t['a'][PX], t['c'][PY] - t['a'][PY], t['c'][PZ] - t['a'][PZ])
                #
                # va = numpy.subtract(triangle['b'], triangle['a']);
                # wa = numpy.subtract(triangle['c'], triangle['a']);
                # print "V(%s,%s,%s) W(%s,%s,%s)" % ( va[0], va[1], va[2], wa[0], wa[1], wa[2] )
                # print "\n\n"




import pprint
def main():
    dataset = gdal.Open('mto.tif', gdal.GA_ReadOnly)
    s2n(dataset)
# get_general_info(dataset)
# emap = get_map(dataset)

#    lets_map_a_point(map, dataset)
#    print len(emap)
#    for i in emap:
#	print i


main()
