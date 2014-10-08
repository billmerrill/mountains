from indicies import * 

class Builder(object):
    
    def __init__(self, kwargs):
        self.src = kwargs['src'];
        self.sample_rate = kwargs['sample_rate']
        self.output_size_x = kwargs['output_size_x']
        self.wall_thickness = kwargs['wall_thickness']
        self.input_scale_vector = [1,1,1]
        self.output_scalar = 1
        
    def get_src_file(self):
        return self.src
        
    def get_input_sample_rate(self):
        return self.sample_rate