import bpy
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend') as (s,d):
    n=[x for x in s.objects if any(k in x.lower() for k in ('backdrop','dem','context','far','ground','band','street_tree','streettree'))]
    print('N48',n[:80])
    import collections; print('N48T',collections.Counter(x.split('_')[0]+'_'+x.split('_')[1] for x in s.objects if x.startswith('T_')).most_common(10))
