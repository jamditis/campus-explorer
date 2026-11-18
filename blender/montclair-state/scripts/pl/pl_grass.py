# pl: grass clump scatter on the lawn N and W of Feliciano (PK west DTM fill + LiDAR DTM), where the ortho grass reads pale.
# Removable: REVERT=1 deletes collection PL_feliciano_lawn_grass_20261101pl. Static points; instanced with the existing
# cx_grass node group (Main_grass_cx_clumps). UNVERIFIED (density/coverage a style guess; no photo of this lawn).
import bpy, os, sys, random, math
from mathutils import Vector
COL='PL_feliciano_lawn_grass_20261101pl'; OBN='PL_feliciano_lawn_grass_points_UNVERIFIED'
D=float(os.environ.get('D','16')); MARG=float(os.environ.get('MARG','28')); SEED=int(os.environ.get('SEED','1113'))
c=bpy.data.collections.get(COL)
if c:
    for o in list(c.objects): bpy.data.objects.remove(o)
    bpy.data.collections.remove(c)
for me in [m for m in bpy.data.meshes if m.name.startswith(OBN) and m.users==0]: bpy.data.meshes.remove(me)
if os.environ.get('REVERT')!='1':
    rnd=random.Random(SEED); dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
    grounds=[bpy.data.objects[n].evaluated_get(dg) for n in ('Terrain_LiDAR_DTM_1m','PK_Feliciano_west_DTM_fill_UNVERIFIED')]
    blk=[bpy.data.objects[n].evaluated_get(dg) for n in ('Footpaths_OSM','Roads_OSM','Feliciano School of Business roof (LiDAR)')]
    x0,x1,y0,y1=-258.8,-191.9,166.3,222.2
    def gz(x,y):
        hz=None
        for o in grounds:
            mi=o.matrix_world.inverted(); org=mi@Vector((x,y,400)); dr=(mi.to_3x3()@Vector((0,0,-1))).normalized()
            r=o.ray_cast(org,dr)
            if r[0]:
                z=(o.matrix_world@r[1]).z
                if hz is None or z>hz: hz=z
        return hz
    def blocked(x,y,z):
        for o in blk:
            mi=o.matrix_world.inverted(); org=mi@Vector((x,y,400)); dr=(mi.to_3x3()@Vector((0,0,-1))).normalized()
            r=o.ray_cast(org,dr)
            if r[0] and (o.matrix_world@r[1]).z>z-0.05: return True
        return False
    X0,X1,Y0,Y1=x0-MARG,x1,y0-6,y1+MARG
    area=(X1-X0)*(Y1-Y0); n=int(area*D); pts=[]; nb=nn=0
    for _ in range(n):
        x=rnd.uniform(X0,X1); y=rnd.uniform(Y0,Y1)
        if not (x<x0+18 or y>y1-10): continue   # N and W sides only
        # distance from bbox for a soft outer fade
        dx=max(x0-x,0,x-x1); dy=max(y0-y,0,y-y1); d=math.hypot(dx,dy)
        if d>MARG or rnd.random()>1-(d/MARG)**2: continue
        z=gz(x,y)
        if z is None: nn+=1; continue
        if blocked(x,y,z): nb+=1; continue
        pts.append((x,y,z-0.005))
    me=bpy.data.meshes.new(OBN); me.from_pydata(pts,[],[])
    ob=bpy.data.objects.new(OBN,me); c=bpy.data.collections.new(COL); sc.collection.children.link(c); c.objects.link(ob)
    src=bpy.data.objects['cx_grass_points'].modifiers['cx_grass']
    m=ob.modifiers.new('cx_grass','NODES'); m.node_group=src.node_group
    ob['UNVERIFIED_pl_grass']='D=%.1f MARG=%.1f SEED=%d'%(D,MARG,SEED)
    print('PLGRASS pts',len(pts),'blocked',nb,'noground',nn)
else: print('REVERTED_PLGRASS')
if os.environ.get('SAVEAS'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['SAVEAS'],copy=True); print('SAVED_AS')
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')
