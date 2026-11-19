# W53j (ws230): north of y ~40 the QI LiDAR patch's east boundary steps diagonally from x 240 (y 28) to x 217 (y 248),
# but the WS60 apron starts at x 246: probe230e (evaluated terrain + apron rays) found NO ground in between (a wedge-shaped
# hole, up to ~29 m wide, through which the lower skirt shows), and the W53i strip's inner column (x 246) had fallen back to
# the edge-PADDED dtm_1m (constant rows), standing 1-8 m over USGS 3DEP 1 m (fetched ws230, scripts/ws230/url_3dep1m_full.txt;
# 3DEP matches dtm_1m within ~0.1 m wherever dtm_1m is real, checked at 60 points). Fix, terrain only (no paving here):
#  (1) WS60 strip verts in x 246..268.5, y >= -33.5 whose inner side has no terrain (gap) are set to 3DEP 1 m (bilinear);
#      the outer column (x 276, skirt top + 2 cm) is kept.
#  (2) QI patch boundary verts next to the gap that sit > 0.3 m UNDER 3DEP are raised to 3DEP (raise only).
#  (3) New WS230_NE_east_gap_fill_3DEP_UNVERIFIED: 1 m cells on the QI grid covering every gap cell (no evaluated terrain and
#      no apron at the cell centre) in x 200..246, y -40..262; verts shared with the QI patch take the QI vert z, verts on
#      x = 246 take the apron inner edge (linear between its rows, watertight), others 3DEP 1 m bilinear. Terrain material +
#      ortho UVs u = x/500 + 0.5, v = y/500 + 0.5. Cells covered by any other visible Terrain-collection mesh (the WN south-wood
#      patch north of y 228; the QJ NE seam fill is covered too and tucked 5 cm under it) are excluded; the 4 km skirt / beyond-data ground are the backdrop, not cover.
import bpy, bmesh, json
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
MS='/workspace/nj-scenes/montclair-state/'
P=np.load(MS+'scripts/ws230/dep1m_full_x-280_280_y-280_280_rowS.npy')
def p3(x,y):
    gx=x+280-0.5; gy=y+280-0.5; i=int(np.floor(gy)); j=int(np.floor(gx)); fy=gy-i; fx=gx-j
    return float(P[i,j]*(1-fx)*(1-fy)+P[i,j+1]*fx*(1-fy)+P[i+1,j]*(1-fx)*fy+P[i+1,j+1]*fx*fy)
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; TW=t.matrix_world
sv=[m.show_viewport for m in t.modifiers]
for m in t.modifiers: m.show_viewport=m.show_render
dg=bpy.context.evaluated_depsgraph_get(); e=t.evaluated_get(dg); tm=e.to_mesh()
BT=BVHTree.FromPolygons([TW@v.co for v in tm.vertices],[p.vertices[:] for p in tm.polygons]); e.to_mesh_clear()
for m,s in zip(t.modifiers,sv): m.show_viewport=s
ap=bpy.data.objects['WS60_terrain_edge_apron_LiDAR_to_skirt']; AW=ap.matrix_world; AI=AW.inverted(); am=ap.data
def BA():
    return BVHTree.FromPolygons([AW@v.co for v in am.vertices],[p.vertices[:] for p in am.polygons])
def ray(B,x,y):
    h=B.ray_cast(Vector((x,y,400)),Vector((0,0,-1))); return None if h[0] is None else h[0].z
B0=BA()
# other visible ground objects in the Terrain collection over the area (e.g. WN_south_wood_LiDAR_patch_ext_UNVERIFIED, y 228..292)
OB=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or o in (t,ap) or o.name.startswith(('QI_east_edge_delete','Context_skirt_3DEP','Context_ground_beyond')): continue
    if not any(c.name=='Terrain' for c in o.users_collection): continue
    W=o.matrix_world; vs=[W@v.co for v in o.data.vertices]
    if not vs or max(v.x for v in vs)<200 or min(v.x for v in vs)>246 or max(v.y for v in vs)<-40 or min(v.y for v in vs)>262: continue
    OB.append((o.name,BVHTree.FromPolygons(vs,[p.vertices[:] for p in o.data.polygons])))
print('F230A other ground objs',[n for n,_ in OB],flush=True)
# gap cells
gap=set(); cov={}
for x in range(200,246):
    for y in range(-40,262):
        if ray(BT,x+0.5,y+0.5) is None and ray(B0,x+0.5,y+0.5) is None:
            for n,b in OB:
                z=ray(b,x+0.5,y+0.5)
                if z is not None: cov.setdefault(n,[]).append((x,y,round(z-p3(x+0.5,y+0.5),2)))
for n,l in cov.items():
    dzs=[c[2] for c in l]
    print('F230A covered-by',n,len(l),'x',min(c[0] for c in l),max(c[0] for c in l),'y',min(c[1] for c in l),max(c[1] for c in l),'z-3dep',np.percentile(dzs,[0,50,100]).round(2).tolist(),flush=True)
