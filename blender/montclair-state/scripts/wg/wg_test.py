import bpy, os
from datetime import datetime
R='/workspace/nj-scenes/montclair-state'
O=bpy.data.objects; sc=bpy.context.scene
m=bpy.data.materials['QT_walk_concrete_joints_UNVERIFIED']; nt=m.node_tree
ao=nt.nodes['Ambient Occlusion']; print('AO dist',ao.inputs['Distance'].default_value,'local',ao.only_local,'inside',ao.inside,'samples',ao.samples)
for l in nt.links:
    if l.from_node==ao or l.to_node.name in('Mix.005','Math.031','Math.032','Math.033','OV_walk_tone','Mix.004'): print('L',l.from_node.name,l.from_socket.identifier,'->',l.to_node.name,l.to_socket.identifier)
mode=os.environ.get('MODE','base')
if mode=='noao':
    for l in list(nt.links):
        if l.from_node==ao: 
            s=l.to_socket; nt.links.remove(l)
            try: s.default_value=1.0
            except: s.default_value=(1,1,1,1)
if mode=='nolawn':
    for o in O:
        if o.name.startswith(('WT_rich','WU_rich')): o.hide_render=True
if mode=='local':
    ao.only_local=True
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=16; sc.cycles.use_denoising=True
sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=50
sc.render.image_settings.file_format='JPEG'; sc.render.threads_mode='FIXED'; sc.render.threads=4
sc.camera=O['WF_CAM_closeup_436_east_edge']; sc.render.filepath=f'{R}/renders/wip/test_wg_{mode}.jpg'
bpy.ops.render.render(write_still=True); print('DONE',mode,datetime.now().strftime('%H:%M:%S'),flush=True)
