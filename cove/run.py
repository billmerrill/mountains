import pprint
import gdal
from geohelpers import get_general_info
from mesh import Mesh, HorizontalPointPlane
from stl_canvas import STLCanvas
from builder import Builder
from elevation import Elevation
from indicies import *
from model import SolidElevationModel


build_config = { 'src': 'mtr-sq.tif',
                 'output_resolution_max': 50,
                 'output_physical_max': 200
                 }

def build_solid_model():
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
    
    
def new_run():
    builder = Builder(build_config)
    model = SolidElevationModel(build_config)
    model.build_stl()
    
new_run()
