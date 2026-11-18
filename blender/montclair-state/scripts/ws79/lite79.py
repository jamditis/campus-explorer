import bpy,os,bmesh
from mathutils import Vector
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws72/lite_load.py').read())
sc=bpy.context.scene
with bpy.data.libraries.load(src,link=False) as (fr,to): to.worlds=['WP2_World_GOLDEN']; to.objects=['WP2_Sun_GOLDEN']
for o in bpy.data.objects:
    if o.name=='WP2_Sun_GOLDEN' and o.name not in sc.objects: sc.collection.objects.link(o)
for m in bpy.data.objects['Terrain_LiDAR_DTM_1m'].modifiers:
    if m.name.startswith('WS64'): m.show_viewport=False; m.show_render=False
s=open('/workspace/nj-scenes/montclair-state/scripts/ws59/render59.py').read()
ground=['Terrain_LiDAR_DTM_1m']+[o.name for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground')][:1]
s=s.replace("('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km')",repr(tuple(ground)),1)
cut=s.index("camz('WS49"); end=s.index("base=bpy.data.objects.get('Sun')")
s=s[:cut]+open('/workspace/nj-scenes/montclair-state/scripts/ws79/cams79.py').read()+s[end:]
pre,loop=s.split("ts=datetime.now()",1)
exec(compile(pre,'pre','exec'))
def go(cams,tag):
    os.environ['CAMS']=cams; os.environ['OUT_TAG']=tag
    exec(compile("ts=datetime.now()"+loop,'loop','exec'),globals())
if os.environ.get('INFO')=='1':
    fp=bpy.data.objects['Footpaths_OSM']; mw=fp.matrix_world
    n=0
    for p in fp.data.polygons:
        c=mw@p.center
        if -226<c.x<-205 and -92<c.y<-74: n+=1; print('FPF',p.index,round(c.x,2),round(c.y,2),round(c.z,2),round(p.area,2))
    print('FP count',n)
    for o in sc.objects:
        if o.name.startswith(('WS76','WS75','WS77')): 
            bb=[o.matrix_world@Vector(c) for c in o.bound_box]; print('BB',o.name,round(min(v.x for v in bb),1),round(max(v.x for v in bb),1),round(min(v.y for v in bb),1),round(max(v.y for v in bb),1))
if os.environ.get('BEFORE_CAMS'): go(os.environ['BEFORE_CAMS'],os.environ.get('BEFORE_TAG','ws79L_before'))
if os.environ.get('APPLYF'):
    for f in os.environ['APPLYF'].split(','): exec(open('/workspace/nj-scenes/montclair-state/scripts/ws79/'+f).read())
if os.environ.get('AFTER_CAMS'): go(os.environ['AFTER_CAMS'],os.environ.get('AFTER_TAG','ws79L_after'))
