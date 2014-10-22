import struct
import math
import numpy
from indicies import *

class STLCanvas:
    
    def __init__(self):
        self.triangles = []
        
    def add_triangle(self, tri):
        ''' assume points follow right hand rule 
        '''
        self.triangles.append(tri)
        
    def add_square(self, square, invert_normal = False):
        ''' assume points like this for right hand rule
            0  1
            2  3
        '''
        if invert_normal:
            self.add_triangle([square[0], square[1], square[3]])
            self.add_triangle([square[0], square[3], square[2]])
        else:
            self.add_triangle([square[0], square[3], square[1]])
            self.add_triangle([square[0], square[2], square[3]])
            
    def add_mesh(self, mesh, invert_normal = False):
        for sy in range(0, mesh.y_max()):
            for sx in range(0, mesh.x_max()):
                self.add_square([mesh.get(sx,sy),
                                 mesh.get(sx+1, sy),
                                 mesh.get(sx, sy+1),
                                 mesh.get(sx+1, sy+1)], invert_normal)
                                     
        
    def compute_normal(self, triangle):
        Nraw = numpy.cross( numpy.subtract(triangle[TA], triangle[TB]),
                                   numpy.subtract(triangle[TA], triangle[TC]) )
        hypo = math.sqrt(Nraw[PX]**2 + Nraw[PY]**2 + Nraw[PZ]**2)
        N = (Nraw[PX] / hypo,
             Nraw[PY] / hypo,
             Nraw[PZ] / hypo)
        return N
        
    def add_mesh_sandwich(self, s1, s2):
        if not (s1.xsize == s2.xsize and s1.ysize == s2.ysize):
            print ("CANT MAKE SAMMICHES")
            return
       
        self.add_mesh(s1)
        self.add_mesh(s2, invert_normal=True)
        
        for sy in range(0, s1.y_max()):
            self.add_square([s1.get(0,sy),
                             s1.get(0,sy+1),
                             s2.get(0,sy),
                             s2.get(0,sy+1)])
            self.add_square([s1.get(s1.x_max(), sy+1),
                             s1.get(s1.x_max(), sy),
                             s2.get(s2.x_max(), sy+1),
                             s2.get(s2.x_max(), sy)])
            
                            
        for sx in range(0, s1.x_max()):
            self.add_square([s1.get(sx+1,0),
                             s1.get(sx,0),
                             s2.get(sx+1,0),
                             s2.get(sx,0)])
            self.add_square([s1.get(sx, s1.y_max()),
                             s1.get(sx+1, s1.y_max()),
                             s2.get(sx, s2.y_max()),
                             s2.get(sx+1, s2.y_max())])
                             
        
    def write_stl(self, outfile):
        print ("Writing %s triangles" % len(self.triangles))
        with open(outfile, 'wb') as dest_file:
            dest_file.write(struct.pack("80sI", b'Quick Release Lever', len(self.triangles)))
            for tri in self.triangles:
                normal = self.compute_normal(tri)
                data = [normal[PX], normal[PY], normal[PZ],
                    tri[TA][PX], tri[TA][PY], tri[TA][PZ],
                    tri[TB][PX], tri[TB][PY], tri[TB][PZ],
                    tri[TC][PX], tri[TC][PY], tri[TC][PZ],0]
                dest_file.write(struct.pack("12fH", *data))
