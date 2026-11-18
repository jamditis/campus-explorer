# oh: hide the floating Footpaths_OSM slab look at the Schmitt ESE entrance WITHOUT editing the OSM plane:
# new object = vertical concrete cheek/retaining wall skirts from the slab's open boundary edges (near the entrance)
# down to LiDAR terrain where the slab floats > 0.12 m. UNVERIFIED (no photo of this spot). REVERT=1 removes.
import bpy, bmesh, os, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
NAME='OH_Schmitt_entrance_walk_cheek_wall_UNVERIFIED'; MN='OH_cheek_wall_concrete_UNVERIFIED'
REV=os.environ.get('REVERT')=='1'
o=bpy.data.objects.get(NAME)
if o: me=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(me)
if REV:
    m=bpy.data.materials.get(MN)
    if m: bpy.data.materials.remove(m)
else:
    C=Vector((10.6,141.1)); R=float(os.environ.get('R','16'))
    fp=bpy.data.objects['Footpaths_OSM']; ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']
    dg=bpy.context.evaluated_depsgraph_get()
    te=ter.evaluated_get(dg); bt=bmesh.new(); bt.from_mesh(te.to_mesh()); bt.transform(ter.matrix_world)
    tree=BVHTree.FromBMesh(bt)
    bm=bmesh.new(); bm.from_mesh(fp.data); bm.transform(fp.matrix_world)
    out=bmesh.new(); n=0; mx=0
    for e in bm.edges:
        if not e.is_boundary: continue
        a,b=e.verts[0].co.copy(),e.verts[1].co.copy()
        if (a.xy-C).length>R and (b.xy-C).length>R: continue
        za=[];ok=True
        for v in (a,b):
            h=tree.ray_cast(v+Vector((0,0,30)),Vector((0,0,-1)))
            if h[0] is None: ok=False; break
            za.append(h[0].z)
        if not ok: continue
        if max(a.z-za[0],b.z-za[1])<0.12: continue
        mx=max(mx,a.z-za[0],b.z-za[1])
        vs=[out.verts.new((a.x,a.y,a.z-0.005)),out.verts.new((b.x,b.y,b.z-0.005)),out.verts.new((b.x,b.y,za[1]-0.25)),out.verts.new((a.x,a.y,za[0]-0.25))]
        out.faces.new(vs); n+=1
    me=bpy.data.meshes.new(NAME); out.to_mesh(me)
    o=bpy.data.objects.new(NAME,me); bpy.data.collections['OH_Schmitt_cams_20261031oh'].objects.link(o)
    m=bpy.data.materials.get(MN) or bpy.data.materials.new(MN); m.use_nodes=True
    p=m.node_tree.nodes['Principled BSDF']; p.inputs['Base Color'].default_value=(0.36,0.355,0.34,1); p.inputs['Roughness'].default_value=0.85
    me.materials.append(m)
    for f in me.polygons: f.use_smooth=False
    print('cheek faces',n,'max float',round(mx,2))
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')
