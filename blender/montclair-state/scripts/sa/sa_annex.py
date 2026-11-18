# sa (Nov 4 2026, MAIN): append the north-file Student Center Annex rebuild (Oct 29 mg..ms + Oct 14 s NE arm), its terrace/deck/low wall/
# lower walk/bank, and the Health Drop-In Center (mo) into MAIN. Same EPSG:6527 frame (rz/qm precedent, no transform). ALL UNVERIFIED.
# Skips MH apron + hides 'MN seam fade' (north-edge patches). Hides MAIN's duplicate QXP/QY 313027423 terrace paving.
# Culls MAIN grass points whose XY falls on an appended visible mesh (0.5 m raster). REVERT=1 removes everything (data/sa/annex_added.json).
import bpy, os, json, bmesh, numpy as np
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; J='data/sa/annex_added.json'; PARENT='SA_Annex_terrace_HealthDropIn_from_north_UNVERIFIED'
CN=['MG_StudentCenterAnnex_20261029mg','MI_StudentCenterAnnex_20261029mi','MJ_StudentCenterAnnex_lowwall_20261029mj','MK_StudentCenterAnnex_lowerwalk_20261029mk',
 'ML_StudentCenterAnnex_weststeps_deck_20261029ml','MM_StudentCenterAnnex_deckwall_terrace_rail_20261029mm','MN_StudentCenterAnnex_seam_deckfill_bank_paving_20261029mn',
 'MR_Annex_wall_joints_bankgrass_20261029mr','MS_Annex_deckwall_joints_20261029ms','North_StudentCenterAnnex_20261014s','MO_HealthDropInCenter_bankgrass_20261029mo']
HIDE_MAIN=['QXP_pedestrian_area_313027423_paving_UNVERIFIED','QY_plaza_rim_band_313027423_UNVERIFIED']
GZ='data/sa/grass_removed.npz'
if os.path.exists(J) and (REV or bpy.data.collections.get(PARENT)):
    d=json.load(open(J))
    for n in d['objects']:
        o=bpy.data.objects.get(n)
        if o: bpy.data.objects.remove(o,do_unlink=True)
    for k in ('collections','meshes','materials','node_groups','images','curves','fonts'):
        for n in d.get(k,[]):
            x=getattr(bpy.data,k).get(n)
            if x and (k=='collections' or x.users==0): getattr(bpy.data,k).remove(x)
    for n,(hr,hv) in d['hidden'].items():
        o=bpy.data.objects.get(n)
        if o: o.hide_render=hr; o.hide_viewport=hv
    if os.path.exists(GZ):
        z=np.load(GZ)
        for n in d['culled']:
            o=bpy.data.objects.get(d['culled'][n]); a=z[n]
            if o is None or len(a)==0: continue
            me=o.data; k0=len(me.vertices); me.vertices.add(len(a))
            for i,co in enumerate(a): me.vertices[k0+i].co=co
            me.update()
    print('SA_ANNEX reverted')
    if REV:
        if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
        raise SystemExit
before={k:set(x.name for x in getattr(bpy.data,k)) for k in ('objects','meshes','materials','collections','libraries','node_groups','images','curves','fonts')}
with bpy.data.libraries.load('north/montclair_north.blend',link=False) as (a,b): b.collections=[c for c in a.collections if c in CN]
par=bpy.data.collections.new(PARENT); bpy.context.scene.collection.children.link(par)
AC=[c for c in b.collections if c is not None]
print('SA got',[c.name for c in AC])
for c in AC: par.children.link(c)
NEWOBJS=list({o for c in AC for o in c.objects})
hid={}
for o in NEWOBJS:
    if o.name.startswith('MN seam fade'): o.hide_render=True; o.hide_viewport=True
for n in HIDE_MAIN:
    o=bpy.data.objects.get(n)
    if o: hid[n]=(o.hide_render,o.hide_viewport); o.hide_render=True; o.hide_viewport=True
