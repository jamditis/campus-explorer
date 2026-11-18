import bpy, numpy as np, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state/'
DT=np.load(R+'data/dtm_1m.npy'); H=DT.shape[0]/2
def dtm(x,y):
    fx=x+H-0.5; fy=y+H-0.5; j=int(np.floor(fx)); i=int(np.floor(fy)); a=fx-j; b=fy-i
    return float(DT[i,j]*(1-a)*(1-b)+DT[i,j+1]*a*(1-b)+DT[i+1,j]*(1-a)*b+DT[i+1,j+1]*a*b)
dg=bpy.context.evaluated_depsgraph_get()
def bv(o):
    e=o.evaluated_get(dg); me=e.to_mesh(); mw=o.matrix_world
    b=BVHTree.FromPolygons([tuple(mw@v.co) for v in me.vertices],[tuple(p.vertices) for p in me.polygons]); e.to_mesh_clear(); return b
B=[(o.name,bv(o)) for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS107_Chapin','Chapin','Buildings'))]
print('BLD',[n for n,_ in B][:20])
for y in np.arange(-201,-159,1.0):
    hits=[]
    for n,b in B:
        h=b.ray_cast(Vector((-230,y,125.6)),Vector((1,0,0)),40)
        if h[0] is not None: hits.append((round(h[0].x,2),n[:28]))
    print('FAC',y,min(hits) if hits else None)
for nm in ('WS116_Chapin_W_N_connector','WS116_Chapin_W_bed_E2','WS116_Chapin_W_bed_W','WS117_Chapin_W_entrance_landing','WS117_Chapin_W_entrance_cheek'):
    o=next(o for o in bpy.data.objects if o.name.startswith(nm)); mw=o.matrix_world
    ws=[mw@v.co for v in o.data.vertices]
    ys=max(w.y for w in ws); top=[w for w in ws if w.y>ys-0.05]
    print('NEND',nm,round(ys,2),[(round(w.x,2),round(w.z,2)) for w in sorted(top,key=lambda w:w.x)])
fp=bpy.data.objects['Footpaths_OSM']; mw=fp.matrix_world; me=fp.data
for p in me.polygons:
    c=mw@p.center
    if -224<c.x<-203 and -186<c.y<-160:
        ws=[mw@me.vertices[i].co for i in p.vertices]
        print('FP',p.index,round(c.x,1),round(c.y,1),round(c.z-dtm(c.x,c.y),2),[(round(w.x,1),round(w.y,1)) for w in ws])
for y in np.arange(-186,-159,2.0):
    print('DTM',y,' '.join('%.2f'%dtm(x,y) for x in np.arange(-224,-203,1.0)))
