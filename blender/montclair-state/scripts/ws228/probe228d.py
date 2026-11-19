import bpy,bmesh,sys,os,json
R=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws228/fix228c_report.json'))
o=bpy.data.objects['WS60_terrain_edge_apron_LiDAR_to_skirt']; ab=bmesh.new(); ab.from_mesh(o.data)
loose=[e for e in ab.edges if not e.link_faces]; ng=[f for f in ab.faces if len(f.verts)>4]
print('P228D apron loose edges',len(loose),'ngons',len(ng),[ (len(f.verts),tuple(round(c,1) for c in f.calc_center_median())) for f in ng][:10],flush=True)
lv=[v for v in ab.verts if not v.link_faces]; print('P228D loose verts',len(lv),[tuple(round(c,1) for c in v.co) for v in lv[:5]],flush=True)
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; bm=bmesh.new(); bm.from_mesh(t.data)
bv=[v for v in bm.verts if v.is_boundary and v.co.y<-247 and v.co.x>40]; bv.sort(key=lambda v:v.co.x)
print('P228D terrain S boundary verts x>40',len(bv),[round(v.co.x,1) for v in bv][:8],'...',[round(v.co.x,1) for v in bv][-5:],flush=True)
av=[v for v in ab.verts if abs(v.co.y+248.74)<0.3 and v.co.x>40 and v.co.x<247]; print('P228D apron verts on S line',len(av),flush=True)
sys.stdout.flush(); os._exit(0)
