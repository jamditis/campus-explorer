# pn: window units on the exposed walls of the pn tier prisms (rows 149.0/153.4/157.6 m, 3.6 m pitch), only where 5 horizontal
# probe rays 1 m outward are clear (not behind the old walls, lower tiers or other masses). Maroon frame + mullion, dark glass,
# tan sill, after the ported Feliciano windows. ALL UNVERIFIED (count/positions guessed). REVERT=1 removes.
import bpy, bmesh, os, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv; OUT=os.environ.get('SAVEAS')
ON='PN_Feliciano_tier_windows_UNVERIFIED'
if ON in bpy.data.objects:
    o=bpy.data.objects[ON]; me=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(me); print('REVERTED_PN_WIN')
if not REV:
    col=bpy.data.collections['PN_Feliciano_remass_20261101pn_UNVERIFIED']
    occ=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and ('Feliciano' in o.name or o.name.startswith('PG_feliciano'))]
    V=[];F=[]
    for o in occ:
        mw=o.matrix_world; b=len(V); V+= [mw@v.co for v in o.data.vertices]; F+=[[b+i for i in p.vertices] for p in o.data.polygons]
    T=BVHTree.FromPolygons(V,F); print('OCC',len(occ),len(F))
    ROWS=[(149.0,2.45),(153.4,2.45),(157.6,2.8)]; PITCH=3.6; WW=2.0
    bm=bmesh.new(); n_ok=0; n_try=0
    def box(c,ux,n,w,h,d,mi,off):
        # axis box centred at c on the wall: width along ux, height z, depth along n from off to off+d
        z=Vector((0,0,1)); vs=[]
        for a in (-w/2,w/2):
            for bb in (-h/2,h/2):
                for e in (off,off+d): vs.append(bm.verts.new(c+ux*a+z*bb+n*e))
        idx=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
        for q in idx: bm.faces.new([vs[i] for i in q]).material_index=mi
    for o in [o for o in col.objects if o.name.startswith('PN_Feliciano_tier_')]:
        mw=o.matrix_world; zt=max((mw@v.co).z for v in o.data.vertices)
        for p in o.data.polygons:
            n=(mw.to_3x3()@p.normal).normalized()
            if abs(n.z)>0.1 or p.material_index!=0: continue
            vs=[mw@o.data.vertices[i].co for i in p.vertices]
            bot=sorted(vs,key=lambda v:v.z)[:2]; a,b=bot
            ux=Vector((b.x-a.x,b.y-a.y,0)); L=ux.length
            if L<WW+0.8: continue
            ux.normalize(); nn=Vector((n.x,n.y,0)).normalized()
            k=int((L-0.6)//PITCH); 
            if k<1: continue
            s0=(L-k*PITCH)/2+PITCH/2
            for z0,h in ROWS:
                if z0+h>zt-0.45: continue
                for j in range(k):
                    n_try+=1
                    c=Vector((a.x,a.y,0))+ux*(s0+j*PITCH); c.z=z0+h/2
                    ok=True
                    for du,dz in ((0,0),(-WW/2+.1,-h/2+.1),(WW/2-.1,-h/2+.1),(-WW/2+.1,h/2-.1),(WW/2-.1,h/2-.1),(0,h/2+0.3),(0,-h/2-0.3)):
                        q=c+ux*du+Vector((0,0,dz))+nn*0.01
                        hit=T.ray_cast(q,nn,1.2)
                        if hit[0] is not None: ok=False; break
                    if not ok: continue
                    n_ok+=1
                    box(c,ux,nn,WW+0.2,h+0.2,0.07,0,-0.02)          # stucco surround
                    FW=0.07
                    for du,dz,bw,bh in ((0,h/2-FW/2,WW,FW),(0,-h/2+FW/2,WW,FW),(-WW/2+FW/2,0,FW,h),(WW/2-FW/2,0,FW,h),(0,h*0.2,WW,0.05)):
                        box(c+ux*du+Vector((0,0,dz)),ux,nn,bw,bh,0.06,1,0.03)   # maroon frame bars + transom
                    box(c,ux,nn,WW-0.1,h-0.1,0.004,2,0.052)          # glass, 4 cm behind the frame face
                    box(c,ux,nn,0.06,h-0.14,0.03,1,0.08)             # mullion
                    box(c-Vector((0,0,h/2+0.07)),ux,nn,WW+0.3,0.08,0.13,3,-0.02)   # sill
    me=bpy.data.meshes.new(ON); bm.to_mesh(me); bm.free()
    for nm in ('North_Feliciano_stucco_white','North_Feliciano_frame_maroon','North_Feliciano_glass_dark','North_Feliciano_sill_tan'): me.materials.append(bpy.data.materials[nm])
    o=bpy.data.objects.new(ON,me); col.objects.link(o)
    print('PN_WIN placed',n_ok,'of',n_try)
if OUT: bpy.ops.wm.save_as_mainfile(filepath=OUT,copy=True); print('SAVED_AS',OUT)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
