# ws131 self-review fixes: (1) lawn S of the facade band lifted to meet the band edge (no reveal/dip);
# (2) ground E of the W-foot mulch bed (under the unmodelled E building footprint) raised to the bed edge (no 0.4 m cliff);
# (3) Footpaths_OSM / OZ joint faces S of the bed edge y -243.7 in x -190..-179 (floating slab on the lot) retired.
import bpy, bmesh, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
yS=lambda x:-229.4-0.22*(x+213.0)
band=[o for o in bpy.data.objects if o.name.startswith('WS131_Chapin_S_facade_concrete_edge_band')][0]
bedm=[o for o in bpy.data.objects if o.name.startswith('WS131_E_building_W_foot_mulch_bed')][0]
def bvh(o): return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[p.vertices for p in o.data.polygons if p.normal.z>0.5])
TB=bvh(band); TM=bvh(bedm)
def ztop(T,x,y):
    h=T.ray_cast(Vector((x,y,200)),Vector((0,0,-1))); return None if h[0] is None else h[0].z
n1=n2=0
for g in [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill','WS110_ground_patch'))]:
    gw=g.matrix_world; gi=gw.inverted()
    for v in g.data.vertices:
        p=gw@v.co
        if -214.4<p.x<-200.3:
            d=yS(p.x)-p.y
            if 0.0<d<1.2:
                ze=ztop(TB,p.x,yS(p.x)+0.05)
                if ze is not None:
                    w=1-d/1.2; zt=ze-0.02
                    nz=p.z*(1-w)+zt*w if d>0.15 else zt
                    if abs(nz-p.z)>0.005: p.z=nz; v.co=gi@p; n1+=1
        if -175.6<p.x<-169.0 and -251.7<p.y<-243.0:
            ze=ztop(TM,-175.6,min(max(p.y,-251.5),-243.8))
            if ze is not None:
                zt=ze-0.03-0.02*(p.x+175.6)
                if p.z<zt: p.z=zt; v.co=gi@p; n2+=1
    g.data.update()
print('M131c lawn lifted at band',n1,'ground raised E of bed',n2)
for nm in ('Footpaths_OSM','OZ_walk_joints_auto_GN_UNVERIFIED'):
    ro=bpy.data.objects.get(nm)
    if not ro or ro.type!='MESH': continue
    rb=bmesh.new(); rb.from_mesh(ro.data); rw=ro.matrix_world
    k=[f for f in rb.faces if (lambda c:-190<c.x<-179 and -256.5<c.y<-243.7)(rw@f.calc_center_median())]
    bmesh.ops.delete(rb,geom=k,context='FACES'); rb.to_mesh(ro.data); rb.free(); ro.data.update(); print('M131c retired',nm,len(k))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('M131c SAVED')
