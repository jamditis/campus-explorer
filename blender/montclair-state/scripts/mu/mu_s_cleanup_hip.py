# Session mu: S side cleanup - remove leftover eave stubs inside the S return zone (u 2.361..3.19) and make the S tile cap a hipped return
# (outer end drops to eave level so no end board stands above the roof; inner end rises to cover the trimmed LiDAR roof hole under the gable rake).
import bpy, bmesh
from mathutils import Vector
n=Vector((-0.972,0.232,0)).normalized(); t=Vector((0.232,0.972,0)).normalized()
def P(u,z,w): v=t*u+n*w; return Vector((v.x,v.y,z))
US,U0=2.361,3.197
for nm in ['Eave drip / moss streaks on stucco (3g)','el coping strips School of Communication and Media (generic, UN','School of Communication and Media barrel tile eave course','School of Communication and Media eave soffit + fascia + rafter']:
    o=[x for x in bpy.data.objects if x.name.startswith(nm)][0]; mw=o.matrix_world; mi=mw.inverted()
    bm=bmesh.new(); bm.from_mesh(o.data)
    def inb(c): u=c.dot(t); w=c.dot(n); return US+0.002<u<U0+0.7 and 21.9<w<23.4 and 146.4<c.z<147.9
    pre=sum(1 for f in bm.faces if inb(mw@f.calc_center_median()))
    r=bmesh.ops.bisect_plane(bm,geom=bm.verts[:]+bm.edges[:]+bm.faces[:],dist=0.0005,plane_co=mi@P(US,147,22.6),plane_no=(mw.to_3x3().transposed()@t).normalized())
    kill=[f for f in bm.faces if inb(mw@f.calc_center_median())]
    bmesh.ops.delete(bm,geom=kill,context='FACES')
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
    bm.to_mesh(o.data); o.data.update(); bm.free(); print('CLEAN',o.name[:50],'pre',pre,'killed',len(kill),'cutgeom',len(r['geom_cut']))
o=bpy.data.objects['CCOM gable eave return S tile cap (mu)']
ua,ub=US-0.004,U0-0.006
outer=[(21.40,146.985),(23.06,146.985),(23.06,147.165),(21.40,147.165)]
inner=[(21.40,146.985),(23.06,146.985),(23.06,147.165),(21.40,147.36+(22.73-21.40)*0.59)]
vs=[P(ua,z,w) for w,z in outer]+[P(ub,z,w) for w,z in inner]
fs=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
me=o.data; me.clear_geometry(); me.from_pydata([tuple(v) for v in vs],[],fs); me.update()
bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
for p in me.polygons:
    p.use_smooth=False; p.material_index=1 if abs((o.matrix_world.to_3x3()@p.normal).normalized().dot(t))>0.9 else 0
print('HIP',len(me.polygons))
print('COUNT',len(bpy.data.objects)); bpy.ops.wm.save_mainfile(); print('SAVED')
