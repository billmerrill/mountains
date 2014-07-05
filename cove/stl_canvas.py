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
        
    def add_square(self, square):
        ''' assume points like this for right hand rule
            0  1
            2  3
        '''
        self.add_triangle([square[0], square[3], square[1]])
        self.add_triangle([square[0], square[2], square[3]])
        
    def add_mesh(self, mesh):
        for sy in range(0, mesh.y_max()):
            for sx in range(0, mesh.x_max()):
                self.add_square([mesh.get(sx,sy),
                                 mesh.get(sx+1, sy),
                                 mesh.get(sx, sy+1),
                                 mesh.get(sx+1, sy+1)])
        
    def compute_normal(self, triangle):
        Nraw = numpy.cross( numpy.subtract(triangle[TA], triangle[TB]),
                                   numpy.subtract(triangle[TA], triangle[TC]) )
        hypo = math.sqrt(Nraw[PX]**2 + Nraw[PY]**2 + Nraw[PZ]**2)
        N = (Nraw[PX] / hypo,
             Nraw[PY] / hypo,
             Nraw[PZ] / hypo)
        return N
        
    def write_stl(self, outfile):
        with open(outfile, 'wb') as dest_file:
            dest_file.write(struct.pack("80sI", b'Quick Release Lever', len(self.triangles)))
            for tri in self.triangles:
                normal = self.compute_normal(tri)
                data = [normal[PX], normal[PY], normal[PZ],
                    tri[TA][PX], tri[TA][PY], tri[TA][PZ],
                    tri[TB][PX], tri[TB][PY], tri[TB][PZ],
                    tri[TC][PX], tri[TC][PY], tri[TC][PZ],0]
                dest_file.write(struct.pack("12fH", *data))
