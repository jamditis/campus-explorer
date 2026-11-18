# ws111c: E walk rebuilt with a tree-lawn strip (ortho: dark strip + trunk between road and walk), taper to curb-tight at the apron
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
A=np.array([-244.8,-239.3]);B=np.array([-256.1,-271.6]);d=(B-A)/np.linalg.norm(B-A);n=np.array([d[1],-d[0]])
def st(x,y): return (x-A[0])*d[0]+(y-A[1])*d[1],(x-A[0])*n[0]+(y-A[1])*n[1]
def W(s,t): p=A+d*s+n*t; return float(p[0]),float(p[1])
O=lambda p: next(o for o in bpy.data.objects if o.name.startswith(p))
# trees near the E walk
trees=[]
for o in bpy.data.objects:
    if o.type in ('MESH','EMPTY') and o.name.startswith(('T_','Tree','WS','UA')) and ('Tree' in o.name or o.name.startswith('T_')):
        p=o.matrix_world.translation; s,t=st(p.x,p.y)
        if -2<s<17 and -12<t<-3.6: trees.append((o.name,round(s,2),round(t,2))); 
print('G111 trees',trees)
old=O('WS111_CollegeAve_S_E_walk'); wc=np.array([tuple(old.matrix_world@v.co) for v in old.data.vertices]); ws,wt=st(wc[:,0],wc[:,1])
# old rows: s -> (inner t, z inner)
cu=O('WS110_CollegeAve_S_end_curb_E'); mw=cu.matrix_world; me=cu.data
bk=np.array([tuple(mw@me.vertices[k+2].co) for k in range(0,len(me.vertices),4)]); sb,tb=st(bk[:,0],bk[:,1])
need=max([1.6]+[(-tt)-3.63+0.6 for nm,ss,tt in trees if ss<14])
print('G111 strip',round(need,2))
mats=list(old.data.materials); col=old.users_collection[0]; name=old.name
bpy.data.objects.remove(old)
ss=list(np.arange(4.39,16.0,0.5))+[16.0]
bm=bmesh.new(); top=[];bot=[]; WID=2.6
for s in ss:
    i=np.argmin(np.abs(sb-s)); zt=float(bk[i,2]); tback=float(tb[i])
    u=min(max((s-11.0)/5.0,0),1); u=u*u*(3-2*u); strip=need*(1-u); w=WID*(1-u)+2.7*u
    r=[]
    for f in (0,0.5,1):
        t=tback-strip-w*f; x,y=W(s,t); r.append(bm.verts.new((x,y,zt+0.02*(strip+w*f)+0.0)))
    x,y=W(s,tback-strip-w); rb=[bm.verts.new((x,y,zt+0.02*(strip+w)-0.30))]
    x,y=W(s,tback-strip); rb.append(bm.verts.new((x,y,zt+0.02*strip-0.30)))
    top.append(r); bot.append(rb)
for i in range(len(ss)-1):
    for j in range(2): bm.faces.new((top[i][j],top[i][j+1],top[i+1][j+1],top[i+1][j]))
    bm.faces.new((top[i][2],bot[i][0],bot[i+1][0],top[i+1][2])); bm.faces.new((top[i][0],top[i+1][0],bot[i+1][1],bot[i][1]))
# start end cap
bm.faces.new((top[0][0],bot[0][1],bot[0][0],top[0][2],top[0][1]))
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
me2=bpy.data.meshes.new(name); bm.to_mesh(me2); bm.free()
for m in mats: me2.materials.append(m)
ob=bpy.data.objects.new(name,me2); col.objects.link(ob)
# strip: lawn faces between curb back and walk inner edge, s 4.39..15
lawn=bpy.data.materials.get('COLE_lawn_post2020_bs')
bm=bmesh.new(); rows=[]
for s in ss:
    if s>15.5: break
    i=np.argmin(np.abs(sb-s)); zt=float(bk[i,2]); tback=float(tb[i])
    u=min(max((s-11.0)/5.0,0),1); u=u*u*(3-2*u); strip=need*(1-u)
    r=[]
    for f in (0,0.5,1):
        t=tback-strip*f; x,y=W(s,t); r.append(bm.verts.new((x,y,zt-0.04+0.0*f)))
    rows.append(r)
for i in range(len(rows)-1):
    for j in range(2): bm.faces.new((rows[i][j],rows[i][j+1],rows[i+1][j+1],rows[i+1][j]))
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
for f in bm.faces:
    if f.normal.z<0: f.normal_flip()
me3=bpy.data.meshes.new('WS111_CollegeAve_S_E_tree_lawn_strip_ortho2020_UNVERIFIEDwidth'); bm.to_mesh(me3); bm.free(); me3.materials.append(lawn)
o3=bpy.data.objects.new(me3.name,me3); col.objects.link(o3)
print('G111 rebuilt',name,len(me2.vertices),'strip obj',len(me3.vertices))
bpy.ops.wm.save_mainfile(); print('G111 SAVED')
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws111/cut111.py').read())
