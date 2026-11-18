import bpy, numpy as np
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
def rc(o,d):
    h=sc.ray_cast(dg,Vector(o),Vector(d))
    if not h[0]: return None
    ob=h[4]; mn='?'
    try:
        if ob.type=='MESH' and h[3]<len(ob.data.polygons): mn=ob.data.materials[ob.data.polygons[h[3]].material_index].name
    except Exception: pass
    return ob.name[:48],mn,tuple(round(c,2) for c in h[1])
def gz(x,y):
    r=rc((x,y,300),(0,0,-1)); return r[2][2] if r else 0
# camera 1245: WS139_CAM_eye_strip_seam_from_W
eye=Vector((-174,-279,gz(-174,-279)+1.7)); tgt=Vector((-136,-280,gz(-136,-280)+2.0))
q=(tgt-eye).to_track_quat('-Z','Y'); lens=26; sw=36.0
W,H=640,360
for py in (200,205,210,215,222,230):
    for px in range(20,340,25):
        x=(px/W-0.5)*sw; y=-(py/H-0.5)*sw*H/W
        d=q@Vector((x,y,-lens))
        r=rc(eye,d); print('C1245',px,py,r)
# top-down grid over the lawn W of the lot and bank N of W end
hits={}
for x in np.arange(-190,-150,2.0):
    for y in np.arange(-300,-250,2.0):
        r=rc((x,y,300),(0,0,-1))
        if r: hits.setdefault((r[0],r[1]),[]).append((float(x),float(y)))
for k,v in sorted(hits.items(),key=lambda kv:-len(kv[1])):
    xs=[a for a,b in v]; ys=[b for a,b in v]
    print('TOP',k,len(v),'x',min(xs),max(xs),'y',min(ys),max(ys))
