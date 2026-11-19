# ws236 W53q gap: the main-native grounds stop ~1 m short of M3b (M3b was cut to never stack on them), so after the feather a
# 0.5-1.5 m slot shows the skirt (held 0.35 m under) as a dark line. Extrude each target's SEAM boundary edges out to the nearest
# M3b boundary + 0.6 m overlap, new verts at M3b z - 0.04 (tucked under the LiDAR surface where they overlap). Ground only.
import bpy, bmesh, mathutils, os
from mathutils.kdtree import KDTree
M=bpy.data.objects['M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam']
mb=bmesh.new(); mb.from_mesh(M.data); mb.transform(M.matrix_world)
mbd=[v.co.copy() for v in mb.verts if v.is_boundary]
K=KDTree(len(mbd))
for i,c in enumerate(mbd): K.insert((c.x,c.y,0),i)
K.balance()
from mathutils.bvhtree import BVHTree
MT=BVHTree.FromBMesh(mb)
names=['PK_Feliciano_west_DTM_fill_UNVERIFIED','WS60_terrain_edge_apron_LiDAR_to_skirt']+[o.name for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground_northDTM')]
for n in names:
    o=bpy.data.objects[n]; mw=o.matrix_world; mi=mw.inverted()
    bm=bmesh.new(); bm.from_mesh(o.data)
    uv=bm.loops.layers.uv.active
    seam=set()
    for v in bm.verts:
        if not v.is_boundary: continue
        c=mw@v.co; d=K.find((c.x,c.y,0))
        if d[2]<=3: seam.add(v)
    edges=[e for e in bm.edges if e.is_boundary and e.verts[0] in seam and e.verts[1] in seam]
    res=bmesh.ops.extrude_edge_only(bm,edges=edges)
    nv=[g for g in res['geom'] if isinstance(g,bmesh.types.BMVert)]
    nf=set()
    for g in res['geom']:
        if isinstance(g,bmesh.types.BMEdge):
            for f in g.link_faces: nf.add(f)
    # map new vert -> its source (the extrude keeps order: connect via edges)
    mx=0
    for v in nv:
        src=[e.other_vert(v) for e in v.link_edges if e.other_vert(v) in seam]
        c=mw@v.co
        _,i,d=K.find((c.x,c.y,0))
        t=mbd[i]; dv=mathutils.Vector((t.x-c.x,t.y-c.y))
        L=dv.length
        if L<1e-4: continue
        p=mathutils.Vector((c.x,c.y))+dv*((L+0.6)/L)
        h=MT.ray_cast(mathutils.Vector((p.x,p.y,c.z+60)),mathutils.Vector((0,0,-1)),200)
        z=(h[0].z if h[0] else t.z)-0.04
        v.co=mi@mathutils.Vector((p.x,p.y,z)); mx=max(mx,L+0.6)
    if uv:
        for f in nf:
            for l in f.loops:
                if l.vert in nv:
                    s=[e.other_vert(l.vert) for e in l.vert.link_edges if e.other_vert(l.vert) in seam]
                    if s:
                        for l2 in s[0].link_loops:
                            if l2.face not in nf: l[uv].uv=l2[uv].uv.copy(); break
    if nf:
        mat=[f.material_index for f in bm.faces if f not in nf]
        mi0=max(set(mat),key=mat.count) if mat else 0
        for f in nf: f.material_index=mi0
    bmesh.ops.recalc_face_normals(bm,faces=list(nf))
    for f in nf:
        if f.normal.z<0: f.normal_flip()
    bm.to_mesh(o.data); o.data.update()
    print('F236C',n[:40],'seam verts',len(seam),'edges',len(edges),'new faces',len(nf),'max reach',round(mx,2),flush=True)
