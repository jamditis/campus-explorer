import bpy
for o in bpy.data.objects:
    if o.type!='MESH': continue
    n=o.name.lower()
    if any(k in n for k in ('skirt','context','ground','dtm','3dep','ortho','terrain')):
        d=o.dimensions
        print('OBJ',o.name,'|',[s.material.name if s.material else '' for s in o.material_slots],'|',round(d.x),round(d.y),'|',tuple(round(v) for v in o.location),'hide',o.hide_render,'v',len(o.data.vertices))
