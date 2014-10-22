from indicies import * 

class Builder(object):
    
    def __init__(self, kwargs):
        self.src = kwargs['src'];
        self.sample_rate = kwargs['sample_rate']
        self.output_size_x = kwargs['output_size_x']
        self.wall_thickness = kwargs['wall_thickness']
        self.input_scale_vector = [1,1,1]
        self.output_scalar = 1
        self.resize_ratio = kwargs['resize_ratio']
        self.output_file_name = kwargs['output_file_name']
        
    def get_src_file(self):
        return self.src
        
    def get_input_sample_rate(self):
        return self.sample_rate
        
    def get_resize_ratio(self):
        return self.resize_ratio
        
    def get_output_file_name(self):
        return self.output_file_name