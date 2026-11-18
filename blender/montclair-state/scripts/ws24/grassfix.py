import bpy,bmesh
P=[(-97.3,303.5),(-97.3,341),(-98.5,346),(-101,353),(-102,360),(-117,360),(-116,353),(-119,348),(-125,342),(-138,339.5),(-138,336.5),(-128,335.5),(-120,333.5),(-115,330),(-112.8,325),(-112.6,319),(-113.5,314),(-112,309),(-111.5,304),(-108,302.5),(-101,302.8)]
def inside(x,y,poly=P):
    c=False; n=len(poly)
    for i in range(n):
        x1,y1=poly[i]; x2,y2=poly[(i+1)%n]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1: c=not c
    return c
for o in bpy.data.objects:
    if o.type=='MESH' and len(o.data.polygons)==0 and len(o.data.vertices)>0 and not o.name.startswith('mi_grass_annex_west_bed'):
        mw=o.matrix_world; bm=bmesh.new(); bm.from_mesh(o.data)
        kill=[v for v in bm.verts if inside(*(mw@v.co).xy)]
        if kill:
            print('pts',o.name,len(kill),'of',len(bm.verts)); bmesh.ops.delete(bm,geom=kill,context='VERTS'); bm.to_mesh(o.data)
        bm.free()
# list GN modifiers on terrain-ish objects overlapping (scatter)
for o in bpy.data.objects:
    for m in o.modifiers:
        if m.type=='NODES' and m.node_group and ('grass' in m.node_group.name.lower() or 'scatter' in m.node_group.name.lower()) and not o.hide_render:
            print('GN',o.name,m.name,m.node_group.name)
bpy.ops.wm.save_mainfile(); print('SAVED')
