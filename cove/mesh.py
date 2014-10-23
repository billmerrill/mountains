from indicies import * 
import copy

class CanvasShape(object):
    
    def get_triangles(self):
        pass 

class GridShape(object):
    
    def triangulate_square(self, square, invert_normal = False):
        ''' assume points like this for right hand rule
            0  1
            2  3
        '''
        tri = []
        if invert_normal:
            return [[square[0], square[1], square[3]],
                   [square[0], square[3], square[2]]]
        else:
            return [[square[0], square[3], square[1]],
                   [square[0], square[2], square[3]]]   
                   
                   
class MeshSandwich(GridShape):
    def __init__(self, top, bottom):
        if not (top.xsize == bottom.xsize and top.ysize == bottom.ysize):
            print ("CANT MAKE SAMMICHES")
            return
        self.xsize = top.xsize
        self.ysize = top.ysize
        self.top = top
        self.bottom = bottom
 
    def triangulate(self):
        triangles = self.top.triangulate()
        triangles.extend(self.bottom.triangulate())
        triangles.extend(self.triangulate_sides())    
        return triangles
    
    def triangulate_sides(self):
        triangles = []
        for sy in range(0, self.top.y_max()):
            triangles.extend(self.triangulate_square([self.top.get(0,sy),
                             self.top.get(0,sy+1),
                             self.bottom.get(0,sy),
                             self.bottom.get(0,sy+1)]))
            triangles.extend(self.triangulate_square([self.top.get(self.top.x_max(), sy+1),
                             self.top.get(self.top.x_max(), sy),
                             self.bottom.get(self.bottom.x_max(), sy+1),
                             self.bottom.get(self.bottom.x_max(), sy)]))
            
                            
        for sx in range(0, self.top.x_max()):
            triangles.extend(self.triangulate_square([self.top.get(sx+1,0),
                             self.top.get(sx,0),
                             self.bottom.get(sx+1,0),
                             self.bottom.get(sx,0)]))
            triangles.extend(self.triangulate_square([self.top.get(sx, self.top.y_max()),
                             self.top.get(sx+1, self.top.y_max()),
                             self.bottom.get(sx, self.bottom.y_max()),
                             self.bottom.get(sx+1, self.bottom.y_max())]))
                             
        return triangles
        

class Mesh(GridShape):
    
    def __init__(self, xsize=0, ysize=0):
        self.xsize = xsize 
        self.ysize = ysize
        self.mesh = []
            
    def triangulate(self, invert_normal = False):
        triangles = []
        for sy in range(0, self.y_max()):
            for sx in range(0, self.x_max()):
                triangles.extend(self.triangulate_square([self.get(sx,sy),
                                     self.get(sx+1, sy),
                                     self.get(sx, sy+1),
                                     self.get(sx+1, sy+1)], 
                                     invert_normal))        
                                 
        return triangles
        
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
        
                

class HorizontalPointPlane(GridShape):
    
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
        
    def triangulate(self, invert_normal = False):
        triangles = []
        for sy in range(0, self.y_max()):
            for sx in range(0, self.x_max()):
                triangles.extend(self.triangulate_square([self.get(sx,sy),
                                     self.get(sx+1, sy),
                                     self.get(sx, sy+1),
                                     self.get(sx+1, sy+1)], 
                                     invert_normal))   
        return triangles
        
class MeshBasePlate(object):
    '''
    A custom set of triangles to draw a bottom plate
    '''
    
    def __init__(self, top, elevation=0):
        self.top = top
        self.xsize = top.xsize
        self.ysize = top.ysize
        self.elevation = elevation
    
    def get(self, x, y):
        orig = self.top.get(x,y)
        return [orig[PX], orig[PY], self.elevation]  
        
    def x_max(self):
        return self.xsize-1
        
    def y_max(self):
        return self.ysize-1        
    
    def triangulate(self):
        triangles = []
        
        def make_pt(x, y, z):
            orig = self.top.get(x,y)
            return (orig[PX],orig[PY],self.elevation)
            
        sample_height = self.top.y_max()+1
        sample_width = self.top.x_max()+1
        
        yhalf = sample_height / 2
        xhalf = sample_width / 2
        yquarter = sample_height / 4
        xquarter = sample_width / 4

        negx = make_pt(xquarter, yhalf, 0)
        posx = make_pt(xquarter + xhalf, yhalf, 0)
        negy = make_pt(xhalf, yquarter, 0)
        posy = make_pt(xhalf, yquarter + yhalf, 0)

        # star inset base
        for sy in range(0, sample_height-1):
            a_triangle = { TA: make_pt(0, sy, 0),
                           TB: negx,
                           TC: make_pt(0, sy+1, 0)}
            z_triangle = { TA: make_pt(sample_width-1, sy, 0),
                          TB: make_pt(sample_width-1, sy+1, 0),
                          TC: posx }

            triangles.append(a_triangle)
            triangles.append(z_triangle)

        for sx in range(0, sample_width-1):
            a_triangle = { TA: make_pt(sx, 0, 0),
                           TB: make_pt(sx+1, 0, 0),
                           TC: negy }
            z_triangle = { TA: make_pt(sx, sample_height-1, 0),
                           TB: posy,
                           TC: make_pt(sx+1, sample_height-1, 0) }

            triangles.append(a_triangle)
            triangles.append(z_triangle)


        a_triangle = { TA: make_pt(0,0,0),
                       TB: negy,
                       TC: negx }
        b_triangle = { TA: negy,
                       TB: make_pt(sample_width-1, 0, 0),
                       TC: posx }
        c_triangle = { TA: posx,
                       TB: make_pt(sample_width-1, sample_height-1, 0),
                       TC: posy }
        d_triangle = { TA: negx,
                       TB: posy,
                       TC: make_pt(0, sample_height-1, 0) }

        e_triangle = { TA: negy,
                       TB: posx,
                       TC: negx }

        f_triangle = { TA: posx,
                       TB: posy,
                       TC: negx }

        triangles.append(a_triangle)
        triangles.append(b_triangle)
        triangles.append(c_triangle)
        triangles.append(d_triangle)
        triangles.append(e_triangle)
        triangles.append(f_triangle)

        return triangles
    
        