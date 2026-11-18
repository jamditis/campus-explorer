# Session eh (Oct 21 2026 ~9:25 PM ET): eg left the planar forecourt up to ~20 cm proud of the lawn along its south/SE edge
# (reads as a brick curb in the closeF/eyeW WIPs). Real forecourt edges at CCOM's west entrance are most likely near-flush
# (UNVERIFIED), so ease terrain + lawn grass up in a wider, gentler apron: within 3.5 m outside the paving edge,
# z >= edge_z - 0.02 - 0.055*d (only raises). Grass within 0.25 m of the edge stays sunk (ed rule, no poke-through).
# Pre-ramp z in point attribute eh_orig_z. SAVE=1 saves; REVERT=1 restores.
import bpy, os, re, bmesh, mathutils
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'; SAVE=os.environ.get('SAVE')=='1'; R=float(os.environ.get('RAMP_M','3.5')); K=float(os.environ.get('RAMP_K','0.055'))
fc=bpy.data.objects['CCOM brick forecourt (ortho + photo)']; me=fc.data; mw=fc.matrix_world
b=bmesh.new(); b.from_mesh(me); b.transform(mw); bvh=BVHTree.FromBMesh(b)
bnd=[(e.verts[0].co.copy(),e.verts[1].co.copy()) for e in b.edges if e.is_boundary]
xs=[v.co.x for v in b.verts]; ys=[v.co.y for v in b.verts]
def edge(p):
    best=(1e9,None)
    for a_,b_ in bnd:
        a2=a_.xy; b2=b_.xy; ab=b2-a2; t=max(0,min(1,(p.xy-a2).dot(ab)/ab.length_squared)); q=a2+ab*t
        d=(p.xy-q).length
        if d<best[0]: best=(d,a_.z+(b_.z-a_.z)*t)
    return best
# keep the ramp off building footprints: skip points under any CCOM/Life Hall wall mesh (ray up hits nothing we care about); use a
# simple guard: never raise terrain more than 0.25 m
objs=[bpy.data.objects['Terrain_LiDAR_DTM_1m']]+[o for o in bpy.data.objects if o.type=='MESH' and re.match(r'(?i)^(dS_grass|cx_grass|cd_grass|Lawn_grass_instanced)',o.name)]
tot=0
for o in objs:
    m=o.data; ow=o.matrix_world; oi=ow.inverted(); grass=o.name!='Terrain_LiDAR_DTM_1m'
    at=m.attributes.get('eh_orig_z')
    if REV:
        if at:
            for v,d in zip(m.vertices,at.data):
                if d.value>-9000: v.co.z=d.value
            m.attributes.remove(at); m.update(); print('EH_REVERT',o.name)
        continue
    if at is None:
        at=m.attributes.new('eh_orig_z','FLOAT','POINT'); at.data.foreach_set('value',[-9999.0]*len(m.vertices))
    n=0; mx=0
    for i,v in enumerate(m.vertices):
        w=ow@v.co
        if not (min(xs)-R-0.1<w.x<max(xs)+R+0.1 and min(ys)-R-0.1<w.y<max(ys)+R+0.1): continue
        if bvh.ray_cast(mathutils.Vector((w.x,w.y,w.z+30)),mathutils.Vector((0,0,-1)))[0] is not None: continue
        d,ez=edge(w)
        if d>R or (grass and d<0.25): continue
        base=at.data[i].value if at.data[i].value>-9000 else w.z
        zf=max(base, ez-0.02-K*d); zf=min(zf, base+0.25)
        if zf-w.z>1e-4:
            if at.data[i].value<-9000: at.data[i].value=w.z
            mx=max(mx,zf-w.z); v.co.z=(oi@mathutils.Vector((w.x,w.y,zf))).z; n+=1
    m.update(); tot+=n; print('EH_RAMP',o.name,'raised',n,'max',round(mx,3))
if not REV:
    ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tb=bmesh.new(); tb.from_mesh(ter.data); tb.transform(ter.matrix_world); tv=BVHTree.FromBMesh(tb)
    c=sum((v.co for v in b.verts),mathutils.Vector())/len(b.verts)
    for off in (0.3,1.0,2.0):
        st=[]
        for v in b.verts:
            if not v.is_boundary: continue
            dd=(v.co-c); dd.z=0; dd.normalize(); q=v.co+dd*off
            h=tv.ray_cast(mathutils.Vector((q.x,q.y,200)),mathutils.Vector((0,0,-1)))
            if h[0]: st.append((round(h[0].z-v.co.z,3),round(v.co.x,1),round(v.co.y,1)))
        st.sort(); print('EH_STEP off',off,'terrain-paving min',st[0],'max',st[-1])
    # material probe for paving bump
    for s in fc.material_slots:
        mt=s.material; print('EH_MAT',mt.name if mt else None)
        if mt and mt.use_nodes: print('  nodes',[n.bl_idname+':'+n.name for n in mt.node_tree.nodes])
if SAVE: bpy.ops.wm.save_mainfile(); print('EH_SAVED')
