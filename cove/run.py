from model import SolidElevationModel


model_config = { 'src': 'mtr-sq.tif',
                 'output_resolution_max': 100,
                 'output_physical_max': 200
                 }

def main():
    model = SolidElevationModel(model_config)
    model.build_stl()
    
main()