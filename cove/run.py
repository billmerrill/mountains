from model import SolidElevationModel, DebugElevationModel


model_config = { 'src': 'mto.tif',
                 'output_resolution_max': 100,
                 'output_physical_max': 200
                 }

def main():
    model = DebugElevationModel(model_config)
    model.build_stl()
    
main()
