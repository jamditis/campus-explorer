# ts (Nov 5 2026 ~3:40 AM ET, MAIN, day 8 east edge: pale far-field ground band). ALL UNVERIFIED tone, reversible (REVERT=1).
# The 4 km skirt used a 1k (3.9 m/px) leaf-off NJ 2020 ortho under a 0.6 distance haze, which read as a milky pale band.
# (1) Skirt: swap to a 4096 px (~0.98 m/px) leaf-on USGS NAIP Plus mosaic of the SAME EPSG:6527 bbox (same UVs, checked), retune gain/haze.
# (2) Far field (local _bm copy): swap ortho_far.jpg for a NAIP export of the same bbox if data/ts/naip_far.jpg exists.
import bpy, os
REV=os.environ.get('REVERT')=='1'
D='/workspace/nj-scenes/montclair-state/'
SK='OW2_Context_skirt_ortho_strip_tone_UNVERIFIED'; FAR='BD_farfield_ortho_haze_bm'
NAIP=D+'data/ts/naip_skirt_4k.jpg'; NAIPF=D+'data/ts/naip_far.jpg'
SET={ # node, input index/name, new value
 ('ah_mrV','To Min'):1.00, ('ah_mrV','To Max'):0.56,
 ('ah_mrS','To Max'):1.10,
 ('ah_leafon','Factor'):0.10,
 ('EP_haze_mr','To Max'):float(os.environ.get('HAZE','0.42')),
 ('Principled BSDF','IOR'):float(os.environ.get('IOR','1.0')),
}
def inp(n,k):
    for i in n.inputs:
        if i.name==k and not i.is_linked and hasattr(i,'default_value'): return i
def revert():
    for mn in (SK,FAR):
        m=bpy.data.materials.get(mn)
        if not m or 'ts_orig' not in m: continue
        o=dict(m['ts_orig']); N=m.node_tree.nodes
        for key,val in o.items():
            nn,k=key.split('|')
            if k=='__image':
                N[nn].image=bpy.data.images.get(val) or N[nn].image
            else:
                i=inp(N[nn],k); i.default_value=val
        del m['ts_orig']
        for n in [n for n in N if n.name.startswith('TS_')]: N.remove(n)
        if mn==SK and 'QV_final' in N: m.node_tree.links.new(N['QV_final'].outputs[0],N['Principled BSDF'].inputs['Base Color'])
    fo_=[o for o in bpy.data.objects if o.name=='BD_farfield_3DEP_ortho' and o.library is None]
    for o in fo_:
        if 'ts_orig_mesh' in o:
            om=bpy.data.meshes.get(o['ts_orig_mesh']); nm=o.data
            if om: o.data=om; om.use_fake_user=False
            if nm and nm.users==0: bpy.data.meshes.remove(nm)
            del o['ts_orig_mesh']
    for im in list(bpy.data.images):
        if im.get('ts_obj'): bpy.data.images.remove(im)
    print('TS reverted')
revert()
if REV:
    if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
m=bpy.data.materials[SK]; N=m.node_tree.nodes; orig={}
it=N['Image Texture']; orig['Image Texture|__image']=it.image.name
im=bpy.data.images.load(NAIP); im.name='TS_naip_skirt_4k_UNVERIFIED'; im['ts_obj']=1; it.image=im
for (nn,k),v in SET.items():
    if v is None: continue
    i=inp(N[nn],k); orig[nn+'|'+k]=i.default_value; i.default_value=v
m['ts_orig']=orig
# (1b) outer-skirt tone: beyond r~280 m (outside the 1 m LiDAR tile) fade toward the NAIP colour itself (darker, more saturated,
# real leaf-on canopy) under the existing distance haze, instead of the pale processed chain. Inside r<280 m nothing changes.
L=m.node_tree.links; E=os.environ
def nw(t,name,x,y):
    n=N.new(t); n.name=name; n.label=name; n.location=(x,y); return n
