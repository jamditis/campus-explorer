# ws239 read-only: PK/M3b seam geometry. M3b boundary (free-edge) verts within 3 m of the strips: vertical gap to the strip
# surface below/above (base meshes), and verts with no strip under them (horizontal gap). Also list modifiers.
import bpy, bmesh, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects
M=O['M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam']
S=['PK_Feliciano_west_DTM_fill_UNVERIFIED','WS60_terrain_edge_apron_LiDAR_to_skirt']+[o.name for o in O if o.name.startswith('WS68_RHD_ground_northDTM')]
for n in [M.name]+S: print('P239B MODS',n[:40],[(m.name,m.type,m.show_render) for m in O[n].modifiers],len(O[n].data.vertices),flush=True)
def bvh(o):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); return t
T={n:bvh(O[n]) for n in S}
bm=bmesh.new(); bm.from_mesh(M.data); bm.transform(M.matrix_world)
bv=[v for v in bm.verts if any(e.is_boundary for e in v.link_edges)]
stats={}; miss=0; near=0; gaps=[]
for v in bv:
    best=None
    for n,t in T.items():
        for d in (Vector((0,0,-1)),Vector((0,0,1))):
            h=t.ray_cast(v.co+Vector((0,0,0))-d*0.0,d,3.0)
            if h[0] is not None and (best is None or abs(h[0].z-v.co.z)<abs(best[1])): best=(n,h[0].z-v.co.z)
    # nearest horizontal distance to any strip
    dn=min(t.find_nearest(v.co)[3] for t in T.values())
    if dn>3: continue
    near+=1
    if best is None: miss+=1; gaps.append((round(v.co.x,1),round(v.co.y,1),round(dn,2)))
    else:
        k=best[0][:6]; stats.setdefault(k,[]).append(best[1])
print('P239B boundary verts',len(bv),'within3m',near,'no strip above/below',miss,flush=True)
for k,l in stats.items():
    l.sort(); print('P239B',k,'n',len(l),'dz(strip-M3b) min %.4f med %.4f max %.4f'%(l[0],l[len(l)//2],l[-1]),flush=True)
print('P239B gaps sample',gaps[:30],flush=True)
os._exit(0)
