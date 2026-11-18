import bpy
for cn in ('QP_Richardson_Hall_UNVERIFIED',):
    c=bpy.data.collections.get(cn); zs=[]
    for o in c.all_objects:
        if o.type=='MESH':
            mw=o.matrix_world
            for v in o.data.vertices:
                w=mw@v.co
                if w.y>250: zs.append((round(w.z,2),o.name))
    zs.sort(); print('RICH lowest north verts',zs[:3],'n',len(zs))
for o in bpy.data.objects:
    if o.name.startswith('QT_Richardson_base_plinth') or o.name.startswith('QQ_') and 'apron' in o.name.lower():
        mw=o.matrix_world; z=[ (mw@v.co).z for v in o.data.vertices if (mw@v.co).y>250] if o.type=='MESH' else []
        print('OBJ',o.name,round(min(z),2) if z else None, round(max(z),2) if z else None)
