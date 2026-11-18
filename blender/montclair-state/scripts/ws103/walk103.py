# ws103: College Ave S leg W sidewalk rebuilt as one smooth concrete walk (curb-tight, 3.5 m), replacing the crumpled
# Footpaths_OSM drape that sat 0.5-1.2 m BELOW the WS102 curb top (old-terrain drape). Evidence: 2023 LiDAR cross-sections
# (scripts/ws102/lid_so.npz): curb step at o~3.0-3.5, flat walk +0.05..+0.10 over the crown out to o~6.5-7.5 for s 24-50,
# +0.1..+0.2 at s 52-88; 2020 ortho light concrete strip; ws102 research: curb-tight W sidewalk.
import bpy,bmesh,numpy as np,sys,os,json
sys.path.insert(0,'/workspace/nj-scenes/montclair-state/scripts/ws103'); from frame103 import *
src=open('/workspace/nj-scenes/montclair-state/scripts/ws102/apply102.py').read(); exec(src[:src.index('mats={')])  # zc, sm, EW (bpy-dependent part)
SA,SB=1.0,86.0; O0=EW+0.14
def O1f(s): return 6.3+0.65*sm(18,24,s)
O1=6.95
def zw(s,o): return zc(s)+0.15*sm(21,24.5,s)+0.004+(-0.008+0.018*sm(19,23,s))*(o-O0)
old=[o for o in bpy.data.objects if o.name.startswith('WS103_CollegeAve_S_W_sidewalk')]
for o in old: bpy.data.objects.remove(o)
print('W103 old removed',len(old))
fp=bpy.data.objects['Footpaths_OSM']; mat=fp.data.materials[0]; print('W103 fp mat',mat.name,[m.name for m in fp.data.materials])
bm=bmesh.new(); rows=np.arange(SA,SB+0.01,0.5); OC=np.linspace(O0,O1,5); G=[]
for s in rows:
    p,n=frame(s); G.append([bm.verts.new((*(p+n*o),zw(s,o))) for o in np.linspace(O0,O1f(s),5)])
for i in range(len(rows)-1):
    for j in range(len(OC)-1): bm.faces.new((G[i][j],G[i+1][j],G[i+1][j+1],G[i][j+1]))
for i in range(len(rows)-1):  # back skirt 0.5 m
    a,b=G[i][-1],G[i+1][-1]; a2=bm.verts.new(a.co-Vector((0,0,0.5))); b2=bm.verts.new(b.co-Vector((0,0,0.5))); bm.faces.new((a,b,b2,a2))
for r in (G[0],G[-1]):  # end skirts 0.3 m
    for j in range(len(OC)-1):
        a,b=r[j],r[j+1]; a2=bm.verts.new(a.co-Vector((0,0,0.3))); b2=bm.verts.new(b.co-Vector((0,0,0.3))); bm.faces.new((a,b,b2,a2))
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
for f in bm.faces:
    if f.normal.z<-0.5: f.normal_flip()
me=bpy.data.meshes.new('WS103_CollegeAve_S_W_sidewalk'); bm.to_mesh(me); bm.free(); me.materials.append(mat)
for p_ in me.polygons: p_.use_smooth=False
ob=bpy.data.objects.new('WS103_CollegeAve_S_W_sidewalk_concrete_LiDAR2023_UNVERIFIEDwidth',me)
cw=[o for o in bpy.data.objects if o.name.startswith('WS102_CollegeAve_S_carriageway')][0]; cw.users_collection[0].objects.link(ob)
# retire Footpaths_OSM source faces inside the new walk footprint
bm=bmesh.new(); bm.from_mesh(fp.data); mw=fp.matrix_world; dl=[]
for f in bm.faces:
    c=mw@f.calc_center_median(); s,o=so(np.array([c.x,c.y]))
    if SA-0.25<=s<=SB and 2.4<=o<=O1f(s)+0.35: dl.append(f)
bmesh.ops.delete(bm,geom=dl,context='FACES'); lv=[v for v in bm.verts if not v.link_faces]; bmesh.ops.delete(bm,geom=lv,context='VERTS')
bm.to_mesh(fp.data); fp.data.update(); bm.free(); print('W103 fp faces removed',len(dl))
# terrain: cap 4 cm under the walk inside footprint (+0.3 m), feather the bank behind it so no grass covers the walk
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tm=T.data; nt=len(tm.vertices)
c2=np.empty(nt*3); tm.vertices.foreach_get('co',c2); c2=c2.reshape(-1,3); MT=np.array(T.matrix_world); TW=c2@MT[:3,:3].T+MT[:3,3]
sel=np.where((TW[:,0]>-250)&(TW[:,0]<-205)&(TW[:,1]>-250)&(TW[:,1]<-165))[0]; nc=0; nf=0
for k in sel:
    s,o=so(TW[k]);
    if not (SA<=s<=SB): continue
    if EW<=o<=O1f(s)+0.3:
        lim=zw(s,min(o,O1f(s)))-0.04
        if TW[k,2]>lim: TW[k,2]=lim; nc+=1
    elif O1f(s)+0.3<o<O1f(s)+2.5:  # behind walk: terrain may not rise above walk+slope 1:3 (no grass lip over the back edge)
        lim=zw(s,O1f(s))-0.02+(o-O1f(s)-0.3)/3.0
        if TW[k,2]>lim: TW[k,2]=lim; nf+=1
Mi=np.linalg.inv(MT); tm.vertices.foreach_set('co',(TW@Mi[:3,:3].T+Mi[:3,3]).ravel()); tm.update(); print('W103 terrain capped',nc,'feathered',nf)
json.dump({'fp_removed':len(dl),'cap':nc,'feather':nf,'verts':len(me.vertices)},open('/workspace/nj-scenes/montclair-state/scripts/ws103/walk103.json','w'))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('W103 SAVED')
