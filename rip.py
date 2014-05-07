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

    if True:
        band = dataset.GetRasterBand(1)
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

    geotransform = dataset.GetGeoTransform()
    if not geotransform is None:
        print 'Origin = (',geotransform[0], ',',geotransform[3],')'
        print 'Pixel Size = (',geotransform[1], ',',geotransform[5],')'


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
    band = dataset.GetRasterBand(1)


    pixel_size = get_pixel_meters(dataset)
    output_scalar = .0035
    sample_scale = 10
    thick = 1



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

    def make_pt(x,y,z=None):
        if z is None:
            z = float(emap[y][x]) * pt_scalar[PZ]
        else:
            z = z * pt_scalar[PX]

        return (float(x) * pt_scalar[PX],
                float(y) * pt_scalar[PY],
                z)

    def get_closest_vertice(x,y):
        pt = ( int(x / pt_scalar[PX]),
               int(y / pt_scalar[PY]))
        return pt

    def make_square(square):
        a_triangle = {TA: square[0],
                     TB: square[1],
                     TC: square[2]}
        a_normal = compute_normal(a_triangle) # 0,-1,0 ?

        b_triangle = { TA: square[2],
                      TB: square[3],
                      TC: square[0]}
        b_normal = compute_normal(b_triangle)

        # pprint.pprint(a_normal)
        # pprint.pprint(b_normal)

        return [(a_normal, a_triangle), (b_normal, b_triangle)]


    print "Scaled space option max is:"
    pprint.pprint(make_pt(sample_width-1, sample_height-1, 0))

    # generate a mountain mesh
    if False:
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


    # generate a base box, bottom is at height 0 XXX TODO THESE NEED TO BE SCALED

    if True:
        for sy in range(0, sample_height-1):
            # -x side
            a_triangle = {TA: make_pt(0, sy),
                          TB: make_pt(0, sy, 0),
                          TC: make_pt(0, sy+1, 0)}
            a_normal = compute_normal(a_triangle) # -1,0,0 ?
            b_triangle = {TA: make_pt(0, sy+1),
                          TB: make_pt(0, sy),
                          TC: make_pt(0, sy+1, 0)}
            b_normal = compute_normal(b_triangle)

            mesh.append((a_normal, a_triangle))
            mesh.append((b_normal, b_triangle))

            if True:
                # +x side
                a_triangle = {TA: make_pt(sample_width-1, sy),
                              TB: make_pt(sample_width-1, sy+1, 0),
                              TC: make_pt(sample_width-1, sy, 0)}
                a_normal = compute_normal(a_triangle) # 1,0,0 ?
                b_triangle = {TA: make_pt(sample_width-1, sy+1),
                              TB: make_pt(sample_width-1, sy+1, 0),
                              TC: make_pt(sample_width-1, sy)}
                b_normal = compute_normal(b_triangle)

                mesh.append((a_normal, a_triangle))
                mesh.append((b_normal, b_triangle))
    if True:
        for sx in range(0, sample_width-1):
            # +y side
            a_triangle = {TA: make_pt(sx, 0),
                          TB: make_pt(sx+1, 0, 0),
                          TC: make_pt(sx, 0, 0)}
            a_normal = compute_normal(a_triangle) # 0,1,0 ?
            b_triangle = {TA: make_pt(sx+1, 0),
                          TB: make_pt(sx+1, 0, 0),
                          TC: make_pt(sx, 0)}
            b_normal = compute_normal(b_triangle)

            mesh.append((a_normal, a_triangle))
            mesh.append((b_normal, b_triangle))

            if True:
                # -y side
                a_triangle = {TA: make_pt(sx, sample_height-1),
                              TB: make_pt(sx, sample_height-1, 0),
                              TC: make_pt(sx+1, sample_height-1, 0)}
                a_normal = compute_normal(a_triangle) # 0,-1,0 ?
                b_triangle = {TA: make_pt(sx+1, sample_height-1),
                              TB: make_pt(sx, sample_height-1),
                              TC: make_pt(sx+1, sample_height-1, 0)}
                b_normal = compute_normal(b_triangle)

                mesh.append((a_normal, a_triangle))
                mesh.append((b_normal, b_triangle))


    # solid base

    if False:
        yhalf = sample_height / 2
        xhalf = sample_width / 2
        yquarter = sample_height / 4
        xquarter = sample_width / 4

        negx = make_pt(xquarter, yhalf, 0)
        posx = make_pt(xquarter + xhalf, yhalf, 0)
        negy = make_pt(xhalf, yquarter, 0)
        posy = make_pt(xhalf, yquarter + yhalf, 0)

        # star inset base
        for sy in range(0, sample_height-1):
            a_triangle = { TA: make_pt(0, sy, 0),
                           TB: negx,
                           TC: make_pt(0, sy+1, 0)}
            z_triangle = { TA: make_pt(sample_width-1, sy, 0),
                          TB: make_pt(sample_width-1, sy+1, 0),
                          TC: posx }

            mesh.append((compute_normal(a_triangle), a_triangle))
            mesh.append((compute_normal(z_triangle), z_triangle))

        for sx in range(0, sample_width-1):
            a_triangle = { TA: make_pt(sx, 0, 0),
                           TB: make_pt(sx+1, 0, 0),
                           TC: negy }
            z_triangle = { TA: make_pt(sx, sample_height-1, 0),
                           TB: posy,
                           TC: make_pt(sx+1, sample_height-1, 0) }

            mesh.append((compute_normal(a_triangle), a_triangle))
            mesh.append((compute_normal(z_triangle), z_triangle))


        a_triangle = { TA: make_pt(0,0,0),
                       TB: negy,
                       TC: negx }
        b_triangle = { TA: negy,
                       TB: make_pt(sample_width-1, 0, 0),
                       TC: posx }
        c_triangle = { TA: posx,
                       TB: make_pt(sample_width-1, sample_height-1, 0),
                       TC: posy }
        d_triangle = { TA: negx,
                       TB: posy,
                       TC: make_pt(0, sample_height-1, 0) }

        e_triangle = { TA: negy,
                       TB: posx,
                       TC: negx }

        f_triangle = { TA: posx,
                       TB: posy,
                       TC: negx }

        mesh.append((compute_normal(a_triangle), a_triangle))
        mesh.append((compute_normal(b_triangle), b_triangle))
        mesh.append((compute_normal(c_triangle), c_triangle))
        mesh.append((compute_normal(d_triangle), d_triangle))
        mesh.append((compute_normal(e_triangle), e_triangle))
        mesh.append((compute_normal(f_triangle), f_triangle))

    # hollow base

    def tr_pt(point, vector):
        return (point[PX] + vector[PX], point[PY] + vector[PY], point[PZ] + vector[PZ])


    print "margin in indexes:"
    in_margin = (int(thick / (pt_scalar[PX])) + 1,
                 int(thick / (math.fabs(pt_scalar[PY]))) + 1)
    pprint.pprint(in_margin)

    if True:
        # x side edges
        for sy in range(in_margin[PY], sample_height-1-in_margin[PY]):
            a_triangle = {TA: make_pt(0, sy, 0),
                          TB: tr_pt(make_pt(0, sy, 0), (thick, 0, 0)),
                          TC: make_pt(0, sy+1, 0)}
            b_triangle = {TA: make_pt(0, sy+1, 0),
                          TB: tr_pt(make_pt(0, sy, 0), (thick, 0, 0)),
                          TC: tr_pt(make_pt(0, sy+1, 0), (thick, 0, 0))}

            mesh.append((compute_normal(a_triangle), a_triangle))
            mesh.append((compute_normal(b_triangle), b_triangle))

            a_triangle = {TA: make_pt(sample_width-1, sy, 0),
                          TB: make_pt(sample_width-1, sy+1, 0),
                          TC: tr_pt(make_pt(sample_width-1, sy, 0), (-thick, 0, 0))}
            b_triangle = {TA: make_pt(sample_width-1, sy+1, 0),
                          TC: tr_pt(make_pt(sample_width-1, sy, 0), (-thick, 0, 0)),
                          TB: tr_pt(make_pt(sample_width-1, sy+1, 0), (-thick, 0, 0))}

            mesh.append((compute_normal(a_triangle), a_triangle))
            mesh.append((compute_normal(b_triangle), b_triangle))


        # y sides
        for sx in range(in_margin[PX], sample_width-1-in_margin[PX]):
            a_triangle = {TA: make_pt(sx, 0, 0),
                          TB: make_pt(sx+1, 0, 0),
                          TC: tr_pt(make_pt(sx, 0, 0), (0, -thick, 0))}
            b_triangle = {TA: make_pt(sx+1, 0, 0),
                          TB: tr_pt(make_pt(sx+1, 0, 0), (0, -thick, 0)),
                          TC: tr_pt(make_pt(sx, 0, 0), (0, -thick, 0))}

            mesh.append((compute_normal(a_triangle), a_triangle))
            mesh.append((compute_normal(b_triangle), b_triangle))

            a_triangle = {TA: make_pt(sx, sample_height-1, 0),
                          TC: make_pt(sx+1, sample_height-1, 0),
                          TB: tr_pt(make_pt(sx, sample_height-1, 0), (0, thick, 0))}
            b_triangle = {TA: make_pt(sx+1, sample_height-1, 0),
                          TB: tr_pt(make_pt(sx+1, sample_height-1, 0), (0, thick, 0)),
                          TC: tr_pt(make_pt(sx, sample_height-1, 0), (0, thick, 0))}

            mesh.append((compute_normal(a_triangle), a_triangle))
            mesh.append((compute_normal(b_triangle), b_triangle))

        # corners
        #-x+y
        a_triangle = {TA: make_pt(in_margin[PX], 0, 0),
                      TB: tr_pt(make_pt(in_margin[PX], 0, 0), (0, -thick, 0)),
                      TC: make_pt(0, 0, 0)}
        b_triangle = {TA: make_pt(0, in_margin[PY], 0),
                      TB: make_pt(0, 0, 0),
                      TC: tr_pt(make_pt(0, in_margin[PY], 0), (thick, 0, 0))}
        c_triangle = {TA: make_pt(0, 0, 0),
                      TB: tr_pt(make_pt(in_margin[PX], 0, 0), (0, -thick, 0)),
                      TC: tr_pt(make_pt(0, in_margin[PY], 0), (thick, 0, 0))}

        mesh.append((compute_normal(a_triangle), a_triangle))
        mesh.append((compute_normal(b_triangle), b_triangle))
        mesh.append((compute_normal(c_triangle), c_triangle))

        #+x+y
        a_triangle = {TA: make_pt(sample_width-1-in_margin[PX], 0, 0),
                      TB: make_pt(sample_width-1, 0, 0),
                      TC: tr_pt(make_pt(sample_width-1-in_margin[PX], 0, 0), (0, -thick, 0))}
        b_triangle = {TA: make_pt(sample_width-1, 0, 0),
                      TB: make_pt(sample_width-1, in_margin[PY], 0),
                      TC: tr_pt(make_pt(sample_width-1, in_margin[PY], 0), (-thick, 0, 0))}
        c_triangle = {TA: make_pt(sample_width-1, 0, 0),
                      TB: tr_pt(make_pt(sample_width-1, in_margin[PY], 0), (-thick, 0, 0)),
                      TC: tr_pt(make_pt(sample_width-1-in_margin[PX], 0, 0), (0, -thick, 0))}

        mesh.append((compute_normal(a_triangle), a_triangle))
        mesh.append((compute_normal(b_triangle), b_triangle))
        mesh.append((compute_normal(c_triangle), c_triangle))

        #+x-y
        a_triangle = {TA: make_pt(sample_width-1, sample_height-1, 0),
                      TB: make_pt(sample_width-1-in_margin[PX], sample_height-1, 0),
                      TC: tr_pt(make_pt(sample_width-1-in_margin[PX], sample_height-1, 0), (0, thick, 0))}
        b_triangle = {TA: make_pt(sample_width-1, sample_height-1-in_margin[PY], 0),
                      TB: make_pt(sample_width-1, sample_height-1, 0),
                      TC: tr_pt(make_pt(sample_width-1, sample_height-1-in_margin[PY], 0), (-thick, 0, 0))}
        c_triangle = {TA: make_pt(sample_width-1, sample_height-1, 0),
                      TB: tr_pt(make_pt(sample_width-1-in_margin[PX], sample_height-1, 0), (0, thick, 0)),
                      TC: tr_pt(make_pt(sample_width-1, sample_height-1-in_margin[PY], 0), (-thick, 0, 0))}

        mesh.append((compute_normal(a_triangle), a_triangle))
        mesh.append((compute_normal(b_triangle), b_triangle))
        mesh.append((compute_normal(c_triangle), c_triangle))

        #-x-y
        a_triangle = {TA: make_pt(0, sample_height-1, 0),
                      TB: make_pt(0, sample_height-1-in_margin[PY], 0),
                      TC: tr_pt(make_pt(0, sample_height-1-in_margin[PY], 0), (thick, 0, 0))}
        b_triangle = {TA: make_pt(0, sample_height-1, 0),
                      TB: tr_pt(make_pt(in_margin[PX], sample_height-1, 0), (0, thick, 0)),
                      TC: make_pt(in_margin[PY], sample_height-1, 0)}
        c_triangle = {TA: make_pt(0, sample_height-1, 0),
                      TB: tr_pt(make_pt(0, sample_height-1-in_margin[PY], 0), (thick, 0, 0)),
                      TC: tr_pt(make_pt(in_margin[PX], sample_height-1, 0), (0, thick, 0))}

        mesh.append((compute_normal(a_triangle), a_triangle))
        mesh.append((compute_normal(b_triangle), b_triangle))
        mesh.append((compute_normal(c_triangle), c_triangle))

    # inner edges
    if True:
        for sy in range(in_margin[PY], sample_height-1-in_margin[PY]):
                # -x side
                a_triangle = {TA: tr_pt(make_pt(0, sy, 3), (thick, 0, 0)),
                              TB: tr_pt(make_pt(0, sy, 0), (thick, 0, 0)),
                              TC: tr_pt(make_pt(0, sy+1, 0), (thick, 0, 0))}
                a_normal = compute_normal(a_triangle) # -1,0,0 ?
                b_triangle = {TA: tr_pt(make_pt(0, sy+1, 3), (thick, 0, 0)),
                              TB: tr_pt(make_pt(0, sy, 3), (thick, 0, 0)),
                              TC: tr_pt(make_pt(0, sy+1, 0), (thick, 0, 0))}
                b_normal = compute_normal(b_triangle)

                mesh.append((a_normal, a_triangle))
                mesh.append((b_normal, b_triangle))

                if True:
                    # +x side
                    a_triangle = {TA: tr_pt(make_pt(sample_width-1, sy, 3), (-thick, 0, 0)),
                                  TB: tr_pt(make_pt(sample_width-1, sy+1, 0), (-thick, 0, 0)),
                                  TC: tr_pt(make_pt(sample_width-1, sy, 0), (-thick, 0, 0))}
                    a_normal = compute_normal(a_triangle) # 1,0,0 ?
                    b_triangle = {TA: tr_pt(make_pt(sample_width-1, sy+1,3), (-thick, 0, 0)),
                                  TB: tr_pt(make_pt(sample_width-1, sy+1, 0), (-thick, 0, 0)),
                                  TC: tr_pt(make_pt(sample_width-1, sy, 3), (-thick, 0, 0))}
                    b_normal = compute_normal(b_triangle)

                    mesh.append((a_normal, a_triangle))
                    mesh.append((b_normal, b_triangle))
    if True:
        for sx in range(in_margin[PX], sample_width-1-in_margin[PX]):
            # +y side
            a_triangle = {TA: tr_pt(make_pt(sx, 0,3), (0, -thick, 0)),
                          TB: tr_pt(make_pt(sx+1, 0, 0), (0, -thick, 0)),
                          TC: tr_pt(make_pt(sx, 0, 0), (0, -thick, 0))}
            a_normal = compute_normal(a_triangle) # 0,1,0 ?
            b_triangle = {TA: tr_pt(make_pt(sx+1, 0,3), (0, -thick, 0)),
                          TB: tr_pt(make_pt(sx+1, 0, 0), (0, -thick, 0)),
                          TC: tr_pt(make_pt(sx, 0,3), (0, -thick, 0))}
            b_normal = compute_normal(b_triangle)

            mesh.append((a_normal, a_triangle))
            mesh.append((b_normal, b_triangle))

            if True:
                # -y side
                a_triangle = {TA: tr_pt(make_pt(sx, sample_height-1,3), (0, thick, 0)),
                              TB: tr_pt(make_pt(sx, sample_height-1, 0), (0, thick, 0)),
                              TC: tr_pt(make_pt(sx+1, sample_height-1, 0), (0, thick, 0))}
                a_normal = compute_normal(a_triangle) # 0,-1,0 ?
                b_triangle = {TA: tr_pt(make_pt(sx+1, sample_height-1,3), (0, thick, 0)),
                              TB: tr_pt(make_pt(sx, sample_height-1,3), (0, thick, 0)),
                              TC: tr_pt(make_pt(sx+1, sample_height-1, 0), (0, thick, 0))}
                b_normal = compute_normal(b_triangle)

                mesh.append((a_normal, a_triangle))
                mesh.append((b_normal, b_triangle))


    if True:
        #inside corner caps
        mesh.extend(make_square((tr_pt(make_pt(0, in_margin[PY], 3), (thick, 0, 0)),
              tr_pt(make_pt(0, in_margin[PY], 0), (thick, 0, 0)),
              tr_pt(make_pt(in_margin[PX], 0, 0), (0, -thick, 0)),
              tr_pt(make_pt(in_margin[PX], 0, 3), (0, -thick, 0)))))
        mesh.extend(make_square((
            tr_pt(make_pt(sample_width-1-in_margin[PX], 0, 3), (0, -thick, 0)),
            tr_pt(make_pt(sample_width-1-in_margin[PX], 0, 0), (0, -thick, 0)),
            tr_pt(make_pt(sample_width-1, in_margin[PY], 0), (-thick, 0, 0)),
            tr_pt(make_pt(sample_width-1, in_margin[PY], 3), (-thick, 0, 0)))))
        mesh.extend(make_square((
            tr_pt(make_pt(sample_width-1, sample_height-1-in_margin[PY], 3), (-thick, 0, 0)),
            tr_pt(make_pt(sample_width-1, sample_height-1-in_margin[PY], 0), (-thick, 0, 0)),
            tr_pt(make_pt(sample_width-1-in_margin[PX], sample_height-1, 0), (0, thick, 0)),
            tr_pt(make_pt(sample_width-1-in_margin[PX], sample_height-1, 3), (0, thick, 0)))))
        mesh.extend(make_square((
            tr_pt(make_pt(in_margin[PX], sample_height-1, 3), (0, thick, 0)),
            tr_pt(make_pt(in_margin[PX], sample_height-1, 0), (0, thick, 0)),
            tr_pt(make_pt(0, sample_height-1-in_margin[PY], 0), (thick, 0, 0)),
            tr_pt(make_pt(0, sample_height-1-in_margin[PY], 3), (thick, 0, 0)))))



    print "Generated %s triangles." % len(mesh)
    return mesh

def get_positive(mesh):
    base = [1,1,1]
    thresh = [1,1,1]
    for tx, tri in enumerate(mesh):
        for pt in [TA, TB, TC]:
            # print '----'
            # print tx, tri
            # print pt
            # print mesh[tx][1][pt][PX]
            # print mesh[tri][pt][PX]
            if (mesh[tx][1][pt][PX] < thresh[PX]):
                thresh[PX] = mesh[tx][1][pt][PX]
            if (mesh[tx][1][pt][PY] < thresh[PY]):
                thresh[PY] = mesh[tx][1][pt][PY]
            if (mesh[tx][1][pt][PZ] < thresh[PZ]):
                thresh[PZ] = mesh[tx][1][pt][PZ]

    if thresh != base:
        inc = numpy.subtract(base, thresh)
        for tx, tri in enumerate(mesh):
            for pt in [TA,TB,TC]:
                mesh[tx][1][pt] = numpy.add(mesh[tx][1][pt], inc)

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
    dataset = gdal.Open('mtr-v2.tif', gdal.GA_ReadOnly)
    get_general_info(dataset)
    mesh = get_mesh(dataset)
    mesh = get_positive(mesh)
    print "Writing STL"
    write_stl("output.stl", mesh)


main()
