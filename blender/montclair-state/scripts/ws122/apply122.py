# ws122 apply: replace WS108 per-column-ground windows with storey-datum windows from layout122.json
import bpy, bmesh, json, os
from mathutils import Vector
J=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws122/layout122.json'))
FR=J['FR']; GW=J['GW']
NAME='WS122_Chapin_windows_storey_datum_FFE124p77_UNVERIFIED'
def mat(name,rgb,rough):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes=True
    b=m.node_tree.nodes.get('Principled BSDF'); b.inputs['Base Color'].default_value=(*rgb,1); b.inputs['Roughness'].default_value=rough
    m.diffuse_color=(*rgb,1); return m
M_frame=bpy.data.materials.get('WS108_Chapin_window_frame_dark_bronze') or mat('WS108_Chapin_window_frame_dark_bronze',(0.06,0.045,0.035),0.5)
M_glass=bpy.data.materials.get('WS108_Chapin_window_glass_dark') or mat('WS108_Chapin_window_glass_dark',(0.025,0.03,0.035),0.12)
M_sill=mat('WS122_Chapin_window_sill_precast_cream_UNVERIFIED',(0.62,0.58,0.50),0.75)
old=bpy.data.objects.get('WS108_Chapin_windows_grid_UNVERIFIED')
col=(old.users_collection[0] if old else bpy.data.collections.get('WS108_Chapin_eaves_windows_UNVERIFIED'))
for o in [o for o in bpy.data.objects if o.name.startswith('WS122_Chapin_windows')]: bpy.data.objects.remove(o)
bm=bmesh.new()
def P(c,u,n,a,b,d): return c+u*a+n*d+Vector((0,0,b))
def quad(vs,mi):
    f=bm.faces.new([bm.verts.new(v) for v in vs]); f.material_index=mi
def box(c,u,n,a0,a1,b0,b1,d0,d1,mi,skip_back=True):
    q=lambda a,b,d:P(c,u,n,a,b,d)
    quad([q(a0,b0,d1),q(a1,b0,d1),q(a1,b1,d1),q(a0,b1,d1)],mi)          # front
    quad([q(a0,b1,d0),q(a1,b1,d0),q(a1,b1,d1),q(a0,b1,d1)][::-1],mi)    # top
    quad([q(a0,b0,d0),q(a0,b0,d1),q(a1,b0,d1),q(a1,b0,d0)][::-1],mi)    # bottom
    quad([q(a0,b0,d0),q(a0,b1,d0),q(a0,b1,d1),q(a0,b0,d1)][::-1],mi)    # left
    quad([q(a1,b0,d0),q(a1,b0,d1),q(a1,b1,d1),q(a1,b1,d0)][::-1],mi)    # right
for w in J['wins']:
    n=Vector((w['nh'][0],w['nh'][1],0)).normalized(); u=Vector((-n.y,n.x,0))
    gh=w['gh']; c=Vector((w['c'][0],w['c'][1],w['sill']))   # c at sill (glass bottom) on facade plane
    hi=GW/2; ho=hi+FR
    DF,DG,DB=0.035,0.012,-0.02   # frame face proud, glass proud, back (tucked into wall)
    # frame ring as 4 boxes (head, jambs, bottom rail)
    box(c,u,n,-ho,ho,gh,gh+FR,DB,DF,0)
    box(c,u,n,-ho,ho,-FR,0,DB,DF,0)
    box(c,u,n,-ho,-hi,0,gh,DB,DF,0)
    box(c,u,n,hi,ho,0,gh,DB,DF,0)
    # glass (recessed behind frame face) + double-hung meeting rail
    quad([P(c,u,n,-hi,0,DG),P(c,u,n,hi,0,DG),P(c,u,n,hi,gh,DG),P(c,u,n,-hi,gh,DG)],1)
    box(c,u,n,-hi,hi,gh*0.5-0.025,gh*0.5+0.025,DG-0.005,DG+0.02,0)
    # precast sill under the frame, projecting 8 cm
    box(c,u,n,-ho-0.05,ho+0.05,-FR-0.06,-FR,DB,0.08,2)
me=bpy.data.meshes.new(NAME); bm.to_mesh(me); bm.free()
for m in (M_frame,M_glass,M_sill): me.materials.append(m)
ob=bpy.data.objects.new(NAME,me); col.objects.link(ob)
for p in me.polygons: p.use_smooth=False
if old: bpy.data.objects.remove(old)
print('A122 windows',len(J['wins']),'faces',len(me.polygons),'old_removed',old is not None)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('A122 SAVED')
