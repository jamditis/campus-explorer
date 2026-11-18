# ws124: (1) UNIFY #30 – landing S-end gap to the S-wing face (0.38 m strip where the WS113 fan fill dropped 0.6 m = dark wedge, plus 3 Footpaths_OSM residue faces at 124.85 poking 8 cm above the terrace = pale shards) -> retire residue, extend the landing slab to the wing face;
# (2) door glass: transmissive glass let the wall/transom light show through the left leaf -> dedicated opaque reflective storefront glass;
# (3) canopy: precast coping cap with drip overhang on the WS117 canopy slab + 2 flush soffit downlights (UNVERIFIED fixtures).
import bpy, bmesh, os
from mathutils import Vector
def ob(p): return next(o for o in bpy.data.objects if o.name.startswith(p))
# (1a) retire Footpaths residue in the recess strip
fp=bpy.data.objects['Footpaths_OSM']; mw=fp.matrix_world
bm=bmesh.new(); bm.from_mesh(fp.data)
kill=[f for f in bm.faces if (lambda c:-212<c.x<-207 and -204<c.y<-200.3)(mw@f.calc_center_median())]
print('M124 FP retire',len(kill)); bmesh.ops.delete(bm,geom=kill,context='FACES'); bm.to_mesh(fp.data); bm.free(); fp.data.update()
# (1b) landing strip slab to the S-wing N face
land=ob('WS117_Chapin_W_entrance_landing_terrace'); col=land.users_collection[0]
bm=bmesh.new()
def box(x0,x1,y0,y1,z0,z1,mi=0):
    r=bmesh.ops.create_cube(bm,size=1.0); vs=r['verts']
    for v in vs:
        v.co.x=x0 if v.co.x<0 else x1; v.co.y=y0 if v.co.y<0 else y1; v.co.z=z0 if v.co.z<0 else z1
    for f in {f for v in vs for f in v.link_faces}: f.material_index=mi
box(-213.40,-209.10,-201.78,-201.28,124.52,124.77)
me=bpy.data.meshes.new('WS124_Chapin_W_landing_S_strip_to_S_wing_face_UNIFY30'); bm.to_mesh(me); bm.free()
for m in land.data.materials: me.materials.append(m)
o=bpy.data.objects.new(me.name,me); col.objects.link(o)
# lower the fan fill inside the strip so it can't show through
ff=ob('WS113_terrain_fan_fill'); fm=ff.matrix_world; inv=fm.inverted(); n=0
for v in ff.data.vertices:
    w=fm@v.co
    if -213.6<w.x<-209.0 and -201.9<w.y<-201.2 and w.z>124.45: w.z=124.45; v.co=inv@w; n+=1
ff.data.update(); print('M124 fanfill lowered',n)
# (2) opaque storefront glass on the doors
d=ob('WS123_Chapin_W_entrance_storefront_doors')
g=bpy.data.materials.get('WS124_storefront_glass_opaque_reflective') or bpy.data.materials.new('WS124_storefront_glass_opaque_reflective')
g.use_nodes=True; b=g.node_tree.nodes.get('Principled BSDF')
b.inputs['Base Color'].default_value=(0.018,0.022,0.026,1); b.inputs['Metallic'].default_value=0.0; b.inputs['Roughness'].default_value=0.05
for k in ('Transmission Weight','Transmission'):
    if k in b.inputs: b.inputs[k].default_value=0.0
for k in ('Specular IOR Level','Specular'):
    if k in b.inputs: b.inputs[k].default_value=0.8
d.data.materials[1]=g
# also push the dark back panel to cover the full opening (y and z 1 cm beyond the frame)
# (3) canopy coping + downlights
cp=ob('WS117_Chapin_W_entrance_frame_canopy'); ccol=cp.users_collection[0]
coping=bpy.data.materials.get('WS119_precast_coping') or next((m for o2 in bpy.data.objects if o2.name.startswith('WS119_Chapin_W_terrace_wall_coping') for m in o2.data.materials if m),None)
bm=bmesh.new()
box(-212.56,-209.05,-201.31,-196.69,130.40,130.46)     # cap, 6 cm proud W/N/S
box(-212.56,-212.53,-201.31,-196.69,130.33,130.40)     # drip lip W
box(-212.56,-209.05,-201.31,-201.28,130.33,130.40)     # drip lip S
box(-212.56,-209.05,-196.72,-196.69,130.33,130.40)     # drip lip N
me=bpy.data.meshes.new('WS124_Chapin_W_canopy_precast_coping_drip_UNVERIFIED'); bm.to_mesh(me); bm.free()
me.materials.append(coping); oc=bpy.data.objects.new(me.name,me); ccol.objects.link(oc)
bm=bmesh.new()
for y in (-200.0,-198.0):
    bmesh.ops.create_circle(bm,cap_ends=True,radius=0.09,segments=16,matrix=__import__('mathutils').Matrix.Translation((-210.9,y,130.045)))
bmesh.ops.reverse_faces(bm,faces=bm.faces[:])
me=bpy.data.meshes.new('WS124_Chapin_W_canopy_soffit_downlights_UNVERIFIED'); bm.to_mesh(me); bm.free()
L=bpy.data.materials.get('WS124_downlight_warm') or bpy.data.materials.new('WS124_downlight_warm')
L.use_nodes=True; lb=L.node_tree.nodes.get('Principled BSDF'); lb.inputs['Base Color'].default_value=(0.9,0.85,0.75,1)
lb.inputs['Emission Color'].default_value=(1.0,0.86,0.66,1); lb.inputs['Emission Strength'].default_value=3.0
me.materials.append(L); ol=bpy.data.objects.new(me.name,me); ccol.objects.link(ol)
print('M124 coping mat',coping.name if coping else None)
SAVE=os.environ.get('SAVE','main')
if SAVE=='main': bpy.ops.wm.save_mainfile(); print('M124 SAVED main')
else: bpy.ops.wm.save_as_mainfile(filepath=SAVE,copy=True); print('M124 SAVED',SAVE)
