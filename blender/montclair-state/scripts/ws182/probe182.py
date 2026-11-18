import bpy, bmesh, numpy as np
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(p) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(('WS167','WS162','WS163_ground','WS169c'))]
sc=bpy.context.scene
for o in b.objects:
    if o and o.type=='MESH': sc.collection.objects.link(o)
for o in b.objects:
    if not o or o.type!='MESH': continue
    M=o.matrix_world; bm=bmesh.new(); bm.from_mesh(o.data)
    vs=[M@v.co for v in bm.verts if -326<(M@v.co).x<-306 and -222<(M@v.co).y<-206]
    bnd=[M@v.co for v in bm.verts if v.is_boundary and -326<(M@v.co).x<-306 and -224<(M@v.co).y<-204]
    if vs: print('OBJ',o.name,len(o.data.vertices),'win',len(vs),'bnd',len(bnd),[m.name for m in o.data.materials][:3])
    if 'service' in o.name.lower() or 'lane' in o.name.lower():
        for v in sorted(bnd,key=lambda v:v.y): print('  B %.2f %.2f %.3f'%(v.x,v.y,v.z))
