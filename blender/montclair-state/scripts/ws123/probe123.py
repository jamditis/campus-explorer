import bpy
for o in bpy.data.objects:
    n=o.name
    if any(k in n for k in ('WS120','WS121','WS117','WS113_paving')):
        print('P',n,o.type,len(o.data.polygons) if o.type=='MESH' else '',[m.type for m in o.modifiers], o.hide_render)
with bpy.data.libraries.load('/workspace/nj-scenes/assets/campus_assets.blend') as (df,dt):
    print('ASSET objs',[x for x in df.objects if any(k in x.lower() for k in ('tree','shrub','maple','oak','ornament','cherry'))][:60])
    print('ASSET colls',[x for x in df.collections][:80])
