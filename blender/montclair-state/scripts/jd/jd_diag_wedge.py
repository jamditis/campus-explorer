# Session jd diag (read-only): faces of Kasser_amphitheater_bowl_hl that project into a screen box of the jc close-up cam.
import bpy, bmesh, os, mathutils, collections
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; sc.render.resolution_x,sc.render.resolution_y=1280,720
L=mathutils.Vector((-165.3,7.2,134.5)); T=mathutils.Vector((-167.8,18,137.0))
cd=bpy.data.cameras.new('jdc'); cd.lens=32; o=bpy.data.objects.new('jdc',cd); sc.collection.objects.link(o)
o.location=L; o.rotation_euler=(T-L).to_track_quat('-Z','Y').to_euler(); bpy.context.view_layer.update()
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data; mw=ob.matrix_world
names=[s.material.name if s.material else '' for s in ob.material_slots]
X0,X1,Y0,Y1=[float(v) for v in os.environ.get('BOX','150,260,470,540').split(',')]  # px in 960x540 image, y from top
bm=bmesh.new(); bm.from_mesh(me); bm.normal_update()
lays={k:bm.faces.layers.int.get(k) for k in ('jb_chamfer','iy_wedge','jc_flatn')}
hits=[]
for f in bm.faces:
    c=mw@f.calc_center_median(); p=world_to_camera_view(sc,o,c)
    if p.z<=0: continue
    x=p.x*960; y=(1-p.y)*540
    if X0<=x<=X1 and Y0<=y<=Y1:
        # facing camera?
        if (L-c).dot(f.normal)<=0: continue
        hits.append((p.z,x,y,f))
hits.sort(key=lambda h:h[0])
print('JDD hits',len(hits))
for z,x,y,f in hits[:60]:
    c=mw@f.calc_center_median()
    print('JDD f%d'%f.index,'px',round(x),round(y),'d',round(z,2),'c',[round(v,3) for v in c],'n',[round(v,2) for v in f.normal],'A cm2',round(f.calc_area()*1e4,1),'nv',len(f.verts),names[f.material_index][:24],{k:(f[l] if l else None) for k,l in lays.items()})
