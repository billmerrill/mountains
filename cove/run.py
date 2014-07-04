import pprint
import gdal
from geohelpers import get_general_info
from elevation_reader import sample_mesh_in_meters, scale_mesh_to_output
from mesh import Mesh


build_config = { 'src': 'mtr-sq.tif',
                 'sample_rate': 10,
                 'x_output_max': 600 #mm
                 }


def build(dataset):
    
    elevation_mesh_meters = sample_mesh_in_meters(build_config, dataset)
    elevation_mesh_output_scaled = scale_mesh_to_output(build_config, elevation_mesh_meters)
    
    print elevation_mesh_meters.get_max_corner()
    print elevation_mesh_output_scaled.get_max_corner()
    
def main():
    dataset = gdal.Open(build_config['src'], gdal.GA_ReadOnly)
    get_general_info(dataset)
    build(dataset)
    
main()
