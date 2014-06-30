import pprint
import gdal
from geohelpers import get_general_info
from elevation_reader import sample_mesh_in_meters
from mesh import Mesh


build_config = { 'src': 'mtr-sq.tif',
                 'sample_rate': 10}


def build(dataset):
    elevation_mesh_meters = sample_mesh_in_meters(build_config, dataset)
    print elevation_mesh_meters
    
def main():
    dataset = gdal.Open(build_config['src'], gdal.GA_ReadOnly)
    get_general_info(dataset)
    build(dataset)
    
main()
