# pi (C): Feliciano east-facing base course / water table: 0.07 m proud cast-stone band from 0.25 m below to 0.75 m above
# the LiDAR grade along every east-facing (outward n.x>0.5, outward = away from the footprint centre since normals are mixed) vertical wall face that reaches the ground. Height/material UNVERIFIED
# (style-matched to the pavilion's North_Feliciano_caststone_tan). REVERT=1 deletes the object.
import bpy,bmesh,os,sys
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; ON='PI_Feliciano_east_base_course_UNVERIFIED'
if ON in bpy.data.objects:
    o=bpy.data.objects[ON]; me=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(me)
if not REV:
    s=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
    w=bpy.data.objects['Feliciano School of Business walls']; mw=w.matrix_world; R=mw.to_3x3()
    bm=bmesh.new(); n_ok=0
    ws=[mw@v.co for v in w.data.vertices]; C=Vector(((min(v.x for v in ws)+max(v.x for v in ws))/2,(min(v.y for v in ws)+max(v.y for v in ws))/2,0))
    def ground(p):
        hit,loc,nor,i,ob,_=s.ray_cast(dg,Vector((p.x,p.y,p.z+3)),Vector((0,0,-1)))
        return loc.z if hit else None
    for p in w.data.polygons:
        n=(R@p.normal).normalized(); pc=mw@p.center
        if abs(n.z)>0.2: continue
        if Vector((n.x,n.y,0)).dot(Vector((pc.x-C.x,pc.y-C.y,0)))<0: n=-n   # many faces have inward normals
        if n.x<0.5: continue
        vs=sorted([mw@w.data.vertices[v].co for v in p.vertices],key=lambda v:v.z)
        a,b=vs[0],vs[1]
        if (a-b).length<0.3 or abs(a.z-b.z)>1.0: continue
        nh=Vector((n.x,n.y,0)).normalized()
        ga=ground(a+nh*0.6); gb=ground(b+nh*0.6)
        if ga is None or gb is None or ga-a.z>3 or max(ga,gb)-min(a.z,b.z)>4: continue
        n_ok+=1
        z0a,z0b=ga-0.25,gb-0.25; z1=max(ga,gb)+0.75
        ao=a+nh*0.07; bo=b+nh*0.07
        V=[bm.verts.new((ao.x,ao.y,z0a)),bm.verts.new((bo.x,bo.y,z0b)),bm.verts.new((bo.x,bo.y,z1)),bm.verts.new((ao.x,ao.y,z1)),
           bm.verts.new((b.x,b.y,z1)),bm.verts.new((a.x,a.y,z1))]
        bm.faces.new((V[0],V[1],V[2],V[3])); bm.faces.new((V[3],V[2],V[4],V[5]))
    bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.01)
    me=bpy.data.meshes.new(ON); bm.to_mesh(me); bm.free()
    o=bpy.data.objects.new(ON,me); w.users_collection[0].objects.link(o)
    me.materials.append(bpy.data.materials['North_Feliciano_caststone_tan'])
    o['UNVERIFIED']='base course height 0.75 m, projection 7 cm, material style-matched; no photo of the east base'
    print('PI_BASE faces',n_ok,len(me.polygons))
if '--save' in sys.argv: bpy.ops.wm.save_mainfile()
print('PI_BASE_DONE',REV,len(bpy.data.objects))
