import bpy, bmesh, os, heapq, numpy as np
from datetime import datetime
R='/workspace/nj-scenes/montclair-state'
O=bpy.data.objects; sc=bpy.context.scene
o=O['QY_walk_junction_wear_decals_UNVERIFIED']; me=o.data
m=o.active_material; nt=m.node_tree
mr=nt.nodes['Map Range']; print('MR interp',mr.interpolation_type,'dtype',mr.data_type)
bs=nt.nodes['Principled BSDF']; print('base',tuple(round(c,3) for c in bs.inputs['Base Color'].default_value))
w=np.array([d.value for d in me.attributes['qy_w'].data]); print('qy_w before p50/p90/max',np.percentile(w,50),np.percentile(w,90),w.max())
bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
mw=o.matrix_world
co=[mw@v.co for v in bm.verts]
dist=[1e9]*len(bm.verts); pq=[]
for v in bm.verts:
    if v.is_boundary: dist[v.index]=0.0; pq.append((0.0,v.index))
heapq.heapify(pq)
while pq:
    d,i=heapq.heappop(pq)
    if d>dist[i]: continue
    for e in bm.verts[i].link_edges:
        j=e.other_vert(bm.verts[i]).index; nd=d+(co[i].xy-co[j].xy).length
        if nd<dist[j]: dist[j]=nd; heapq.heappush(pq,(nd,j))
D=np.array(dist); F=float(os.environ.get('FADE','1.2'))
t=np.clip(D/F,0,1); s=t*t*(3-2*t)
w2=w*s
for k,d in enumerate(me.attributes['qy_w'].data): d.value=float(w2[k])
print('boundary verts',int((D==0).sum()),'qy_w after p50/p90/max',np.percentile(w2,50),np.percentile(w2,90),w2.max())
if mr.interpolation_type in ('STEPPED','LINEAR'): mr.interpolation_type='SMOOTHSTEP'
a=float(os.environ.get('ALPHA','0.5')); nt.nodes['Math.001'].inputs[1].default_value=a
print('alpha strength ->',a, 'interp ->',mr.interpolation_type)
me.update()
if os.environ.get("SEAT")=="1": exec(open(R+"/scripts/wg/wg_seat.py").read())
if os.environ.get('SAVE')=='1':
    bpy.ops.wm.save_mainfile(); print('SAVED',len(O),flush=True)
if os.environ.get('TEST')=='1':
    sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=16; sc.cycles.use_denoising=True
    sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=50
    sc.render.image_settings.file_format='JPEG'; sc.render.threads_mode='FIXED'; sc.render.threads=4
    sc.camera=O['WF_CAM_closeup_436_east_edge']; sc.render.filepath=f'{R}/renders/wip/test_wg_fix_{os.environ.get("TAG","a")}.jpg'
    bpy.ops.render.render(write_still=True); print('DONE',datetime.now().strftime('%H:%M:%S'),flush=True)