# raster mask of appended visible meshes (XY), 0.5 m
X0,X1,Y0,Y1,S=-115.0,70.0,265.0,345.0,0.5
nx=int((X1-X0)/S)+1; ny=int((Y1-Y0)/S)+1; mask=np.zeros((ny,nx),bool)
dg=bpy.context.evaluated_depsgraph_get()
for o in NEWOBJS:
    if o.type!='MESH' or o.hide_render or len(o.data.polygons)==0: continue
    e=o.evaluated_get(dg); me=e.to_mesh(); me.calc_loop_triangles(); M=o.matrix_world
    V=np.array([tuple(M@v.co) for v in me.vertices])
    for t in me.loop_triangles:
        p=V[list(t.vertices)][:,:2]
        i0=max(0,int((p[:,0].min()-X0)/S)); i1=min(nx-1,int((p[:,0].max()-X0)/S)+1); j0=max(0,int((p[:,1].min()-Y0)/S)); j1=min(ny-1,int((p[:,1].max()-Y0)/S)+1)
        if i1<i0 or j1<j0: continue
        gx,gy=np.meshgrid(X0+S*np.arange(i0,i1+1),Y0+S*np.arange(j0,j1+1))
        (ax,ay),(bx,by),(cx,cy)=p; den=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
        if abs(den)<1e-9: continue
        l1=((by-cy)*(gx-cx)+(cx-bx)*(gy-cy))/den; l2=((cy-ay)*(gx-cx)+(ax-cx)*(gy-cy))/den; l3=1-l1-l2
        mask[j0:j1+1,i0:i1+1]|=(l1>=-0.15)&(l2>=-0.15)&(l3>=-0.15)
    e.to_mesh_clear()
# dilate 1 cell
m2=mask.copy(); m2[1:]|=mask[:-1]; m2[:-1]|=mask[1:]; m2[:,1:]|=mask[:,:-1]; m2[:,:-1]|=mask[:,1:]; mask=m2
print('SA mask cells',int(mask.sum()))
new=set(NEWOBJS); culled={}; cmap={}
for o in bpy.data.objects:
    if o in new or o.type!='MESH' or len(o.data.polygons)>0 or 'grass' not in o.name.lower(): continue
    me=o.data; n=len(me.vertices)
    if n==0: continue
    co=np.zeros(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3); W=np.array(o.matrix_world); wc=co@W[:3,:3].T+W[:3,3]
    ii=np.rint((wc[:,0]-X0)/S).astype(int); jj=np.rint((wc[:,1]-Y0)/S).astype(int); ok=(ii>=0)&(ii<nx)&(jj>=0)&(jj<ny)
    m=np.zeros(n,bool); m[ok]=mask[jj[ok],ii[ok]]
    if not m.any(): continue
    k='g%d'%len(cmap); cmap[k]=o.name; culled[k]=co[m]
    bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[bm.verts[i] for i in np.nonzero(m)[0]],context='VERTS'); bm.to_mesh(me); bm.free(); me.update()
    print('SA culled',o.name,int(m.sum()),'of',n)
np.savez(GZ,**culled)
for i in list(bpy.data.images):
    if i.name not in before['images'] and i.name.startswith('ortho2020_north.jpg') and bpy.data.images.get('ortho2020_north.jpg.001'):
        i.user_remap(bpy.data.images['ortho2020_north.jpg.001']); bpy.data.images.remove(i); print('SA image remapped')
for l in list(bpy.data.libraries):
    if l.name not in before['libraries'] and l.users==0: bpy.data.libraries.remove(l)
for o in NEWOBJS: o['UNVERIFIED_sa']='sa: Annex/terrace/deck/low wall/Health Drop-In appended from north (Oct 29 mg..ms, mo; Oct 14 s)'
after={k:set(x.name for x in getattr(bpy.data,k)) for k in before}
d={k:sorted(after[k]-before[k]) for k in before}; d['hidden']=hid; d['culled']=cmap
json.dump(d,open(J,'w'),indent=0)
print('SA_ANNEX appended',{k:len(v) for k,v in d.items()},'imgs',d['images'],'libs',[l.filepath for l in bpy.data.libraries if l.name not in before['libraries']])
print('OBJCOUNT',len(bpy.data.objects))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
