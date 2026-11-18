# oo: wall skirts from the open bottom edge of floating context-building walls down to the LiDAR DTM (-0.3 m), same plane
# and material as the wall face above. Buildings: CCIS, CELS, Speech, Calcia, Memorial (probe data/oo/walls_float.txt).
# OSM wall meshes NOT edited. UNVERIFIED (plain wall, no lower-storey windows). REVERT=1 removes the collection.
import bpy, bmesh, os, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
CN='OO_context_wall_skirts_to_LiDAR_20261031oo'
B=['Center for Computing and Information Science walls','Center for Environmental and Life Sciences walls','Speech Building walls','Calcia Hall walls','Memorial Auditorium walls']
c=bpy.data.collections.get(CN)
if c:
    for ob in list(c.objects):
        me=ob.data; bpy.data.objects.remove(ob)
        if me and me.users==0: bpy.data.meshes.remove(me)
    bpy.data.collections.remove(c)
if REV:
    print('REVERTED')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']; dg=bpy.context.evaluated_depsgraph_get(); te=ter.evaluated_get(dg); bt=bmesh.new(); bt.from_mesh(te.to_mesh()); bt.transform(ter.matrix_world); t=BVHTree.FromBMesh(bt)
def tz(x,y):
    h=t.ray_cast(Vector((x,y,400)),Vector((0,0,-1))); return h[0].z if h[0] else None
col=bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(col)
for name in B:
    o=bpy.data.objects.get(name)
    if not o: print('MISSING',name); continue
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world)
    def isbottom(e):
        a,b=e.verts
        if abs(a.co.z-b.co.z)>0.5: return False
        fs=[f for f in e.link_faces if abs(f.normal.z)<0.5]
        if not fs: return False
        return all(f.calc_center_median().z>max(a.co.z,b.co.z)+0.05 for f in fs) and (e.is_boundary or any(f.normal.z<-0.7 for f in e.link_faces))
    cand=[e for e in bm.edges if isbottom(e)]; mode='bottom-edges'
    out=bmesh.new(); uvl=out.loops.layers.uv.new('UVMap'); n=0; mats=[]
    for e in set(cand):
        a,b=[v.co.copy() for v in e.verts]
        ta,tb=tz(a.x,a.y),tz(b.x,b.y)
        if ta is None or tb is None: continue
        ba,bb=ta-0.3,tb-0.3
        if a.z-ba<0.1 and b.z-bb<0.1: continue
        side=[f for f in e.link_faces if abs(f.normal.z)<0.5]
        if not side: continue
        f0=side[0]
        mi=f0.material_index
        if mi not in mats: mats.append(mi)
        vs=[out.verts.new(a),out.verts.new(b),out.verts.new((b.x,b.y,min(bb,b.z))),out.verts.new((a.x,a.y,min(ba,a.z)))]
        fn=out.faces.new(vs); fn.material_index=mats.index(mi)
        # orient like the wall face
        fn.normal_update()
        if fn.normal.dot(f0.normal)<0: fn.normal_flip()
        ln=(b-a).length
        for lp in fn.loops:
            p=lp.vert.co; s=(p-a).xy.length
            lp[uvl].uv=(s/3.0,p.z/3.0)
        n+=1
    if n==0: print('NOSKIRT',name,mode); continue
    me=bpy.data.meshes.new('OO_skirt_'+name[:40]); out.to_mesh(me)
    for mi in mats: me.materials.append(o.material_slots[mi].material if mi<len(o.material_slots) else None)
    ob=bpy.data.objects.new(('OO_skirt_'+name)[:60],me); col.objects.link(ob); ob['UNVERIFIED']='oo: wall carried down to LiDAR DTM; lower storey unverified'
    print('SKIRT',name,mode,'faces',n,'mats',[m.name if m else None for m in me.materials])
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
