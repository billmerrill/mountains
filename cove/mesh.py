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
        
        for i,rows in enumerate(self.mesh):
            for j,pixs in enumerate(self.mesh[i]):
                self.mesh[i][j] = [src.mesh[i][j][PX] * scalar[PX] + translate[PX],
                                   src.mesh[i][j][PY] * scalar[PX] + translate[PY],
                                   src.mesh[i][j][PZ] * scalar[PX] + translate[PZ]]
        for sy in range(0, self.y_max()):
            for sx in range(0, self.x_max()):
                self.mesh[sy][sx] = [src.mesh[sy][sx][PX] * scalar[PX] + translate[PX],
                                     src.mesh[sy][sx][PY] * scalar[PX] + translate[PY],
                                     src.mesh[sy][sx][PZ] * scalar[PX] + translate[PZ]]
                                   
    def get_data_x_size(self):
        return self.mesh[0][self.x_max()][PX] - self.mesh[0][0][PX]
        
    def get_data_y_size(self):
        return self.mesh[self.y_max()][0][PY] - self.mesh[0][0][PY]
    
    def get_max_corner(self):
        return self.mesh[self.y_max()][self.x_max()]
    
    def get(self, x, y):
        return self.mesh[y][x]