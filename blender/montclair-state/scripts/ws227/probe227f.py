import bpy,sys,os
S='/workspace/nj-scenes/montclair-state/scripts/ws227/'
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']
nbig=lambda: sum(1 for p in t.data.polygons if p.area>20 and p.center.x>90 and p.center.y<-30)
print('P227F big before',nbig(),flush=True)
exec(open(S+'fix227x.py').read()); print('P227F big after x',nbig(),len(t.data.polygons),flush=True)
exec(open(S+'fix227a.py').read()); print('P227F big after a',nbig(),len(t.data.polygons),flush=True)
sys.stdout.flush(); os._exit(0)
