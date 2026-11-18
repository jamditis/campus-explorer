# Session ec (Oct 21 2026 ~5:40 PM ET): seat floating rooftop units (Roof_hvac / Roof_vent islands)
# Generic: for each island, cast down at centre + 4 inset corners from bottom+0.3 m (self hidden);
# if every hit is > 0.3 m below the island bottom and the hits agree within 0.5 m -> drop the island
# so its bottom sits 0.05 m into the highest hit (same embed as the other units). If they disagree -> hide
# the island by collapsing nothing; instead it is reported (no guess).  Originals in point attribute ec_orig_z.
# Env: SAVE=1 save; REVERT=1 restore originals.
import bpy, bmesh, os
from mathutils import Vector
sc=bpy.context.scene
NAMES=['Roof_hvac','Roof_vent']
REVERT=os.environ.get('REVERT')=='1'
for name in NAMES:
    o=sc.objects[name]; me=o.data
    if 'ec_orig_z' not in me.attributes:
        a=me.attributes.new('ec_orig_z','FLOAT','POINT')
        for v in me.vertices: a.data[v.index].value=v.co.z
        a=me.attributes.new('ec_orig_xy','FLOAT2','POINT')
        for v in me.vertices: a.data[v.index].vector=(v.co.x,v.co.y)
    a=me.attributes['ec_orig_z']; axy=me.attributes['ec_orig_xy']
    for v in me.vertices: v.co=(axy.data[v.index].vector[0],axy.data[v.index].vector[1],a.data[v.index].value)
    if REVERT: o.pop('ec_float_fix',None); me.update(); continue
    mw=o.matrix_world; inv=mw.inverted()
    # islands via bmesh (local), positions world
    bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    seen=set(); isl=[]
    for v in bm.verts:
        if v.index in seen: continue
        st=[v]; comp=[]; seen.add(v.index)
        while st:
            x=st.pop(); comp.append(x.index)
            for e in x.link_edges:
                y=e.other_vert(x)
                if y.index not in seen: seen.add(y.index); st.append(y)
        isl.append(comp)
    bm.free()
    for n in NAMES: sc.objects[n].hide_set(True)
    dg=bpy.context.evaluated_depsgraph_get()
    moved=0; flagged=0
    for comp in isl:
        W=[mw@me.vertices[i].co for i in comp]
        xs=[p.x for p in W]; ys=[p.y for p in W]; zb=min(p.z for p in W)
        cx=(min(xs)+max(xs))/2; cy=(min(ys)+max(ys))/2; ix=(max(xs)-min(xs))*0.4; iy=(max(ys)-min(ys))*0.4
        if not (-60<cx<80 and -70<cy<70): continue   # CCOM day-area only (ec scope)
        hz=[]; hn=[]
        for dx,dy in [(0,0),(-ix,-iy),(ix,-iy),(-ix,iy),(ix,iy)]:
            hit,l,nn,ii,ob,m=sc.ray_cast(dg,Vector((cx+dx,cy+dy,zb+0.3)),Vector((0,0,-1)))
            hz.append(l.z if hit else -1e9); hn.append(ob.name if hit else '')
        gap=zb-max(hz)
        if gap<=0.3: continue
        bad=any(('Terrain' in n or 'Context' in n or n=='') for n in hn)
        if max(hz)-min(hz)>0.5 or bad or gap>8:
            # no single roof under it: collapse the island to its centre (hidden), reported
            c=Vector((cx,cy,zb))
            for i in comp: me.vertices[i].co=inv@c
            print("EC_HIDE",name,round(cx,1),round(cy,1),round(zb,2),[round(h,2) for h in hz],set(n[:30] for n in hn)); flagged+=1; continue
        d=gap+0.05
        for i in comp:
            p=mw@me.vertices[i].co; p.z-=d; me.vertices[i].co=inv@p
        moved+=1
        print("EC_MOVE",name,round(cx,1),round(cy,1),round(zb,2),"->",round(zb-d,2))
    for n in NAMES: sc.objects[n].hide_set(False)
    o['ec_float_fix']=f"moved {moved} flagged {flagged}"
    me.update(); print("EC_SUM",name,moved,flagged)
if os.environ.get('SAVE')=='1':
    bpy.ops.wm.save_mainfile(); print("EC_SAVED")
