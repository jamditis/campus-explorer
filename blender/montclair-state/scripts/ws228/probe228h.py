import bpy,bmesh,sys,os
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; o=bpy.data.objects['WS60_terrain_edge_apron_LiDAR_to_skirt']
TV=sorted([(round(v.co.y,2),round(v.co.z,2)) for v in t.data.vertices if 245.5<v.co.x<246.5 and v.co.y<=-33.4])
bm=bmesh.new(); bm.from_mesh(o.data)
AV={(round(v.co.y,2)):round(v.co.z,2) for v in bm.verts if 245.5<v.co.x<246.5 and v.co.y<=-33.4 and v.link_faces}
miss=[(y,z) for y,z in TV if not any(abs(y-ay)<0.011 and abs(z-az)<0.02 for ay,az in AV.items())]; dz=[(y,z,AV[y]) for y,z in TV if y in AV and abs(AV[y]-z)>0.01]
print('P228H terrain edge verts',len(TV),'apron inner',len(AV),'missing',miss[:12],'zdiff',dz[:6],flush=True)
ng=[f for f in bm.faces if len(f.verts)>4 and min(v.co.x for v in f.verts)>245]; print('P228H east ngons',len(ng),flush=True)
sys.stdout.flush(); os._exit(0)
