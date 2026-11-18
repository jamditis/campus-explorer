# pg: Feliciano bay above the entrance pavilion. LiDAR roof shards (wall-material faces sloping 137-160 m in front of the facade, x -218.2..-209.8, y 166..174.6)
# are moved to a hidden-by-delete? NO: reversible -> faces split off into a separate HIDDEN object PG_feliciano_roof_shards_removed (render off) and deleted from the roof mesh,
# old mesh kept with fake user (prop pg_prev_mesh). Adds a stucco infill facade block at the west-facade line (y~174.3) from the pavilion top to 161.5 m + an east cheek,
# and moves the ported 'windows over the entrance pavilion' back onto it. ALL UNVERIFIED (photo pref_feliciano_07/08: one flat facade plane rises behind the pavilion). REVERT=1 undoes.
import bpy,bmesh,os,sys
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'
r=bpy.data.objects['Feliciano School of Business roof (LiDAR)']
WIN=bpy.data.objects['Feliciano windows over the entrance pavilion (photo 08/09)']
COLN='PG_Feliciano_bay_infill_20261101pg_UNVERIFIED'
def clear():
    c=bpy.data.collections.get(COLN)
    if c:
        for o in list(c.objects): bpy.data.objects.remove(o,do_unlink=True)
        bpy.data.collections.remove(c)
    if 'pg_prev_mesh' in r:
        old=bpy.data.meshes[r['pg_prev_mesh']]; cur=r.data; r.data=old; old.use_fake_user=False
        if cur.users==0: bpy.data.meshes.remove(cur)
        del r['pg_prev_mesh']
    if 'pg_orig_loc' in WIN:
        WIN.location=Vector(WIN['pg_orig_loc']); del WIN['pg_orig_loc']
clear()
if not REV:
    col=bpy.data.collections.new(COLN); bpy.context.scene.collection.children.link(col)
    mw=r.matrix_world; old=r.data; new=old.copy(); new.name=old.name+'_pg'
    old.use_fake_user=True; r['pg_prev_mesh']=old.name; r.data=new
    bm=bmesh.new(); bm.from_mesh(new); bm.faces.ensure_lookup_table()
    kill=[f for f in bm.faces if (lambda c,nz:(-218.2<c.x<-209.8 and 166.0<c.y<174.6 and (c.z<160.0 or (c.z<163.0 and abs(nz)<0.5))))(mw@f.calc_center_median(),(mw.to_3x3()@f.normal).normalized().z)]
    print('PG_KILL',len(kill))
    bmesh.ops.delete(bm,geom=kill,context='FACES'); bm.to_mesh(new); bm.free()
    st=bpy.data.materials['North_Feliciano_stucco_white']
    def box(name,x0,x1,y0,y1,z0,z1):
        me=bpy.data.meshes.new(name); bm=bmesh.new()
        bmesh.ops.create_cube(bm,size=1.0); 
        for v in bm.verts:
            v.co.x=x0 if v.co.x<0 else x1; v.co.y=y0 if v.co.y<0 else y1; v.co.z=z0 if v.co.z<0 else z1
        bm.to_mesh(me); bm.free(); me.materials.append(st)
        o=bpy.data.objects.new(name,me); col.objects.link(o); o['UNVERIFIED_pg']='bay infill behind Feliciano pavilion (photo 07/08), position from LiDAR shards'; return o
    # facade line y = 174.2 at x=-218.6 with normal (0.06,1): y(x)=174.2+0.06*(-218.6-x)*-1 ~ small; use mean 174.25 front
    box('PG_feliciano_bay_infill_facade',-218.15,-209.75,174.25,174.65,144.4,161.5)
    box('PG_feliciano_bay_infill_east_cheek',-210.95,-209.75,167.15,174.65,144.0,161.5)
    WIN['pg_orig_loc']=list(WIN.location)
    WIN.location.y += 174.27-167.5   # windows' back plane (167.5) onto the infill face
    print('PG_WIN',tuple(WIN.location))
if '--save' in sys.argv: bpy.ops.wm.save_mainfile()
print('PG_BAY_DONE',REV)
