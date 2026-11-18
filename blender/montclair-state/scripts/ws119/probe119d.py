import bpy, numpy as np
R='/workspace/nj-scenes/montclair-state/'
DT=np.load(R+'data/dtm_1m.npy'); H=DT.shape[0]/2
def dtm(x,y):
    fx=x+H-0.5; fy=y+H-0.5; j=int(np.floor(fx)); i=int(np.floor(fy)); a=fx-j; b=fy-i
    return float(DT[i,j]*(1-a)*(1-b)+DT[i,j+1]*a*(1-b)+DT[i+1,j]*(1-a)*b+DT[i+1,j+1]*a*b)
fp=bpy.data.objects['Footpaths_OSM']; mw=fp.matrix_world; me=fp.data
for p in me.polygons:
    c=mw@p.center
    if -224<c.x<-208 and -173<c.y<-160:
        n=(mw.to_3x3()@p.normal).normalized()
        print('FP',p.index,round(c.x,2),round(c.y,2),'dz',round(c.z-dtm(c.x,c.y),2),'nz',round(n.z,2),'A',round(p.area,2))
for o in bpy.data.objects:
    if o.type=='MESH' and o.name.startswith('WS102_CollegeAve_S_carriageway'):
        pass
