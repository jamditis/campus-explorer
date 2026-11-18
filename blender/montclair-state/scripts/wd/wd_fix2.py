# wd fix2: (a) WC base eggcrate cell sat over the Bohn W door (TK_Bohn_door_*_W_walk) -> delete overlay faces in the door span;
# (b) replace dark/occluded WD cams with low under-canopy views.
import bpy, bmesh, json, os
from mathutils import Vector
SAVE=os.environ.get('SAVE')=='1'
O=Vector((217.989,408.46,0)); U=Vector((0.3334,0.9428,0))
def tz(p): d=p-O; return d.x*U.x+d.y*U.y
dg=bpy.context.evaluated_depsgraph_get()
G=bpy.data.objects['TK_Bohn_door_glass_W_walk_UNVERIFIED']
gv=[G.matrix_world@v.co for v in G.data.vertices]
t0=min(tz(p) for p in gv); t1=max(tz(p) for p in gv); z0=min(p.z for p in gv); z1=max(p.z for p in gv)
fr=bpy.data.objects.get('TK_Bohn_door_frame_W_walk_UNVERIFIED')
if fr:
    fv=[fr.matrix_world@v.co for v in fr.data.vertices]; t0=min(t0,min(tz(p) for p in fv)); t1=max(t1,max(tz(p) for p in fv)); z1=max(z1,max(p.z for p in fv))
print('DOOR t',round(t0,2),round(t1,2),'z',round(z0,2),round(z1,2))
rep={}
for nm in ['WC_Bohn_NW_lower_W_glass_UNVERIFIED','WC_Bohn_NW_lower_W_reveals_UNVERIFIED','WC_Bohn_NW_lower_W_piers_bands_UNVERIFIED']:
    o=bpy.data.objects[nm]; mw=o.matrix_world
    bm=bmesh.new(); bm.from_mesh(o.data)
    # operate per connected island (each box) : delete islands whose centre lies in door rect
    bm.verts.ensure_lookup_table()
    seen=set(); kill=[]
    for v in bm.verts:
        if v.index in seen: continue
        stack=[v]; isl=[]
        while stack:
            x=stack.pop()
            if x.index in seen: continue
            seen.add(x.index); isl.append(x)
            for ed in x.link_edges: stack.append(ed.other_vert(x))
        P=[mw@q.co for q in isl]
        c=sum(P,Vector())/len(P); ct=tz(c)
        ts=[tz(p) for p in P]; zs=[p.z for p in P]
        if 'piers' in nm:
            # only horizontal bands fully crossing door span, below door head
            if (max(ts)-min(ts))>0.6 and min(zs)<z1-0.05 and max(zs)>z0 and t0-0.05<ct<t1+0.05 and (max(zs)-min(zs))<1.0:
                kill+=isl
        else:
            if t0-0.3<ct<t1+0.3 and z0-0.6<c.z<z1+0.3:
                kill+=isl
    rep[nm]=len(kill)
    bmesh.ops.delete(bm,geom=list(set(kill)),context='VERTS')
    bm.to_mesh(o.data); bm.free(); o.data.update()
print('REMOVED',rep)
# cams
for n in ['WD_CAM_closeup_Bohn_N_steps','WD_CAM_eye_Bohn_N_door_approach_from_NW']:
    o=bpy.data.objects.get(n)
    if o: bpy.data.objects.remove(o)
e=Vector((0.9444,-0.3291,0)).normalized(); nrm=Vector((-e.y,e.x,0)); M=Vector((226.825,413.425,0)); zL=132.45
def W(s,l,z=0): return Vector((M.x+e.x*s+nrm.x*l, M.y+e.y*s+nrm.y*l, z))
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
skp=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
# sample ground with boolean disabled
md=sk.modifiers.get('WD_cut_Bohn_N_steps'); md.show_viewport=False
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get(); ske=sk.evaluated_get(dg)
def g(p):
    r=ske.ray_cast(Vector((p.x,p.y,400)),Vector((0,0,-1))); return r[1].z if r[0] else 134
col=bpy.data.collections['WD_Bohn_approach_walks_steps_UNVERIFIED']
def cam(name,loc,tgt,lens):
    cd=bpy.data.cameras.new(name); cd.lens=lens; cd.clip_end=30000; cd.clip_start=0.1
    o=bpy.data.objects.new(name,cd); col.objects.link(o); o['wd_obj']=1
    o.location=loc; o.rotation_euler=(tgt-loc).to_track_quat('-Z','Y').to_euler(); return o
c1=W(7.5,2.2); c1.z=g(c1)+1.6
cam('WD_CAM_closeup_Bohn_N_steps',c1,W(-2.2,0.1,zL+1.0),24)
c2=W(-2.0,7.0); c2.z=g(c2)+1.65
cam('WD_CAM_eye_Bohn_N_steps_from_N',c2,W(-0.5,0,zL+0.5),26)
print('CAMS',[round(x,1) for x in c1],[round(x,1) for x in c2])
md.show_viewport=True
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
