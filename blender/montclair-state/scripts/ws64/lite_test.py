import bpy,os
src='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(src,link=False) as (fr,to): to.collections=['Terrain']
bpy.context.scene.collection.children.link(to.collections[0])
os.environ.pop('SAVE',None)
exec(open(os.environ['APPLY']).read())
