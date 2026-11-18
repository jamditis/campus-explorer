import bpy
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend') as (s,d): names=list(s.objects); ngs=list(s.node_groups)
open('/tmp/names164.txt','w').write('\n'.join(names)); print('N',len(names),len(ngs))
print([n for n in ngs if 'skirt' in n.lower()])
