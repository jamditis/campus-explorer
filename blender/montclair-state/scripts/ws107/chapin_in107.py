import bpy, json, os, numpy as np
D='/workspace/nj-scenes/montclair-state/'
J=json.load(open(D+'prep/ws102_Chapin_building/chapin103.json'))['Chapin']
O=np.array(J['outer']); I=np.array(J['inner'])
def inpoly(P,x,y):
    c=np.zeros(x.shape,bool); n=len(P)
    for i in range(n):
        x1,y1=P[i]; x2,y2=P[(i+1)%n]
        m=((y1>y)!=(y2>y)); xi=(x2-x1)*(y-y1)/(y2-y1+1e-12)+x1; c^=m&(x<xi)
    return c
def infp(x,y): return inpoly(O,x,y)&~inpoly(I,x,y)
# 1) existing objects that occupy the footprint above grade (duplicates to retire?)
hits=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.name.startswith('WS107_'): continue
    me=o.data
    if len(me.vertices)==0 or len(me.vertices)>400000: continue
    co=np.empty(len(me.vertices)*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
    M=np.array(o.matrix_world); w=co@M[:3,:3].T+M[:3,3]
    k=infp(w[:,0],w[:,1])&(w[:,2]>127.5)
    if k.sum()>=4: hits.append((o.name,int(k.sum()),len(w),round(float(w[k,2].max()),2)))
hits.sort(key=lambda t:-t[1])
for h in hits[:25]: print('H107',h)
if os.environ.get('APPEND')=='1':
    with bpy.data.libraries.load(D+'prep/ws107_Chapin_roofplanes/chapin_massing_ws107.blend') as (src,dst):
        dst.objects=[n for n in src.objects if n.startswith('WS107_Chapin_')]
    col=bpy.data.collections.get('WS107_Chapin_Hall_massing_LiDAR2023_OSM_UNVERIFIED') or bpy.data.collections.new('WS107_Chapin_Hall_massing_LiDAR2023_OSM_UNVERIFIED')
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    for o in dst.objects: col.objects.link(o)
    # swap placeholder materials for campus stucco/tile if present
    def find(*keys):
        for m in bpy.data.materials:
            n=m.name.lower()
            if all(k in n for k in keys) and not m.name.startswith('WS107_'): return m
    stucco=find('cole','stucco') or find('stucco'); tile=find('tile','roof') or find('red','tile')
    print('MAT107',stucco and stucco.name, tile and tile.name)
    for o in dst.objects:
        for i,s in enumerate(o.material_slots):
            if s.material and 'stucco' in s.material.name and stucco: s.material=stucco
            if s.material and 'tile' in s.material.name and tile: s.material=tile
    ret=bpy.data.collections.get('WS107_retired_trees_inside_Chapin') or bpy.data.collections.new('WS107_retired_trees_inside_Chapin')
    if ret.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(ret)
    for o in [o for o in bpy.data.objects if o.name.startswith('T_')]:
        x,y=o.matrix_world.translation.x,o.matrix_world.translation.y
        if infp(np.array([x]),np.array([y]))[0]:
            for c in list(o.users_collection): c.objects.unlink(o)
            ret.objects.link(o); o.hide_render=True; o.hide_viewport=True; print('TREE107 retired',o.name,round(x,1),round(y,1))
    ret.hide_render=True; ret.hide_viewport=True
    # walkway overlap check
    for nm in [o.name for o in bpy.data.objects if o.name.startswith('WS105_Chapin_E_lower_walkway')]:
        o=bpy.data.objects[nm]; co=np.empty(len(o.data.vertices)*3); o.data.vertices.foreach_get('co',co); co=co.reshape(-1,3); M=np.array(o.matrix_world); w=co@M[:3,:3].T+M[:3,3]
        print('WALK107',nm,'verts inside footprint',int(infp(w[:,0],w[:,1]).sum()),'of',len(w))
    # camera fixes for WIPs
    from mathutils import Vector
    def cam(n,loc,tgt,lens=28):
        c=bpy.data.objects.get(n) or bpy.data.objects.new(n,bpy.data.cameras.new(n))
        if c.name not in bpy.context.scene.collection.objects: bpy.context.scene.collection.objects.link(c)
        c.location=loc; c.rotation_euler=(Vector(tgt)-Vector(loc)).to_track_quat('-Z','Y').to_euler(); c.data.lens=lens
    cam('WS107_CAM_oblique_Chapin_W_bank_from_E',(-150,-200,165),(-200,-190,130),30)
    cam('WS107_CAM_eye_Chapin_from_CollegeAve_S',(-226.5,-232,124.0),(-205,-185,130),24)
    print('A107 appended',len(dst.objects))
    bpy.ops.wm.save_mainfile(); print('A107 SAVED')
