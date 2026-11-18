# pv: 'Roof_pent' (campus Roof_equipment_parapets) holds an old 18 x 80 m precast box (faces 30-35, z 145.06-151.02)
# inside Dickson's west wing. Where the LiDAR-derived north wall top slopes down (~148.8 m) its pale precast north/side
# faces show through as grey-blue parallelograms. Its four vertical sides get the Dickson buff brick (facade UV:
# u = horizontal run, v = z-134.8, no win_top -> no shader windows) so the gap reads as set-back brick. UNVERIFIED.
# REVERT=1 restores the material indices, removes the slot and the UV layer.
import bpy, os, math
REV=os.environ.get('REVERT')=='1'
o=bpy.data.objects['Roof_pent']; me=o.data; MN='PE_Dickson_brick_buff_no_red_spandrel_UNVERIFIED'
if 'pv_orig_mi' in o:
    for i,mi in o['pv_orig_mi'].items(): me.polygons[int(i)].material_index=mi
    del o['pv_orig_mi']
    if 'facade' in me.uv_layers: me.uv_layers.remove(me.uv_layers['facade'])
    if 'pv_prev_uv_active' in o:
        a=o['pv_prev_uv_active']
        if a>=0 and a<len(me.uv_layers): me.uv_layers.active_index=a
        del o['pv_prev_uv_active']
    k=[i for i,m in enumerate(me.materials) if m and m.name==MN]
    if k and o.get('pv_added_slot',0): me.materials.pop(index=k[-1])
    if 'pv_added_slot' in o: del o['pv_added_slot']
    print('REVERTED_PV_PENT')
if not REV:
    mw=o.matrix_world; FACES=[]
    for p in me.polygons:
        c=mw@p.center; nz=abs(p.normal.z)
        if p.index in (32,33,34,35) and nz<0.1 and -183<c.x<-129 and 76<c.y<161: FACES.append(p.index)
    print('PV_PENT faces',FACES, 'uv_layers',[u.name for u in me.uv_layers])
    o['pv_prev_uv_active']=me.uv_layers.active_index if len(me.uv_layers) else -1
    if MN not in [m.name for m in me.materials if m]: me.materials.append(bpy.data.materials[MN]); o['pv_added_slot']=1
    slot=[m.name if m else '' for m in me.materials].index(MN)
    o['pv_orig_mi']={str(i):me.polygons[i].material_index for i in FACES}
    prev_active=me.uv_layers.active_index if len(me.uv_layers) else -1
    uvl=me.uv_layers.new(name='pv_uv') if 'facade' not in me.uv_layers else None
    # the brick shader reads the UV map named 'facade'; name our layer that only if none exists
    if uvl is not None: uvl.name='facade'
    else: raise SystemExit('facade layer already present')
    if prev_active>=0: me.uv_layers.active_index=prev_active
    for i in FACES:
        p=me.polygons[i]; n=(mw.to_3x3()@p.normal); h=__import__('mathutils').Vector((-n.y,n.x,0)).normalized()
        for li in p.loop_indices:
            co=mw@me.vertices[me.loops[li].vertex_index].co
            uvl.data[li].uv=(co.dot(h), co.z-134.8)
        p.material_index=slot
    print('PV_PENT done slot',slot)
