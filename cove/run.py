import pprint
import gdal
from geohelpers import get_general_info
from elevation_reader import sample_elevation
from mesh import Mesh


build_config = { 'src': 'mtr-sq.tif',
                 'sample_rate': 100}


def build(dataset):
    elevation_mesh = sample_elevation(build_config, dataset)
    print elevation_mesh
    pprint.pprint(elevation_mesh)

def main():
    dataset = gdal.Open(build_config['src'], gdal.GA_ReadOnly)
    get_general_info(dataset)
    build(dataset)
    
main()
