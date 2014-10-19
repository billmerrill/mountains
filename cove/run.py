import pprint
import gdal
from geohelpers import get_general_info
from mesh import Mesh, HorizontalPointPlane
from stl_canvas import STLCanvas
from builder import Builder
from elevation import Elevation
from indicies import *


build_config = { 'src': 'mtr-sq.tif',
                 'sample_rate': 10,
                 'output_size_x': 600,
                 'resize_ratio': [0.1, 0.1],
                 'wall_thickness': 5 #mm
                 }

def main():
    builder = Builder(build_config)
    
    elevation = Elevation(builder)
    elevation.load_dataset()
    elevation.display_summary()
    
    top = Mesh(builder, elevation)
    #top.load_matrix(elevation.get_elevation_in_meters()) 
    top.load_matrix(elevation.get_elevation_in_meters_with_gdal_resample()) 
    top.scale_to_output_size(builder.output_size_x)

    bottom = HorizontalPointPlane(top, 1)
    
    canvas = STLCanvas()
    canvas.add_mesh_sandwich(top, bottom)
    canvas.write_stl("cove_output.stl")
    
    
main()
