import bpy,os,runpy
names=os.environ['NAMES'].split('|')
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend') as (s,d):
    d.objects=[n for n in s.objects if n in names]
for o in d.objects: bpy.context.scene.collection.objects.link(o)
runpy.run_path('/workspace/nj-scenes/montclair-state/scripts/ws89/apply89.py')
if os.environ.get('OUT'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUT'])
