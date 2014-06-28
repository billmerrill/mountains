import gdal
import gdalconst
import pprint


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

