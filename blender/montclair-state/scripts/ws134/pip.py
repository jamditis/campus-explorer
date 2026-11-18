import numpy as np
def pip(poly,x,y):
    poly=np.asarray(poly); n=len(poly); ins=np.zeros(len(x),bool)
    for i in range(n):
        x1,y1=poly[i]; x2,y2=poly[(i+1)%n]
        c=((y1>y)!=(y2>y)) & (x < (x2-x1)*(y-y1)/((y2-y1)+1e-12)+x1)
        ins^=c
    return ins
