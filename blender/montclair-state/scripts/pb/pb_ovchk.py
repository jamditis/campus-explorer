# dz of the evaluated terrain (pb modifier) under static overlay/skirt objects; also lists ground-seated objects in the box
import bpy, numpy as np, sys
from mathutils.bvhtree import BVHTree
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
b0=BVHTree.FromObject(T,dg,deform=False) if False else None
m=T.modifiers['PB_terrain_fan_regrid']; m.show_viewport=False; dg.update(); b0=BVHTree.FromObject(T,bpy.context.evaluated_depsgraph_get())
m.show_viewport=True; dg=bpy.context.evaluated_depsgraph_get(); dg.update(); b1=BVHTree.FromObject(T,dg)
def dz(x,y):
    h0=b0.ray_cast(Vector((x,y,400)),Vector((0,0,-1))); h1=b1.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
    if h0[0] is None or h1[0] is None: return None,None
    return h1[0].z-h0[0].z, h0[0].z
PFX=('OW3_','OX_','OY_','OV_','OR_base','OO_','OW_basefix','OL_','OK_','OT_','OS_')
for c in bpy.data.collections:
    if not c.name.startswith(PFX): continue
    for o in c.objects:
        if o.type!='MESH': continue
        mw=o.matrix_world; vs=o.data.vertices; n=len(vs); idx=range(0,n,max(1,n//1500)); mx=0
        for i in idx:
            p=mw@vs[i].co
            if not(78<p.x<207 and 118<p.y<264): continue
            d,z0=dz(p.x,p.y)
            if d is not None and abs(p.z-z0)<1.0: mx=max(mx,abs(d))
        if mx>0.005: print('PBV %-60s max|dz| %.3f'%(o.name[:60],mx))
for o in bpy.data.objects:
    if o.parent or o.type not in ('MESH','EMPTY','CURVES'): continue
    p=o.matrix_world.translation
    if 78<p.x<207 and 118<p.y<264:
        d,z0=dz(p.x,p.y)
        if d is not None and abs(p.z-z0)<3.0 and abs(d)>0.01: print('PBG %-50s z-ground %.2f dz %.3f'%(o.name[:50],p.z-z0,d))
