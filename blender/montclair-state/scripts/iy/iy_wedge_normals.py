# Session iy (2026-10-25 ~8:30 PM ET): hide the dark corner wedges at the amphitheater aisle half-steps.
# iw left ~75 seat/riser faces tilted 8-55 deg that touch aisle verts: one-corner wedges where a half-height aisle step
# (verts at level k+0.5) meets a full row (vert at k+1) on the 8 cm grid. Their true normal leans ~53 deg away from the
# sky, so they render as dark triangles beside the handrails. Geometry can't be flattened without tilting the adjoining
# seat cells (the lone row vert is shared with flat seat faces), so the fix is shading-only: those faces get custom split
# normals = straight up (like the seat tops around them); every other loop keeps its current corner normal.
# Order: ip -> iq -> ir -> is -> it -> iu -> iv -> iw -> ix -> iy. Env SAVE=1, DRY=1 (stats only), OUTB=copy path,
# REVERT=1 (clears custom normals = back to ix shading). Faces are tagged in int face attribute 'iy_wedge'.
import bpy, os, numpy as np
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data
names=[s.material.name if s.material else '' for s in ob.material_slots]
SEAT=names.index('hn_amphi_seat_stone_blocks'); RIS=names.index('hn_amphi_riser_coursed_stone')
AIS=set(i for i,n in enumerate(names) if 'aisle' in n)
print('IY has_custom_normals',me.has_custom_normals,'mods',[m.type for m in ob.modifiers])
if os.environ.get('REVERT'):
    if me.has_custom_normals: me.free_normals_split() if hasattr(me,'free_normals_split') else bpy.ops.mesh.customdata_custom_splitnormals_clear()
    print('IY REVERTED')
else:
    P=len(me.polygons); n=np.empty(P*3); me.polygons.foreach_get('normal',n); n=n.reshape(-1,3)
    mi=np.empty(P,int); me.polygons.foreach_get('material_index',mi)
    av=set()
    for p in me.polygons:
        if p.material_index in AIS: av.update(p.vertices)
    tl=np.degrees(np.arccos(np.clip(n[:,2],-1,1)))
    MAXT=float(os.environ.get('MAXT',60))
    # jb (2026-10-25): never treat jb nosing-chamfer faces (face attr jb_chamfer=1) as wedges (no-op if the attr is absent)
    jbx=np.zeros(P,np.int32)
    if me.attributes.get('jb_chamfer'): me.attributes['jb_chamfer'].data.foreach_get('value',jbx)
    wedge=[p.index for p in me.polygons if mi[p.index] in (SEAT,RIS) and 8<tl[p.index]<MAXT and not jbx[p.index] and any(v in av for v in p.vertices)]
    ar=sum(me.polygons[i].area for i in wedge)
    print('IY wedge faces',len(wedge),'area',round(ar,3),'tilt pct',[round(float(np.percentile(tl[wedge],q)),1) for q in (5,50,95)] if wedge else None,
          'mat seat/riser',sum(mi[i]==SEAT for i in wedge),sum(mi[i]==RIS for i in wedge))
    if os.environ.get('DRY')!='1':
        L=len(me.loops); cn=np.empty(L*3)
        me.corner_normals.foreach_get('vector',cn) if hasattr(me,'corner_normals') else None
        cn=cn.reshape(-1,3)
        for i in wedge:
            p=me.polygons[i]
            for li in p.loop_indices: cn[li]=(0.0,0.0,1.0)
        me.normals_split_custom_set(cn.tolist())
        a=me.attributes.get('iy_wedge') or me.attributes.new('iy_wedge','INT','FACE')
        flag=np.zeros(P,np.int32); flag[wedge]=1
        # 2 = half-height riser beside an aisle, only with HALF=1 (tested in iy: brightened the LIT half-risers too much and did not
        # reach the dark notch parallelograms, which are cast shadows on half-risers not touching aisle verts) -> off by default
        RISER=(141.3-132.45)/19; half=0
        for p in (me.polygons if os.environ.get('HALF')=='1' else []):
            if mi[p.index]!=RIS or flag[p.index] or not any(v in av for v in p.vertices): continue
            lv=[(me.vertices[v].co.z-132.45)/RISER for v in p.vertices]; sp=max(lv)-min(lv)
            if 0.35<sp<0.65: flag[p.index]=2; half+=1
        print('IY half-risers flagged',half)
        a.data.foreach_set('value',flag)
        me.update(); print('IY custom normals set; has_custom_normals',me.has_custom_normals)
        ob['iy_wedge_normals']='2026-10-25 session iy: aisle half-step wedge faces given up-facing custom normals'
if os.environ.get('OUTB'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUTB'],copy=True); print('IY WROTE')
elif os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('IY SAVED')
