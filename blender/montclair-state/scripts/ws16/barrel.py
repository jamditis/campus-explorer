import bpy, bmesh, math
from mathutils import Vector
o=bpy.data.objects['TZ_Cole_north_addition_UNVERIFIED']; mw=o.matrix_world; me=o.data
bm=bmesh.new(); R=0.105; L=0.42; SP=0.26; SEG=6
for fi in (4,10):
    p=me.polygons[fi]; vs=sorted([mw@me.vertices[v].co for v in p.vertices], key=lambda w:w.z)
    a,b=vs[0],vs[1]; ridge=(vs[2]+vs[3])/2; eave=(a+b)/2
    t=(b-a); length=t.length; t.normalize()
    up=(ridge-eave); up=up-t*up.dot(t); up.normalize()      # up-slope dir in roof plane
    n=t.cross(up);  n = n if n.z>0 else -n                   # roof normal (upward)
    cnt=int(length/SP)
    for i in range(cnt):
        c=a+t*(SP*(i+0.5)) - up*0.04 + n*0.005
        ring0=[];ring1=[]
        for s in range(SEG+1):
            ang=math.pi*s/SEG
            off=t*(R*math.cos(ang))+n*(R*math.sin(ang)*0.9)
            ring0.append(bm.verts.new(c+off)); ring1.append(bm.verts.new(c+off+up*L))
        for s in range(SEG):
            bm.faces.new((ring0[s],ring0[s+1],ring1[s+1],ring1[s]))
        bm.faces.new(ring0[::-1])  # open-end cap at eave
    print('EAVE',fi,round(length,2),cnt)
nm=bpy.data.meshes.new('WS16_Cole_addition_barrel_eave_course_UNVERIFIED'); bm.to_mesh(nm); bm.free()
ob=bpy.data.objects.new(nm.name,nm); nm.materials.append(bpy.data.materials['Roof_barrel_tile_course'])
for poly in nm.polygons: poly.use_smooth=True
(o.users_collection[0]).objects.link(ob)
print('FACES',len(nm.polygons)); bpy.ops.wm.save_mainfile(); print('SAVED')
