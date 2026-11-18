import bpy, math
from mathutils import Vector
M='/workspace/nj-scenes/montclair-state/'
th=math.radians(76.8); A=Vector((math.cos(th),math.sin(th),0)); B=Vector((math.cos(th-math.pi/2),math.sin(th-math.pi/2),0)); O=Vector((-238.1,-180.2,0))
def AB(v): w=Vector((v.x,v.y,0))-O; return w.dot(A), w.dot(B)
with bpy.data.libraries.load(M+'montclair_state.blend',link=False) as (src,dst):
    names=[n for n in src.objects if n.startswith(('WS105','WS159','WS158_Panzer_gym','Terrain','WS110')) or 'PanzerE' in n]
    print('PROBE names',names)
    dst.objects=names
for o in dst.objects:
    if o is None or o.type!='MESH': continue
    mw=o.matrix_world; me=o.data
    inz=[]
    for v in me.vertices:
        c=mw@v.co; a,b=AB(c)
        if 22<=a<=34 and -8<=b<=4: inz.append((round(a,2),round(b,2),round(c.z,3)))
    print('PROBE',o.name,len(me.vertices),'mats',[m.name for m in me.materials if m],'mods',[m.type for m in o.modifiers],'inzone',len(inz))
    if inz and len(inz)<80: print('   ',sorted(inz))
    elif inz:
        zs=[t[2] for t in inz]; print('    z',min(zs),max(zs))
