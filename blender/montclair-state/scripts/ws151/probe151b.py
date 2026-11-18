import bpy, numpy as np
from mathutils import Vector
P='/workspace/nj-scenes/montclair-state/montclair_state.blend'
want=[l for l in open('/workspace/nj-scenes/montclair-state/scripts/ws151/objnames.txt').read().split('\n') if l.startswith(('WS150_Lot9','WS148_Lot9','WS142_Lot9','WS135a_Skyline_Way','WS145_walk','WS147_walk','WS143_Freeman_E','Curbs_granite_OSM'))]
with bpy.data.libraries.load(P, link=False) as (src,dst): dst.objects=list(want)
for o in dst.objects: bpy.context.scene.collection.objects.link(o)
bpy.context.view_layer.update()
cu=bpy.data.objects['Curbs_granite_OSM']; mw=cu.matrix_world
print("CURVE splines",len(cu.data.splines), "mod inputs", {k:cu.modifiers[0][k] for k in cu.modifiers[0].keys()})
for i,s in enumerate(cu.data.splines):
    pts=[mw@p.co.to_3d() for p in (s.points if s.type=='POLY' or s.type=='NURBS' else s.bezier_points)]
    inb=[j for j,w in enumerate(pts) if -75<w.x<-58 and -205<w.y<-172]
    if inb: print("SPL",i,s.type,len(pts),"inbox idx",inb[0],inb[-1],[(round(pts[j].x,2),round(pts[j].y,2),round(pts[j].z,2)) for j in range(max(0,inb[0]-1),min(len(pts),inb[-1]+2))])
dg=bpy.context.evaluated_depsgraph_get()
for x in np.arange(-70,-61.9,0.5):
    row=[]
    for y in np.arange(-196,-183,0.5):
        h=bpy.context.scene.ray_cast(dg,Vector((float(x),float(y),200.0)),Vector((0,0,-1)))
        row.append("%s:%s@%.3f"%(y,h[4].name[:6]+h[4].name[-4:] if h[0] else '-',h[1].z if h[0] else 0))
    print("COL",x," ".join(row))
