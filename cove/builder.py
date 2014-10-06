from indicies import * 

class Builder(object):
    
    def __init__(self, **kwargs):
        self.src = kwargs['src'];
        self.sample_rate = kwargs['sample_rate']
        self.x_output_max = kwargs['x_output_max']
        self.wall_thickness = kwargs['wall_thickness']
        self.input_scale_vector = [1,1,1]
        self.output_scalar = 1
        
    def scale_pt(self, pt):
        return [pt[PX] * self.scale_factor[PX] * output_scalar ,
                pt[PY] * self.scale_factor[PY] * output_scalar,
                pt[PZ] * self.scale_facotr[PZ] * output_scalar]
    