for x in range(200,246):
    for y in range(-40,262):
        if ray(BT,x+0.5,y+0.5) is None and ray(B0,x+0.5,y+0.5) is None and all(ray(b,x+0.5,y+0.5) is None for n,b in OB if not n.startswith('QJ_')): gap.add((x,y))
# (1) strip re-height
COLS=(246.0,253.5,261.0,268.5); ch=[]
for v in am.vertices:
    w=AW@v.co
    if w.y<-33.6 or w.y>278.1: continue
    c=[k for k in COLS if abs(w.x-k)<0.02]
    if not c: continue
    if ray(BT,245.4,w.y) is not None and w.y<40: continue   # welded to the real terrain edge (ws228 part)
    z=p3(w.x,w.y)
    if abs(w.z-z)>0.05: ch.append(round(w.z-z,2)); w.z=z; v.co=AI@w
am.update(); B1=BA()
# (2) QI boundary verts next to the gap: raise only
qi=bpy.data.objects['QI_east_edge_LiDAR_terrain_patch']; QW=qi.matrix_world; QI=QW.inverted(); qm=qi.data
qv={}
for v in qm.vertices:
    w=QW@v.co; qv[(round(w.x,3),round(w.y,3))]=v
gv=set()
for x,y in gap:
    for p in ((x,y),(x+1,y),(x,y+1),(x+1,y+1)): gv.add(p)
raised=[]
for p in gv:
    v=qv.get((float(p[0]),float(p[1])))
    if v is None: continue
    w=QW@v.co; z=p3(w.x,w.y)
    if z-w.z>0.3: raised.append(round(z-w.z,2)); w.z=z; v.co=QI@w
qm.update()
# (2b) QJ_NE_seam_fill_UNVERIFIED sits 1.5 m under 3DEP inside the gap: the new fill covers those cells too; QJ verts there
# that would poke through the fill (z > 3DEP - 0.05) are set to 3DEP - 0.05 so QJ only backs the fill.
qjn=0
if 'QJ_NE_seam_fill_UNVERIFIED' in bpy.data.objects:
    qj=bpy.data.objects['QJ_NE_seam_fill_UNVERIFIED']; JW=qj.matrix_world; JI=JW.inverted()
    for v in qj.data.vertices:
        w=JW@v.co
        if (int(np.floor(w.x)),int(np.floor(w.y))) in gap or (int(np.floor(w.x-0.01)),int(np.floor(w.y-0.01))) in gap:
            z=p3(w.x,w.y)-0.05
            if w.z>z: w.z=z; v.co=JI@w; qjn+=1
    qj.data.update()
# (3) gap fill
bm=bmesh.new(); vv={}; src={'qi':0,'apron':0,'3dep':0}
def V(x,y):
    if (x,y) in vv: return vv[(x,y)]
    q=qv.get((float(x),float(y)))
    if q is not None: z=(QW@q.co).z; src['qi']+=1
    elif x==246:
        z=ray(B1,246.0+0.02,y)
        if z is None: z=p3(x,y); src['3dep']+=1
        else: src['apron']+=1
    else: z=p3(x,y); src['3dep']+=1
    vv[(x,y)]=bm.verts.new(Vector((x,y,z))); return vv[(x,y)]
for x,y in sorted(gap):
    bm.faces.new((V(x,y),V(x+1,y),V(x+1,y+1),V(x,y+1)))
bm.normal_update()
nm='WS230_NE_east_gap_fill_3DEP_UNVERIFIED'
if nm in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[nm])
me=bpy.data.meshes.new(nm); bm.to_mesh(me); bm.free()
uv=me.uv_layers.new(name='ortho')
for l in me.loops:
    c=me.vertices[l.vertex_index].co; uv.data[l.index].uv=((c.x+250)/500,(c.y+250)/500)
for p in me.polygons: p.use_smooth=True
o=bpy.data.objects.new(nm,me); o.data.materials.append(t.data.materials[0])
for c in t.users_collection: c.objects.link(o)
down=sum(1 for p in me.polygons if p.normal.z<0)
ys=[y for x,y in gap]; xs=[x for x,y in gap]
# post check: gap-cell centres now covered, fill vs 3DEP
dz=[ (me.vertices[i].co.z-p3(me.vertices[i].co.x,me.vertices[i].co.y)) for i in range(len(me.vertices))]
rep={'gap_cells':len(gap),'gap_x':[min(xs),max(xs)] if xs else None,'gap_y':[min(ys),max(ys)] if ys else None,
     'strip_verts_reheighted':len(ch),'strip_dz_max':max(ch or [0]),'strip_dz_min':min(ch or [0]),
     'qj_verts_tucked':qjn,'qi_raised':len(raised),'qi_raise_max':max(raised or [0]),'fill_faces':len(me.polygons),'fill_vert_src':src,
     'fill_minus_3dep':[round(min(dz),2),round(float(np.median(dz)),2),round(max(dz),2)] if dz else None,'down_faces':down,'material':t.data.materials[0].name}
print('F230A',json.dumps(rep),flush=True)
json.dump(rep,open(MS+'scripts/ws230/fix230a_report.json','w'))
