import bpy
from mathutils import Vector
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws152/facade152.py').read())
planes=[]
for N,S,sg in [(W_N,W_S,1),(E_N,E_S,-1)]:
    u=(S-N).normalized(); n=Vector((u.y,-u.x))*sg; planes.append((N,u,n,(S-N).length))
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or o.name.startswith('WS152'): continue
    mw=o.matrix_world; vs=[mw@v.co for v in o.data.vertices]
    if not vs: continue
    for k,(N,u,n,L) in enumerate(planes):
        out=[v for v in vs if 0.03<(v.xy-N).dot(n)<3.0 and -0.3<(v.xy-N).dot(u)<L+0.3 and v.z>128.5]
        if len(out)>3: print('PROBE153','WE'[k],o.name,len(vs),len(out),round(max((v.xy-N).dot(n) for v in out),2))
