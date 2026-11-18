# ws134i: Balance Kitchen rooftop units from LiDAR 2023 class-6 clusters 0.5-2 m above the roof (compact ones only).
import bpy, bmesh, os, json
SAVE=os.environ.get('SAVE','0')=='1'
cl=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws134/bk_rtu134.json'))
def base(x,y): return 130.75 if x>=-95.5 else (129.85 if y>=-264 else 128.75)
bm=bmesh.new(); n=0
for x0,x1,y0,y1,z,c in cl:
    if (x1-x0)*(y1-y0)>12: continue
    x0+=0.2;x1-=0.2;y0+=0.2;y1-=0.2; zb=base((x0+x1)/2,(y0+y1)/2)-0.35; zt=max(z,zb+0.9)
    r=bmesh.ops.create_cube(bm,size=1.0); 
    for v in r['verts']: v.co.x=x0+(v.co.x+0.5)*(x1-x0); v.co.y=y0+(v.co.y+0.5)*(y1-y0); v.co.z=zb+(v.co.z+0.5)*(zt-zb)
    n+=1
me=bpy.data.meshes.new('WS134i_Balance_Kitchen_rooftop_units_LiDAR2023_clusters_UNVERIFIEDtype'); bm.to_mesh(me); bm.free()
src=bpy.data.objects.get('Roof_pent'); m=src.data.materials[0] if src and src.data.materials else None
if m: me.materials.append(m)
for o in [o for o in bpy.data.objects if o.name.startswith('WS134i_')]: bpy.data.objects.remove(o)
bpy.data.collections['WS134_Freeman_block'].objects.link(bpy.data.objects.new(me.name,me)); print('RTU',n,m.name if m else None)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
