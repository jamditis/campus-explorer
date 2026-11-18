# pn (Nov 1 2026): clean re-mass of Feliciano's upper storeys/roof from LiDAR tiers (ALL UNVERIFIED approximation).
# Hides the lumpy 'Feliciano School of Business roof (LiDAR)' mesh and adds nested stucco tier prisms
# (143/146.5/150/153.3/156.6/161.3 m, building-aligned, footprint-clipped 12+3k cm inside the walls, tile ring 2 m on top),
# plus 7 hip roofs (red tile, 0.6 m eaves with soffit) where the LiDAR top rises above 162.5 m. REVERT=1 removes it all.
import bpy, bmesh, json, os, sys, math
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv; OUT=os.environ.get('SAVEAS')
CN='PN_Feliciano_remass_20261101pn_UNVERIFIED'
roof=bpy.data.objects['Feliciano School of Business roof (LiDAR)']
HIDE=[roof]+[o for o in bpy.data.objects if o.name.startswith('el coping strips Feliciano')]
if CN in bpy.data.collections:
    col=bpy.data.collections[CN]
    for o in list(col.objects): me=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(me)
    bpy.data.collections.remove(col)
    for ob in HIDE:
        if 'pn_prev_hide' in ob.keys():
            hv,hr=ob['pn_prev_hide']; ob.hide_viewport=bool(hv); ob.hide_render=bool(hr); del ob['pn_prev_hide']
    print('REVERTED_PN')
if not REV:
    D=json.load(open('data/pn/polys.json')); th=D['th']; cx,cy=D['cx'],D['cy']; c,s=math.cos(th),math.sin(th)
    def uv2w(u,v): return (cx+u*c-v*s, cy+u*s+v*c)
    M=bpy.data.materials
    mats=[M['PG_Feliciano_wall_stucco_plain_no_shader_windows_UNVERIFIED'],M['PI_Feliciano_roof_tile_forced_UNVERIFIED'],M['Roof_tile_or_membrane'],M['Eave_tile_top_soffit_under']]
    col=bpy.data.collections.new(CN); (roof.users_collection[0]).children.link(col)
    FAIL=[0]; ZB=139.8; RING=float(os.environ.get('RING','0')); RD=float(os.environ.get('RD','0.55'))
    for t in D['tiers']:
        bm=bmesh.new(); loops=[t['ext']]+t['holes']; z=t['z']
        tris=tessellate_polygon([[Vector((x,y,0)) for x,y in L] for L in loops])
        flat=[q for L in loops for q in L]
        top=[bm.verts.new((x,y,z)) for x,y in flat]; bot=[bm.verts.new((x,y,ZB)) for x,y in flat]
        tf=[]
        for a,b,cc in tris:
            try: f=bm.faces.new((top[a],top[b],top[cc])); f.material_index=2; tf.append(f)
            except ValueError: FAIL[0]+=1
        off=0
        for L in loops:
            n=len(L)
            for i in range(n):
                a,b=off+i,off+(i+1)%n
                try: bm.faces.new((bot[a],bot[b],top[b],top[a])).material_index=0
                except ValueError: pass
            off+=n
        bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
        # top faces must face up
        for f in tf:
            if f.normal.z<0: f.normal_flip()
        if RING>0:
            r=bmesh.ops.inset_region(bm,faces=tf,thickness=RING,depth=RD,use_even_offset=True,use_boundary=True)
            for f in r['faces']: f.material_index=1
        ne=sum(1 for e in bm.edges if not e.is_manifold); print('TIER',t['k'],'tris',len(tris),'nonmanifold',ne)
        me=bpy.data.meshes.new('PN_tier_%d'%t['k']); bm.to_mesh(me); bm.free()
        for m_ in mats: me.materials.append(m_)
        o=bpy.data.objects.new('PN_Feliciano_tier_%.1f_UNVERIFIED'%z,me); col.objects.link(o)
    OV=0.6; EZ=161.3+0.35
    for h,H in enumerate(D['hips']):
        ua,ub=H['u'][0]-OV,H['u'][1]+OV; va,vb=H['v'][0]-OV,H['v'][1]+OV; zr=max(H['zr'],EZ+1.2)
        lu,lv=ub-ua,vb-va; bm=bmesh.new()
        e=[bm.verts.new(uv2w(*q)+(EZ,)) for q in ((ua,va),(ub,va),(ub,vb),(ua,vb))]
        if lu>=lv: hw=lv/2; r1=bm.verts.new(uv2w(ua+hw,va+hw)+(zr,)); r2=bm.verts.new(uv2w(ub-hw,va+hw)+(zr,))
        else: hw=lu/2; r1=bm.verts.new(uv2w(ua+hw,va+hw)+(zr,)); r2=bm.verts.new(uv2w(ua+hw,vb-hw)+(zr,))
        if lu>=lv: fs=[(e[0],e[1],r2,r1),(e[1],e[2],r2),(e[2],e[3],r1,r2),(e[3],e[0],r1)]
        else: fs=[(e[0],e[1],r1),(e[1],e[2],r2,r1),(e[2],e[3],r2),(e[3],e[0],r1,r2)]
        for q in fs:
            vs=[] 
            for v in q:
                if v not in vs: vs.append(v)
            bm.faces.new(vs).material_index=1
        sf=bm.faces.new((e[3],e[2],e[1],e[0])); sf.material_index=3
        # fascia: 25 cm drop
        lo=[bm.verts.new(v.co-Vector((0,0,0.25))) for v in e]
        for i in range(4): bm.faces.new((lo[i],lo[(i+1)%4],e[(i+1)%4],e[i])).material_index=3
        bm.faces.remove(sf); bm.faces.new((lo[3],lo[2],lo[1],lo[0])).material_index=3
        bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
        me=bpy.data.meshes.new('PN_hip_%d'%h); bm.to_mesh(me); bm.free()
        for m_ in mats: me.materials.append(m_)
        for p in me.polygons: p.use_smooth=False
        o=bpy.data.objects.new('PN_Feliciano_hip_roof_%d_UNVERIFIED'%h,me); col.objects.link(o)
    for ob in HIDE:
        ob['pn_prev_hide']=[int(ob.hide_viewport),int(ob.hide_render)]; ob.hide_viewport=True; ob.hide_render=True
    print('HIDDEN',[ob.name for ob in HIDE])
    print('FAILS',FAIL[0]); print('PN_REMASS tiers',len(D['tiers']),'hips',len(D['hips']))
if OUT: bpy.ops.wm.save_as_mainfile(filepath=OUT,copy=True); print('SAVED_AS',OUT)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
