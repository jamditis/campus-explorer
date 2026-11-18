# pn: raster the Feliciano LiDAR roof top (max hit z) on a building-aligned 0.5 m grid via downward rays.
import bpy, numpy as np, json, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
d=json.load(open('data/pn/feli.json'))
ang=[]
for f in d['walls']:
    b=sorted(f,key=lambda v:v[2])[:2]; ang.append(math.degrees(math.atan2(b[1][1]-b[0][1],b[1][0]-b[0][0]))%90)
th=math.radians(float(np.median(ang))-90)   # rotation of building axes
V=[Vector(v) for v in d['V']]; tree=BVHTree.FromPolygons(V,d['F'])
c,s=math.cos(th),math.sin(th); cx,cy=-225.3,194.2
pts=np.array(d['V'])[:,:2]-[cx,cy]; u=pts@[c,s]; v=pts@[-s,c]
R=0.5; u0,u1=u.min()-1,u.max()+1; v0,v1=v.min()-1,v.max()+1
nu=int((u1-u0)/R)+1; nv=int((v1-v0)/R)+1
Z=np.full((nv,nu),np.nan); MI=np.full((nv,nu),-1)
for j in range(nv):
    for i in range(nu):
        uu=u0+(i+.5)*R; vv=v0+(j+.5)*R
        x=cx+uu*c-vv*s; y=cy+uu*s+vv*c
        h=tree.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),100)
        if h[0] is not None: Z[j,i]=h[0].z; MI[j,i]=d['M'][h[2]]
np.savez('data/pn/raster.npz',Z=Z,MI=MI,th=th,cx=cx,cy=cy,u0=u0,v0=v0,R=R)
print('RASTER',nu,nv,np.degrees(th),np.nanmin(Z),np.nanmax(Z))
