# Verify shared pier t-centres on WC meshes + no leftover vw glass on NW face
import bpy, bmesh, json
from mathutils import Vector
ROOT='/workspace/nj-scenes/montclair-state'
d=json.load(open(ROOT+'/data/wc/apply.json'))
O=Vector((d['origin'][0], d['origin'][1], 0))
U=Vector((d['U'][0], d['U'][1], 0))
N=Vector((d['N'][0], d['N'][1], 0))
def tnz(p):
  q=Vector((p.x,p.y,0))-O; return q.dot(U), q.dot(N), p.z
out={'piers_t_planned': d['pier_centres_t']}
# WC glass island t-centres by z-band
for vn in ('WC_Bohn_NW_lower_W_glass_UNVERIFIED','WC_Bohn_NW_lower_W_piers_bands_UNVERIFIED'):
  o=bpy.data.objects[vn]; mw=o.matrix_world
  bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
  seen=set(); islands=[]
  for v in bm.verts:
    if v.index in seen: continue
    isl=[]; st=[v]; seen.add(v.index)
    while st:
      a=st.pop(); isl.append(a)
      for e in a.link_edges:
        b=e.other_vert(a)
        if b.index not in seen: seen.add(b.index); st.append(b)
    ps=[mw@a.co for a in isl]; c=sum(ps,Vector())/len(ps)
    tt,nn,zz=tnz(c)
    islands.append(dict(t=round(tt,3),n=round(nn,3),z0=round(min(p.z for p in ps),2),z1=round(max(p.z for p in ps),2)))
  bm.free()
  out[vn]=islands
# leftover vw glass in region
o=bpy.data.objects['VW_Bohn_W_glass_UNVERIFIED']; mw=o.matrix_world
bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
seen=set(); left=[]
for v in bm.verts:
  if v.index in seen: continue
  isl=[]; st=[v]; seen.add(v.index)
  while st:
    a=st.pop(); isl.append(a)
    for e in a.link_edges:
      b=e.other_vert(a)
      if b.index not in seen: seen.add(b.index); st.append(b)
  ps=[mw@a.co for a in isl]; c=sum(ps,Vector())/len(ps)
  tt,nn,zz=tnz(c)
  if -9<tt<8 and 118<zz<142 and abs(nn)<2.0:
    left.append(dict(t=round(tt,3),n=round(nn,3),z=round(c.z,2)))
bm.free()
out['vw_glass_leftover_in_region']=left
# cluster WC glass by level
g=out['WC_Bohn_NW_lower_W_glass_UNVERIFIED']
base=[x for x in g if x['z0']<136]
l1=[x for x in g if x['z0']>=136]
out['base_glass_t']=sorted(set(x['t'] for x in base))
out['L1_glass_t']=sorted(set(x['t'] for x in l1))
# pier boxes: tall ones spanning full height — centres
pb=[x for x in out['WC_Bohn_NW_lower_W_piers_bands_UNVERIFIED'] if x['z1']-x['z0']>5]
out['tall_pier_t_base']=sorted(set(x['t'] for x in pb if x['z0']<130))
out['tall_pier_t_L1']=sorted(set(x['t'] for x in out['WC_Bohn_NW_lower_W_piers_bands_UNVERIFIED'] if x['z0']>=135 and x['z1']-x['z0']>2))
json.dump(out, open(ROOT+'/data/wc/verify.json','w'), indent=2)
print('planned', d['pier_centres_t'])
print('base glass t', out['base_glass_t'])
print('L1 glass t', out['L1_glass_t'])
print('tall pier base', out['tall_pier_t_base'])
print('tall pier L1', out['tall_pier_t_L1'])
print('vw leftover', len(left), left[:5])
print('nobj', len(bpy.data.objects))
