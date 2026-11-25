# ws243: rename the slice-5 hold-under modifiers so the subset renderer (TRX 'terrain' rule) keeps them ON, like the real file.
import bpy
k=0
for o in bpy.data.objects:
    for m in o.modifiers:
        if m.name.startswith('WS243_under_stands_pitch'):
            for i,(a,b) in enumerate(_OFF):
                if a==o.name and b==m.name: _OFF[i]=(a,'WS243_terrain_hold_under_stands_pitch')
            m.name='WS243_terrain_hold_under_stands_pitch'; k+=1
print('F243B renamed',k,flush=True)
