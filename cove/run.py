import pprint
import gdal
from geohelpers import get_general_info
from elevation_reader import sample_mesh_in_meters, scale_mesh_to_output
from mesh import Mesh
from stl_canvas import STLCanvas


build_config = { 'src': 'mtr-sq.tif',
                 'sample_rate': 10,
                 'x_output_max': 600 #mm
                 }


def build(dataset):
    
    elevation_mesh_meters = sample_mesh_in_meters(build_config, dataset)
    elevation_mesh_output_scaled = scale_mesh_to_output(build_config, elevation_mesh_meters)
    
    top = elevation_mesh_output_scaled
    bottom = Mesh()
    bottom.copy(top, scalar=[1,1,1], translate=[0,0,-20])
    
    print elevation_mesh_meters.get_max_corner()
    print elevation_mesh_output_scaled.get_max_corner()
    
    

    
    canvas = STLCanvas()
    canvas.add_mesh(top)
    # canvas.add_mesh(bottom)
    canvas.write_stl("cove_out.stl")
    
def main():
    dataset = gdal.Open(build_config['src'], gdal.GA_ReadOnly)
    get_general_info(dataset)
    build(dataset)
    
main()