g=N['QV_geo']
vm=nw('ShaderNodeVectorMath','TS_mulxy',1800,-900); vm.operation='MULTIPLY'; vm.inputs[1].default_value=(1,1,0)
L.new(g.outputs['Position'],vm.inputs[0])
ln=nw('ShaderNodeVectorMath','TS_len',1950,-900); ln.operation='LENGTH'; L.new(vm.outputs[0],ln.inputs[0])
mr=nw('ShaderNodeMapRange','TS_gate',2100,-900); mr.inputs['From Min'].default_value=float(E.get('R0','280')); mr.inputs['From Max'].default_value=float(E.get('R1','460'))
mr.inputs['To Min'].default_value=0.0; mr.inputs['To Max'].default_value=float(E.get('WMAX','0.85')); L.new(ln.outputs['Value'],mr.inputs['Value'])
hs=nw('ShaderNodeHueSaturation','TS_naip_hsv',1950,-700); hs.inputs['Saturation'].default_value=float(E.get('SAT','1.30')); hs.inputs['Value'].default_value=float(E.get('VAL','0.45'))
L.new(it.outputs['Color'],hs.inputs['Color'])
hz=nw('ShaderNodeMix','TS_haze',2100,-700); hz.data_type='RGBA'; hz.blend_type='MIX'
L.new(N['EP_haze_mr'].outputs['Result'],hz.inputs['Factor']); L.new(hs.outputs['Color'],hz.inputs[6]); hz.inputs[7].default_value=N['EP_haze_mix'].inputs[7].default_value[:]
fm=nw('ShaderNodeMix','TS_final',2300,-700); fm.data_type='RGBA'; fm.blend_type='MIX'
L.new(mr.outputs['Result'],fm.inputs['Factor']); L.new(N['QV_final'].outputs['Result'],fm.inputs[6]); L.new(hz.outputs['Result'],fm.inputs[7])
L.new(fm.outputs['Result'],N['Principled BSDF'].inputs['Base Color'])
print('TS skirt image',im.size[:])
if os.path.exists(NAIPF) and os.path.getsize(NAIPF)>200000:
    f=bpy.data.materials[FAR]; FN=f.node_tree.nodes; fo={}
    ft=FN['Image Texture']; fo['Image Texture|__image']=ft.image.name
    imf=bpy.data.images.load(NAIPF); imf.name='TS_naip_far_UNVERIFIED'; imf['ts_obj']=1; ft.image=imf
    hs=FN['Hue/Saturation/Value']; i=inp(hs,'Value')
    if i: fo['Hue/Saturation/Value|Value']=i.default_value; i.default_value=float(os.environ.get('FARV','0.62'))
    f['ts_orig']=fo; print('TS far image',imf.size[:])
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
# (3) FINDING: the local far-field mesh (USGS 30 m DEM, 24.7 x 21.2 km) also covers the 4 km skirt and pokes up through it in patches;
# its haze-emission material drew the milky pale band. Remove its faces fully inside the skirt (|x|,|y| < 1940 m); keep the
# original mesh datablock (fake user) so REVERT=1 swaps it back exactly.
import bmesh
fo=[o for o in bpy.data.objects if o.name=='BD_farfield_3DEP_ortho' and o.library is None][0]
om=fo.data; om.use_fake_user=True; nm=om.copy(); nm.name='TS_farfield_skirt_hole_UNVERIFIED'
bm=bmesh.new(); bm.from_mesh(nm); mw=fo.matrix_world; K=float(os.environ.get('HOLE','1940'))
kill=[f for f in bm.faces if all(abs((mw@v.co).x)<K and abs((mw@v.co).y)<K for v in f.verts)]
bmesh.ops.delete(bm,geom=kill,context='FACES'); bm.to_mesh(nm); bm.free()
fo['ts_orig_mesh']=om.name; fo.data=nm; print('TS far faces removed',len(kill),'left',len(nm.polygons))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
