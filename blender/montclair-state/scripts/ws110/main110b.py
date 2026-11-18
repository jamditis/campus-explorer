import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state/'
def obvh(o):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); return t
road=next(o for o in bpy.data.objects if o.name.startswith('WS110_CollegeAve_S_end_to_NormalAve'))
RB=obvh(road)
ua=bpy.data.objects['UA_NormalAve_N_sidewalk_583841727_UNVERIFIED']
walkmat=ua.data.materials[0] if ua.data.materials else bpy.data.materials['WS27_curb_concrete_UNVERIFIED']
vg=next((o for o in bpy.data.objects if o.name.startswith('WS73') and 'verge' in o.name.lower() and o.type=='MESH' and o.data.materials),None)
grassmat=vg.data.materials[0] if vg else None
print('E110b mats',walkmat.name,grassmat.name if grassmat else None, vg.name if vg else None)
ua.hide_render=True; ua.hide_viewport=True
V=[];G=[];cur=None
for ln in open(R+'prep/ws85_normal_ave_sidewalks/normal_ave_sidewalks_verges_UNVERIFIED.obj'):
    p=ln.split()
    if not p: continue
    if p[0]=='v': V.append(tuple(map(float,p[1:4])))
    elif p[0]=='o': cur=[p[1],[]]; G.append(cur)
    elif p[0]=='f': cur[1].append([int(q.split('/')[0])-1 for q in p[1:]])
V=np.array(V); coll=bpy.data.collections['WS110_CollegeAve_S_end_NormalAve_road_layer']
for kind,mat in (('sidewalk',walkmat),('verge',grassmat)):
    bm=bmesh.new(); vm={}; cut=0
    def gv(i):
        if i not in vm: vm[i]=bm.verts.new(tuple(V[i]))
        return vm[i]
    for nm,fs in G:
        if kind not in nm: continue
        for f in fs:
            c=V[f].mean(0)
            if RB.ray_cast(Vector((c[0],c[1],300)),Vector((0,0,-1)))[0] is not None: cut+=1; continue
            try: bm.faces.new([gv(i) for i in f])
            except ValueError: pass
    for fc in bm.faces:
        if fc.normal.z<0: fc.normal_flip()
    # 8 cm slab edge so the walk reads as a slab, not a sheet
    if kind=='sidewalk':
        ed=[e for e in bm.edges if e.is_boundary]
        r=bmesh.ops.extrude_edge_only(bm,edges=ed)
        for v in r['geom']:
            if isinstance(v,bmesh.types.BMVert): v.co.z-=0.10
    me=bpy.data.meshes.new('WS110_NormalAve_'+kind); bm.to_mesh(me); bm.free()
    if mat: me.materials.append(mat)
    o=bpy.data.objects.new('WS110_NormalAve_%s_ws85prep_ortho2020_UNVERIFIED'%kind,me); coll.objects.link(o)
    print('E110b',kind,'faces',len(me.polygons),'mouth cut',cut)
# poke check: terrain/skirt above the walks
pave=[o for o in coll.objects if 'sidewalk' in o.name or 'verge' in o.name]
for it in range(2):
    TB={tn:obvh(bpy.data.objects[tn]) for tn in ('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km')}; pokes=0; worst=0
    for o in pave:
        for v in o.data.vertices:
            w=o.matrix_world@v.co
            for tn,tb in TB.items():
                h,nrm,fi,_=tb.ray_cast(Vector((w.x,w.y,300)),Vector((0,0,-1)))
                if h is not None and h.z>w.z-0.02:
                    pokes+=1; worst=max(worst,h.z-w.z); tob=bpy.data.objects[tn]; inv=tob.matrix_world.inverted()
                    for vi in tob.data.polygons[fi].vertices:
                        vv=tob.data.vertices[vi]; ww=tob.matrix_world@vv.co
                        if ww.z>w.z-0.08: vv.co=inv@Vector((ww.x,ww.y,w.z-0.08))
    for tn in TB: bpy.data.objects[tn].data.update()
    print('P110b iter',it,'pokes',pokes,'worst %.2f'%worst)
    if pokes==0: break
bpy.ops.wm.save_mainfile(); print('M110 SAVED b',flush=True)
exec(open(R+'scripts/ws105/cut105.py').read().replace('ws105/render_cut105','ws110/render_cut110'))
