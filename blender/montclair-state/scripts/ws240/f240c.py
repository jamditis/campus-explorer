# W12c (ws240) cont.: probe240b (camera rays) found the 'dark lip' at the apron's SE end in the SW eye view is the W54 lawn
# shoulder (WS226_CCOM_dock_apron_lawn_shoulder_UNVERIFIED): its material WS70_berm_lawn_ortho_matched tints the grass by
# the 2020 ortho through the 'ortho' UV, and right beside the apron the ortho shows the apron's dark asphalt, so the grass bank
# rendered as a dark asphalt-toned wedge. The new f240b lawn bank had no 'ortho' UV at all (one corner texel). Fix: both get an
# 'ortho' UV taken from the terrain's own planar ortho mapping (affine fit), sampled 1.5-6 m further AWAY from the apron at the
# first green (lawn) texel, so they take the tone of the lawn they blend into. Geometry unchanged.
import bpy, numpy as np
from mathutils import Vector
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=T.data; M=T.matrix_world
uvl=me.uv_layers['ortho'].data
ap0=bpy.data.objects['CCOM_dock_apron_20261014jf3']; c0=sum((ap0.matrix_world@v.co for v in ap0.data.vertices),Vector())/len(ap0.data.vertices)
near=[v.index for v in me.vertices if ((M@v.co).xy-c0.xy).length<40]; ns=set(near)
li=[l.index for l in me.loops if l.vertex_index in ns]
P=np.array([tuple(M@me.vertices[me.loops[i].vertex_index].co)[:2] for i in li]); U=np.array([tuple(uvl[i].uv) for i in li])
X=np.c_[P,np.ones(len(P))]; A,res,_,_=np.linalg.lstsq(X,U,rcond=None)
err=np.abs(X@A-U).max(); print('F240C local affine (40 m) loops',len(li),'maxerr',float(err),'(texels',float(err)*2048,')',flush=True)
img=next(i for i in bpy.data.images if i.name.startswith('ortho2020'))
w,h=img.size; px=np.empty(w*h*4,np.float32); img.pixels.foreach_get(px); px=px.reshape(h,w,4)
def uv(x,y): return np.array([x,y,1.0])@A
def col(u,v):
    i=min(h-1,max(0,int(v*h))); j=min(w-1,max(0,int(u*w))); return px[i,j,:3]
def green(c): return c[1]>c[0]*1.04 and c[1]>c[2]*1.06
ap=bpy.data.objects['CCOM_dock_apron_20261014jf3']; am=ap.matrix_world
ac=sum((am@v.co for v in ap.data.vertices),Vector())/len(ap.data.vertices)
stats={}
for name in ['WS226_CCOM_dock_apron_lawn_shoulder_UNVERIFIED','WS240_CCOM_apron_S_corner_lawn_bank_UNVERIFIED']:
    o=bpy.data.objects.get(name)
    if not o: continue
    d=o.data; L=d.uv_layers.get('ortho') or d.uv_layers.new(name='ortho'); d.uv_layers.active=L
    om=o.matrix_world; ok=fb=0; cache={}
    for lp in d.loops:
        vi=lp.vertex_index
        if vi not in cache:
            p=om@d.vertices[vi].co; dr=Vector((p.x-ac.x,p.y-ac.y,0)).normalized(); got=None
            for dist in np.arange(1.5,6.01,0.5):
                q=p+dr*float(dist); u=uv(q.x,q.y)
                if green(col(*u)): got=u; break
            if got is None: got=uv(p.x+dr.x*3,p.y+dr.y*3); fb+=1
            else: ok+=1
            cache[vi]=got
        L.data[lp.index].uv=tuple(cache[vi])
    stats[name[:30]]=(ok,fb)
print('F240C uv set',stats,flush=True)
