# ws260 probe (subset CHAIN via subrend234, terrain GN on, crop259, exits before render): evaluated hits near the pit seen in the ws260a eye-from-N view
import bpy
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws259/crop259.py').read())
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for y in (-215,-214,-213,-212,-211,-210,-209,-208,-207,-206,-205):
    row=[]
    for x in (-253,-252,-251,-250,-249,-248,-247,-246):
        o0=Vector((x+0.25,y+0.25,200)); hs=[]
        for k in range(4):
            r=sc.ray_cast(dg,o0,Vector((0,0,-1)))
            if not r[0]: break
            if not r[4].name.startswith('T_'): hs.append('%s@%.2f'%(r[4].name[:12],r[1].z))
            o0=r[1]+Vector((0,0,-0.001))
            if len(hs)>=2: break
        row.append('%d:%s'%(x,'/'.join(hs)))
    print('P260B y',y,' | '.join(row),flush=True)
raise SystemExit
