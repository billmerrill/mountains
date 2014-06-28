
class Mesh:
    
    def __init__(self, xsize=0, ysize=0):
        self.xsize = xsize 
        self.ysize = ysize
        self.mesh = []
        
    def add_row(self, row):
        self.mesh.append(row)
        
    def __str__(self):
        strs = []
        for i in range(0, len(self.mesh)):
            strs.append(", ".join([str(x) for x in self.mesh[i]]))
        return "\n".join(strs)
               
    