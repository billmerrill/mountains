from indicies import * 

class Builder(object):
    
    def __init__(self, kwargs):
        self.src_filename = kwargs['src'];
        self.dst_filename = kwargs.get('dst', self._default_dst_name())
        self.output_resolution_max = kwargs.get('output_resolution_max', 50) # data points
        self.output_physical_max = kwargs.get('output_physical_max', 200) # output mm
        
        self.sample_rate = kwargs.get('sample_rate', 1)
        self.output_size_x = kwargs.get('output_size_x', 200)
        self.resize_ratio = kwargs.get('resize_ratio', (1,1))
        
    def _default_dst_name(self):
        return self.src_filename.replace(".tif", ".stl")
        
    def get_src_filename(self):
        return self.src_filename
        
    def get_input_sample_rate(self):
        return self.sample_rate
        
    def get_resize_ratio(self, src_longest_size=None):
        if src_longest_size:
            ratio = float(self.output_resolution_max) / src_longest_size
            self.resize_ratio = (ratio, ratio)
            
        return self.resize_ratio
        
    def get_output_file_name(self):
        return self.dst_filename
        
    def get_physical_max(self):
        return self.output_physical_max
        