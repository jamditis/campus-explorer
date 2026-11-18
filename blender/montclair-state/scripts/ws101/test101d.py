import bpy
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(p) as (s,d): d.objects=['WS73_curb_back_lawn_verge_UNVERIFIED','WS27_CollegeAve_curb_left_UNVERIFIED']
for o in d.objects: bpy.context.scene.collection.objects.link(o)
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws101/apply101d.py').read())
