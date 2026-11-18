import bpy, bmesh
from mathutils import Vector
sc=bpy.context.scene
pc=bpy.data.collections['WS4_Cole_walk_kit_20261109']
s=bpy.data.objects['WS4_Sign_Wayfinding_ColeHall_UNVERIFIED_POS']; r=bpy.data.objects['WS4_RiverRock_strip_sign_bed_UNVERIFIED_POS']
x0,y0,z0=s.location; zw=z0+0.08  # walk top
X=(x0-1.9,x0+1.9); Y=(-53.28,y0+0.75)
def box(p): return X[0]<p.x<X[1] and Y[0]<p.y<Y[1]
for n in ('cx_grass_points','Lawn_grass_instanced (3g)'):
  o=bpy.data.objects.get(n)
  if not o: continue
  mw=o.matrix_world; bm=bmesh.new(); bm.from_mesh(o.data)
  vs=[v for v in bm.verts if box(mw@v.co)]; bmesh.ops.delete(bm,geom=vs,context='VERTS'); bm.to_mesh(o.data); bm.free(); print('GRASSDEL',n,len(vs))
bm=bmesh.new()
bmesh.ops.create_grid(bm,x_segments=8,y_segments=4,size=0.5)
for v in bm.verts:
  v.co.x=X[0]+(v.co.x+0.5)*(X[1]-X[0]); v.co.y=Y[0]+(v.co.y+0.5)*(Y[1]-Y[0]); v.co.z=zw-0.045
me=bpy.data.meshes.new('WS4_sign_bed'); bm.to_mesh(me); bm.free()
me.materials.append(bpy.data.materials['WS3_Mulch_bark_dark_brown'])
o=bpy.data.objects.new('WS4_Planting_bed_mulch_at_Cole_sign_UNVERIFIED',me); pc.objects.link(o)
so=o.modifiers.new('skirt','SOLIDIFY'); so.thickness=0.12; so.offset=-1
r.location=(x0,-52.95,zw-0.035); r.scale=(1.2,1,1)
print('BED',X,Y,zw)
bpy.ops.wm.save_mainfile(); print('SAVED')
