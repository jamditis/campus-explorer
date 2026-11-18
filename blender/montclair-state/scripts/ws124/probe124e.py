import bpy
for o in bpy.data.objects:
    if o.type!='MESH' or not o.name.startswith(('WS107_Chapin_07','WS107_Chapin_08','WS107_Chapin_02','WS107_Chapin_06')): continue
    mw=o.matrix_world
    for p in o.data.polygons:
        vs=[mw@o.data.vertices[i].co for i in p.vertices]
        if abs(p.normal.z)<0.2 and min(v.x for v in vs)<-205 and max(v.y for v in vs)>-204 and min(v.y for v in vs)<-199:
            print('W',o.name[:22],[round(p.normal.x,2),round(p.normal.y,2)],'x',round(min(v.x for v in vs),2),round(max(v.x for v in vs),2),'y',round(min(v.y for v in vs),2),round(max(v.y for v in vs),2),'z',round(min(v.z for v in vs),2),round(max(v.z for v in vs),2))
