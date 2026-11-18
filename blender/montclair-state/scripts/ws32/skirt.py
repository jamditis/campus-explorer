# ws32 skirt: the apron's east/south-east edge stood 0.1–0.4 m over the new embankment with no side face (read as a black gap).
# Add a concrete edge face from the apron edge down to 8 cm below the terrain.
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
if 'WS32_CCOM_apron_east_edge_skirt' not in bpy.data.objects:
    dg=bpy.context.evaluated_depsgraph_get(); dg.update(); D=Vector((0,0,-1))
    ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']; e=ter.evaluated_get(dg); m=e.to_mesh(); b=bmesh.new(); b.from_mesh(m); b.transform(ter.matrix_world); e.to_mesh_clear(); TB=BVHTree.FromBMesh(b); b.free()
    ap=bpy.data.objects['CCOM_dock_apron_20261014jf3']; ab=bmesh.new(); ab.from_mesh(ap.data); ab.transform(ap.matrix_world)
    out=bmesh.new(); k=0
    for ed in ab.edges:
        if not ed.is_boundary: continue
        a,c=ed.verts[0].co,ed.verts[1].co; mid=(a+c)/2
        if mid.x<10.5: continue
        # skip edges against CCOM wall (north side)
        if mid.y>-22.5: continue
        za=TB.ray_cast(Vector((a.x,a.y,a.z+3)),D,10); zc=TB.ray_cast(Vector((c.x,c.y,c.z+3)),D,10)
        # sample terrain slightly outside the edge
        f=ed.link_faces[0].calc_center_median(); nrm=(mid-f); nrm.z=0; nrm.normalize()
        ta=TB.ray_cast(Vector((a.x,a.y,a.z+3))+nrm*0.3,D,10); tc=TB.ray_cast(Vector((c.x,c.y,c.z+3))+nrm*0.3,D,10)
        if ta[0] is None or tc[0] is None: continue
        if min(a.z-ta[0].z,c.z-tc[0].z)<0.03: continue
        v1=out.verts.new(a-Vector((0,0,0.002))+nrm*0.01); v2=out.verts.new(c-Vector((0,0,0.002))+nrm*0.01)
        v3=out.verts.new(Vector((c.x,c.y,tc[0].z-0.08))+nrm*0.01); v4=out.verts.new(Vector((a.x,a.y,ta[0].z-0.08))+nrm*0.01)
        out.faces.new((v1,v2,v3,v4)); k+=1
    me=bpy.data.meshes.new('WS32_CCOM_apron_east_edge_skirt'); out.to_mesh(me); out.free(); ab.free()
    me.materials.append(bpy.data.materials['CCOM_dock_concrete_20261014jf3'])
    o=bpy.data.objects.new('WS32_CCOM_apron_east_edge_skirt',me)
    (ap.users_collection[0] if ap.users_collection else bpy.context.scene.collection).objects.link(o)
    print('skirt faces',k)
