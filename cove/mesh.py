from indicies import * 
import copy

class Mesh:
    
    def __init__(self, xsize=0, ysize=0):
        self.xsize = xsize 
        self.ysize = ysize
        self.mesh = []
        
    def add_row(self, row):
        self.mesh.append(row)
        
    def x_max(self):
        return self.xsize-1
        
    def y_max(self):
        return self.ysize-1
        
    def __str__(self):
        strs = []
        for i in range(0, len(self.mesh)):
            strs.append(", ".join([str(x) for x in self.mesh[i]]))
        return "\n".join(strs)
               
    def copy(self, src, scalar = [1,1,1], translate = [0,0,0]):
        self.xsize = src.xsize
        self.ysize = src.ysize
        self.mesh = copy.deepcopy(src.mesh)
        self.transform(scalar, translate)
                                   
    def get_data_x_size(self):
        return self.mesh[0][self.x_max()][PX] - self.mesh[0][0][PX]
        
    def get_data_y_size(self):
        return self.mesh[self.y_max()][0][PY] - self.mesh[0][0][PY]
    
    def get_max_corner(self):
        return self.mesh[self.y_max()][self.x_max()]
    
    def get(self, x, y):
        return self.mesh[y][x]
        
    def transform(self, scalar, translate):
        for sy in range(0, self.ysize):
            for sx in range(0, self.xsize):
                self.mesh[sy][sx] = [self.mesh[sy][sx][PX] * scalar[PX] + translate[PX],
                                     self.mesh[sy][sx][PY] * scalar[PY] + translate[PY],
                                     self.mesh[sy][sx][PZ] * scalar[PZ] + translate[PZ]]

        return self
    
    def get_pixel_size(self):
        return [self.mesh[0][1]-self.mesh[0][0], self.mesh[1][0] - self.mesh[0][0]]
        
    def load_matrix(self, src):
        '''
        src: a 2 dimensional python array
        '''
        self.mesh = copy.deepcopy(src)
        self.ysize = len(src)
        self.xsize = len(src[0])
        
    def scale_to_output_size(self, max_output_size):
        input_max_data_size = max(self.get_data_x_size(), self.get_data_y_size())
        output_ratio = max_output_size / input_max_data_size
        self.transform([output_ratio, output_ratio, output_ratio], [0,0,0])
        
                

class HorizontalPointPlane(object):
    
    def __init__(self, src_mesh, elevation):
        self.src_mesh = src_mesh
        self.elevation = elevation
        self.xsize = src_mesh.xsize
        self.ysize = src_mesh.ysize
        
    def get(self, x, y):
        orig = self.src_mesh.get(x,y)
        return [orig[PX], orig[PY], self.elevation]        
        
    def x_max(self):
        return self.xsize-1
        
    def y_max(self):
        return self.ysize-1
        