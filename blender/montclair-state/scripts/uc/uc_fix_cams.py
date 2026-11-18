"""Re-aim UC cams at Finley Hall bbox x[-64,-15] y[88,125] roof~146.2; save."""
import bpy, os
from mathutils import Vector

# Finley centre ~ (-40, 106), roof 146.2
fin = bpy.data.objects['Finley Hall walls']
xs=[]; ys=[]; zs=[]
mw=fin.matrix_world
for v in fin.data.vertices:
    c=mw@v.co; xs.append(c.x); ys.append(c.y); zs.append(c.z)
print('Finley bb', min(xs),max(xs), min(ys),max(ys), min(zs),max(zs))
cx=(min(xs)+max(xs))/2; cy=(min(ys)+max(ys))/2; cz=max(zs)
print('centre', cx, cy, cz)

# Also list nearby building names for sanity
for o in bpy.data.objects:
    if o.type!='MESH' or 'walls' not in o.name.lower(): continue
    if not o.name.endswith(' walls'): continue
    ox=[(o.matrix_world@v.co).x for v in o.data.vertices]
    oy=[(o.matrix_world@v.co).y for v in o.data.vertices]
    if max(ox)<-100 or min(ox)>50: continue
    if max(oy)<50 or min(oy)>160: continue
    print(f'  near {o.name!r} x[{min(ox):.0f},{max(ox):.0f}] y[{min(oy):.0f},{max(oy):.0f}]')

specs = {
    # oblique SW looking NE at Finley
    'UC_CAM_oblique_Finley_area_from_SW': ((cx-55, cy-70, cz+35), (cx, cy, cz-1), 32),
    # eye south of Finley looking north at S facade
    'UC_CAM_eye_Finley_from_S': ((cx, cy-35, 141.5), (cx, cy, 145.5), 35),
    # eye east looking west at E facade
    'UC_CAM_eye_Finley_from_E': ((cx+40, cy, 142.0), (cx, cy, 145.5), 35),
    # closeup of SE wall top meeting roof
    'UC_CAM_closeup_Finley_wall_top': ((max(xs)+8, min(ys)-5, cz+4), (max(xs)-2, min(ys)+8, cz), 45),
}
for n,(p,t,l) in specs.items():
    o=bpy.data.objects.get(n)
    if not o:
        cd=bpy.data.cameras.new(n); o=bpy.data.objects.new(n,cd)
        bpy.context.scene.collection.objects.link(o); o['uc_obj']=1
    o.location=p
    o.rotation_euler=(Vector(t)-Vector(p)).to_track_quat('-Z','Y').to_euler()
    o.data.lens=l
    print('aimed', n, 'loc', tuple(round(x,1) for x in p), 'tgt', tuple(round(x,1) for x in t))

# Also add/aim a Freeman parapet closeup for secondary WIP option — replace eye_E with Freeman parapet eye if Finley E is blocked
# Keep 4 Finley cams; add 5th optional not rendered unless needed
name='UC_CAM_closeup_Freeman_parapet'
if name not in bpy.data.objects:
    cd=bpy.data.cameras.new(name); o=bpy.data.objects.new(name,cd)
    bpy.context.scene.collection.objects.link(o); o['uc_obj']=1
else:
    o=bpy.data.objects[name]
fr=bpy.data.objects['Freeman Hall roof (LiDAR)']
fx=[(fr.matrix_world@v.co).x for v in fr.data.vertices]
fy=[(fr.matrix_world@v.co).y for v in fr.data.vertices]
fz=(fr.matrix_world@fr.data.vertices[0].co).z
fcx,fcy=(min(fx)+max(fx))/2,(min(fy)+max(fy))/2
o.location=(fcx-25, fcy-30, fz+8)
o.rotation_euler=(Vector((fcx, fcy, fz+0.3))-Vector(o.location)).to_track_quat('-Z','Y').to_euler()
o.data.lens=40
print('aimed', name)

bpy.ops.wm.save_mainfile(); print('SAVED')
