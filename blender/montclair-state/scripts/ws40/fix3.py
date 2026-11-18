import bpy,bmesh,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get(); O=bpy.data.objects
def bvh(names):
    bm=bmesh.new()
    for n in names:
        o=O[n]; e=o.evaluated_get(dg); me=e.to_mesh(); t=bmesh.new(); t.from_mesh(me); t.transform(o.matrix_world)
        m2=bpy.data.meshes.new('t'); t.to_mesh(m2); bm.from_mesh(m2); bpy.data.meshes.remove(m2); t.free(); e.to_mesh_clear()
    r=BVHTree.FromBMesh(bm); bm.free(); return r
TR=bvh(['WS27_CollegeAve_carriageway_2020ortho','WS27_CollegeAve_curb_left_UNVERIFIED','WS27_CollegeAve_curb_right_UNVERIFIED','WS40_CollegeAve_east_sidewalk_to_Kasser_steps_concrete_OSM_JOE'])
def road_z(x,y):
    r=TR.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),400); return r[0].z if r[0] else None
# Footpaths faces (evaluated positions differ from original because of redrape GN) -> test on original xy only
o=O['Footpaths_OSM']; m=o.matrix_world; bm=bmesh.new(); bm.from_mesh(o.data); kill=[]
for f in bm.faces:
    c=m@f.calc_center_median()
    if -204<c.x<-186 and -108<c.y<-80 and road_z(c.x,c.y) is not None: kill.append(f)
bmesh.ops.delete(bm,geom=kill,context='FACES'); bm.to_mesh(o.data); bm.free(); o.data.update(); print('F40c footpath faces over road/sidewalk',len(kill))
for g in list(O):
    if g.type!='MESH' or g.library or not any(k in g.name.lower() for k in ('grass','lawn')): continue
    mw=g.matrix_world; ob=[mw@Vector(cc) for cc in g.bound_box]
    if max(q.x for q in ob)<-204 or min(q.x for q in ob)>-186 or max(q.y for q in ob)<-108 or min(q.y for q in ob)>-80: continue
    if len(g.data.vertices)>300000: continue
    bm=bmesh.new(); bm.from_mesh(g.data); kill=[]
    for v in bm.verts:
        p=mw@v.co
        if -204<p.x<-186 and -108<p.y<-80:
            z=road_z(p.x,p.y)
            if z is not None and p.z<z+0.6: kill.append(v)
    bmesh.ops.delete(bm,geom=kill,context='VERTS'); bm.to_mesh(g.data); bm.free(); g.data.update(); print('F40c grass under road/sidewalk',g.name,len(kill))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('F40c SAVED')
