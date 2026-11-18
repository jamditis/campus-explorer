import bpy,os
from mathutils import Vector
P='/workspace/nj-scenes/montclair-state/scripts/ws127/cut127.blend'
with bpy.data.libraries.load(P) as (df,dt):
    names=list(df.objects)
    print('NOBJ',len(names))
    pre=('WS112','WS111','WS102_CollegeAve_S_curb_E','WS113_terrain_fan_fill','WS127_CollegeAve_E_curbside_bed','WS115','WS110_ground','WS113_paving')
    dt.objects=[n for n in names if n.startswith(pre)]
open('/workspace/nj-scenes/montclair-state/scripts/ws128/names.txt','w').write('\n'.join(names))
X0,X1,Y0,Y1=-244,-230,-248,-230
for o in dt.objects:
    if o is None or o.type!='MESH': continue
    mw=o.matrix_world
    vs=[mw@v.co for v in o.data.vertices]; vs=[v for v in vs if X0<v.x<X1 and Y0<v.y<Y1]
    if not vs: continue
    print('OBJ',o.name,len(vs),'z',round(min(v.z for v in vs),2),round(max(v.z for v in vs),2),'x',round(min(v.x for v in vs),2),round(max(v.x for v in vs),2),'y',round(min(v.y for v in vs),2),round(max(v.y for v in vs),2),[m.name for m in o.data.materials if m][:4], [m.type for m in o.modifiers])
