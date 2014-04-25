import struct
import gdal
import gdalconst
import pprint
import math
import numpy
from haversine import haversine

PX = 0
PY = 1
PZ = 2

TA = 0
TB = 1
TC = 2

N = 0
T = 1

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
    Nraw = numpy.cross( numpy.subtract(triangle[TA], triangle[TB]),
                               numpy.subtract(triangle[TA], triangle[TC]) )
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
            triangle[TA][PX], triangle[TA][PY], triangle[TA][PZ],
            triangle['b'][PX], triangle['b'][PY], triangle['b'][PZ],
            triangle['c'][PX], triangle['c'][PY], triangle['c'][PZ]))

def get_pixel_meters(dataset):
    geotransform = dataset.GetGeoTransform()
    x_size_deg = geotransform[1]
    y_size_deg = geotransform[5]
    x_size_m = haversine((0,0),(x_size_deg, 0)) * 1000
    y_size_m = haversine((0,0), (0, y_size_deg)) * 1000
    return (math.copysign(x_size_m, x_size_deg), math.copysign(y_size_m, y_size_deg))


# heightmap is in meters, convert everything else to meters
def get_mesh(dataset):
    destination = "test-output-file.txt"
    band = dataset.GetRasterBand(1)


    pixel_size = get_pixel_meters(dataset)
    output_scalar = .1
    sample_scale = 5

    # multiple this vector again each point for the poly space
    pt_scalar = (sample_scale * pixel_size[PX] * output_scalar,
                 sample_scale * pixel_size[PY] * output_scalar,
                 output_scalar)

    emap = []
    mesh = []

    sample_height = dataset.RasterYSize / sample_scale
    sample_width = dataset.RasterXSize / sample_scale

    for i in range(0, sample_height):
        scanline = band.ReadRaster( 0, i*sample_scale, band.XSize, 1, \
            band.XSize, 1, gdal.GDT_Float32 )
        scanline = struct.unpack('f' * band.XSize, scanline)
        emap.append(scanline[::sample_scale])

    print "Sampled image is %s x %s pixels." % (len(emap), len(emap[0]))

    def make_pt(x,y):
        return (float(x) * pt_scalar[PX],
                float(y) * pt_scalar[PY],
                float(emap[y][x]) * pt_scalar[PZ])

    for sy in range(0, sample_height-1):
        for sx in range(0, sample_width-1):
            a_triangle = {TA:make_pt(sx,sy),
                        TB:make_pt(sx+1,sy+1),
                        TC:make_pt(sx+1,sy)}
            a_normal = compute_normal(a_triangle)
            b_triangle = {TA: make_pt(sx, sy),
                          TB: make_pt(sx, sy+1),
                          TC: make_pt(sx+1, sy+1)}
            b_normal = compute_normal(b_triangle)

            mesh.append((a_normal, a_triangle))
            mesh.append((b_normal, b_triangle))

    print "Generated %s triangles." % len(mesh)
    return mesh

def write_stl(outfile, mesh):
    with open(outfile, 'wb') as dest_file:
        dest_file.write(struct.pack("80sI", b'Quick Release Lever', len(mesh)))
        for f in mesh:
            data = [f[N][PX], f[N][PY], f[N][PZ],
                f[T][TA][PX], f[T][TA][PY], f[T][TA][PZ],
                f[T][TB][PX], f[T][TB][PY], f[T][TB][PZ],
                f[T][TC][PX], f[T][TC][PY], f[T][TC][PZ],0]
            dest_file.write(struct.pack("12fH", *data))



def main():
    dataset = gdal.Open('mto.tif', gdal.GA_ReadOnly)
    get_general_info(dataset)
    mesh = get_mesh(dataset)
    print "Writing STL"
    write_stl("output.stl", mesh)
# emap = get_map(dataset)

#    lets_map_a_point(map, dataset)
#    print len(emap)
#    for i in emap:
#	print i


main()
