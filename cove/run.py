import pprint
import gdal
from geohelpers import get_general_info
from elevation_reader import sample_mesh_in_meters, scale_mesh_to_output
from mesh import Mesh, ConstantMesh
from stl_canvas import STLCanvas
from builder import Builder


# build_config = { 'src': 'mtr-sq.tif',
#                  'sample_rate': 10,
#                  'x_output_max': 600,
#                  'wall_thickness': 5 #mm
#                  }

build_config = Builder( src =  'mtr-sq.tif',
                        sample_rate = 10,
                        x_output_max = 600,
                        wall_thickness = 5)




def build(dataset):
    '''
    To make a solid terrain mesh of uniform thickness:
    ==================================================
    
    top = scale_mesh_to_output(build_config, elevation_mesh_meters)
    bottom = Mesh()
    tr_thick = build_config['wall_thickness'] * -1
    bottom.copy(top, scalar=[1,1,1], translate=[0,0,tr_thick])
    canvas.add_mesh_sandwich(top, bottom)
    
    To make a terrain block:
    ========================
    top = scale_mesh_to_output(build_config, elevation_mesh_meters)
    canvas = STLCanvas()
    canvas.add_terrain_block(top)
    '''
    elevation_mesh_meters = sample_mesh_in_meters(build_config, dataset)
    top = scale_mesh_to_output(build_config, elevation_mesh_meters)
    bottom = ConstantMesh(1, elevation_mesh_meters.xsize, elevation_mesh_meters.ysize)
    
    # bottom = Mesh()
    # tr_thick = build_config['wall_thickness'] * -1
    # bottom.copy(top, scalar=[1,1,1], translate=[0,0,tr_thick])
    
    
    canvas = STLCanvas()
    canvas.add_mesh(top)
    canvas.add_mesh(bottom)
    # canvas.add_mesh_sandwich(top, bottom)
    
    canvas.write_stl("cove_out.stl")
    
def main():
    dataset = gdal.Open(build_config.src, gdal.GA_ReadOnly)
    get_general_info(dataset)
    build(dataset)
    
main()
