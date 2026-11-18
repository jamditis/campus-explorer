"""2026-10-21 session ea (~3:35 PM ET). Fix the pre-existing interior clashes that dZ's clear-zone test found (STATE Next 4).
Non-destructive: per corridor segment a hidden cutter box 'ea_cutter_<SEG>' = the segment's interior volume in the floor's
own frame (floor-slab bottom .. ceiling-tile top, the terrazzo footprint), and an EXACT Boolean DIFFERENCE modifier 'ea_cut_<SEG>'
on each allow-listed intruder:
  SOUTH0: equipment-yard pieces CCOM_equip_*_20261014jf3 (wall patches/backs/heads, platform, roll door, personnel door);
  EAST0 : the old v-era newsroom slab CCOM_int_newsroom_G_20261014v;
  SOUTH1: WEST0's back wall/back base/endcap_b/floor/ceiling/LED/diffuser (SOUTH1 owns the corner overlap, so WEST0's south
          end is closed by SOUTH1's own back wall + endcap_a), and Morehead 'north entrance (secondary, 3i UNVERIFIED)'
          pilasters/entablature/cornice (cut flush to the window wall). Pieces of that UNVERIFIED entrance lying wholly inside the
          corridor (lanterns, arms, caps, pulls) are hidden instead (prop ea_hidden) -- guessed items, Joe's rule.
DRY=1 only reports. REVERT=1 removes modifiers/cutters and unhides. SAVE=1 saves. Idempotent. Report -> data/ea/cutters_ea.txt"""
import bpy, bmesh, os, re
from mathutils import Vector
REP=[]
def rep(*a):
    s=' '.join(str(x) for x in a); REP.append(s); print('EA', s, flush=True)
# revert
for o in bpy.data.objects:
    for m in [m for m in o.modifiers if m.name.startswith('ea_cut_')]: o.modifiers.remove(m)
    if 'ea_mod' in o: del o['ea_mod']
    if 'ea_hidden' in o: o.hide_render=False; o.hide_viewport=False; del o['ea_hidden']
for o in [o for o in bpy.data.objects if 'ea_new' in o]:
    me=o.data; bpy.data.objects.remove(o)
    if me and me.users==0: bpy.data.meshes.remove(me)
bpy.context.view_layer.update()
DRY=os.environ.get('DRY')=='1'
if os.environ.get('REVERT')=='1':
    rep('REVERTED')
else:
    ALLOW={'SOUTH0':[r'^CCOM_equip_.*_20261014jf3$'],
           'EAST0':[r'^CCOM_int_newsroom_G_20261014v$'],
           'SOUTH1':[r'^dd_WEST0_(back_wall|back_base|endcap_b|floor_terrazzo|ceiling_tile|led_strip_\d+|slot_diffuser)$',
                     r'^Morehead north entrance \(secondary, 3i UNVERIFIED\)']}
    WHOLE_HIDE=r'(lantern|pull)'
    for seg,pats in ALLOW.items():
        fl=bpy.data.objects[f'dd_{seg}_floor_terrazzo']; ce=bpy.data.objects[f'dd_{seg}_ceiling_tile']
        M=fl.matrix_world.copy(); Mi=M.inverted()
        F=[v.co for v in fl.data.vertices]
        C=[Mi@(ce.matrix_world@v.co) for v in ce.data.vertices]
        x0,x1=min(v.x for v in F),max(v.x for v in F); y0,y1=min(v.y for v in F),max(v.y for v in F)
        z0=min(v.z for v in F)-0.005; z1=max(v.z for v in C)+0.005
        rep(seg,'cutter local x',round(x0,2),round(x1,2),'y',round(y0,2),round(y1,2),'z',round(z0,3),round(z1,3))
        bm=bmesh.new()
        vs=[bm.verts.new((x,y,z)) for z in (z0,z1) for (x,y) in ((x0,y0),(x1,y0),(x1,y1),(x0,y1))]
        for q in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]: bm.faces.new([vs[i] for i in q])
        me=bpy.data.meshes.new(f'ea_cutter_{seg}'); bm.to_mesh(me); bm.free()
        cut=bpy.data.objects.new(f'ea_cutter_{seg}', me); cut.matrix_world=M
        fl.users_collection[0].objects.link(cut); cut['ea_new']=1
        cut.hide_render=True; cut.display_type='WIRE'; cut.hide_viewport=True
        n_mod=n_hide=0
        for o in sorted(bpy.data.objects, key=lambda o:o.name):
            if o.type!='MESH' or o.hide_render or not any(re.search(p,o.name) for p in pats): continue
            L=[Mi@(o.matrix_world@v.co) for v in o.data.vertices]
            ins=[l for l in L if x0<l.x<x1 and y0<l.y<y1 and z0<l.z<z1]
            # also catch faces crossing the volume with no vertex inside: test bbox overlap
            a=Vector([min(l[i] for l in L) for i in range(3)]); b=Vector([max(l[i] for l in L) for i in range(3)])
            ov = not (b.x<=x0 or a.x>=x1 or b.y<=y0 or a.y>=y1 or b.z<=z0 or a.z>=z1)
            if not ov: continue
            if seg=='SOUTH1' and o.name.startswith('Morehead') and re.search(WHOLE_HIDE,o.name) and len(ins)==len(L):
                rep('  HIDE (wholly inside, UNVERIFIED)',o.name); n_hide+=1
                if not DRY: o['ea_hidden']=1; o.hide_render=True; o.hide_viewport=True
                continue
            rep('  CUT',o.name,'verts inside',len(ins),'/',len(L),'local y',round(a.y,2),round(b.y,2))
            n_mod+=1
            if not DRY:
                m=o.modifiers.new(f'ea_cut_{seg}','BOOLEAN'); m.operation='DIFFERENCE'; m.object=cut; m.solver='EXACT'
                o['ea_mod']=1
        rep(seg,'cut',n_mod,'hidden',n_hide)
    if DRY:
        for o in [o for o in bpy.data.objects if 'ea_new' in o]: bpy.data.objects.remove(o)
    bpy.context.view_layer.update()
    # sanity: evaluated vertex count of each modified object, flag empty results
    dg=bpy.context.evaluated_depsgraph_get()
    for o in bpy.data.objects:
        if 'ea_mod' in o:
            e=o.evaluated_get(dg); n=len(e.data.vertices)
            if n==0: rep('  WARN empty after cut',o.name)
os.makedirs(bpy.path.abspath('//data/ea'), exist_ok=True)
open(bpy.path.abspath('//data/ea/cutters_ea.txt'),'a').write('\n'.join(REP)+'\n')
if os.environ.get('SAVE')=='1' and not DRY: bpy.ops.wm.save_mainfile(); print('EA_SAVED', flush=True)
