# ws72 lite render: chunked append of objects in CULL (lite_load), golden world/sun; optional BEFORE pass, then walk72 (no save) AFTER pass
import bpy,os
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws72/lite_load.py').read())
src=os.environ.get('SRC','/workspace/nj-scenes/montclair-state/montclair_state.blend')
sc=bpy.context.scene
KEEP=tuple(os.environ.get('KEEP','').split(','))
if os.environ.get('KEEP'):
    for o in list(bpy.data.objects):
        if o.type=='MESH' and not o.name.startswith(KEEP) and 'DTM_target' not in o.name: bpy.data.objects.remove(o)
    bpy.data.orphans_purge(do_recursive=True)
with bpy.data.libraries.load(src,link=False) as (fr,to): to.worlds=['WP2_World_GOLDEN']; to.objects=['WP2_Sun_GOLDEN']
print('LR after keep',len(sc.objects),flush=True)
for o in list(bpy.data.objects):
    if o.name[-4:-3]=='.' and o.name[-3:].isdigit() and o.type=='MESH' and o.name[:-4] in bpy.data.objects: bpy.data.objects.remove(o)
for o in bpy.data.objects:
    if o.name=='WP2_Sun_GOLDEN' and o.name not in sc.objects: sc.collection.objects.link(o)
for m in bpy.data.objects['Terrain_LiDAR_DTM_1m'].modifiers:
    if m.name.startswith('WS64'): m.show_viewport=False; m.show_render=False
s=open('/workspace/nj-scenes/montclair-state/scripts/ws59/render59.py').read()
ground=[n for n in ('Terrain_LiDAR_DTM_1m',)]+[o.name for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground')][:1]
s=s.replace("('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km')",repr(tuple(ground)),1)
cut=s.index("camz('WS49"); end=s.index("base=bpy.data.objects.get('Sun')")
cams="""camz('WS72_CAM_eye_CollegeAve_W_from_Kasser_frontage_E',(-198,-74,0),(-252,-52),28,1.7,1.5)
camz('WS73_CAM_closeup_north_curb_bend',(-197,-76,0),(-205,-65),28,1.7,0.2)
camz('WS73_CAM_top_north_curb_bend',(-203,-68,0),(-202.6,-66),30,22.0,0.0)
camz('WS73_CAM_closeup_south_curb',(-226,-62,0),(-240,-64.5),28,1.6,0.2)
"""
s=s[:cut]+cams+s[end:]
pre,loop=s.split("ts=datetime.now()",1)
exec(compile(pre,'r59pre','exec'))
def go(cams,tag):
    os.environ['CAMS']=cams; os.environ['OUT_TAG']=tag
    exec(compile("ts=datetime.now()"+loop,'r59loop','exec'),globals())
if os.environ.get('BEFORE_CAMS'): go(os.environ['BEFORE_CAMS'],'ws72_lite_before')
if os.environ.get('APPLY')=='1':
    pass
if os.environ.get('AFTER_CAMS'): go(os.environ['AFTER_CAMS'],os.environ.get('AFTER_TAG','ws72_lite_after'))
