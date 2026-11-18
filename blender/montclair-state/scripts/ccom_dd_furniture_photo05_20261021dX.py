"""2026-10-21 session dX (~12:30 PM ET). The dd corridor furniture (SOUTH0/SOUTH1/WEST0/EAST0) was boxes: flat slab seats, flat
board backs, square sticks. Joe's photos 04/05 (refs/joe/ccom_interior_east_1f_joe_20261020_04/05.jpg) show:
 - dining chairs: one-piece grey upholstered shell (thick cushioned seat, tall back tapering wider to a rounded top, slight recline)
   on 4 splayed light-oak legs;
 - tables: white tops on chrome posts with star/cross feet;
 - lounge chairs: orange/grey swivel shells with wrap-around arms on a 4-arm chrome star base.
This script hides the old chair seat/back/leg boxes and lounge seat/back/base boxes (obj prop dX_hidden) and builds replacements
(obj prop dX_new) at the same position/heading/floor and with the same materials. Table posts get chrome cross feet.
Sizes are photo-scaled from the 0.45 m seat height (UNVERIFIED +/-0.05 m). REVERT=1 deletes dX_new and unhides. SAVE=1 saves."""
import bpy, bmesh, os, math, re
from mathutils import Vector, Matrix
def bbw(o):
    P=[o.matrix_world@Vector(c) for c in o.bound_box]
    return Vector([min(p[i] for p in P) for i in range(3)]), Vector([max(p[i] for p in P) for i in range(3)])
# --- revert
for o in [o for o in bpy.data.objects if 'dX_new' in o]:
    me=o.data; bpy.data.objects.remove(o)
    if me and me.users==0: bpy.data.meshes.remove(me)
for o in bpy.data.objects:
    if 'dX_hidden' in o:
        o.hide_render=False; o.hide_viewport=False; del o['dX_hidden']
bpy.context.view_layer.update()
if os.environ.get('REVERT')=='1':
    print('DX_REVERTED', flush=True)
else:
    def hide(o): o['dX_hidden']=1; o.hide_render=True; o.hide_viewport=True
    def mk(name, bm, mat, coll, M, bevel=None):
        me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        for p in me.polygons: p.use_smooth=True
        me.materials.append(mat)
        o=bpy.data.objects.new(name, me); o.matrix_world=M; o['dX_new']=1; coll.objects.link(o)
        if bevel:
            m=o.modifiers.new('dX_bevel','BEVEL'); m.width=bevel; m.segments=3; m.limit_method='ANGLE'
            m2=o.modifiers.new('dX_wn','WEIGHTED_NORMAL'); m2.keep_sharp=True
        return o
    def box(bm, x0,x1,y0,y1,z0,z1, topscale=(1,1), topshift=(0,0)):
        cx,cy=(x0+x1)/2,(y0+y1)/2; hx,hy=(x1-x0)/2,(y1-y0)/2
        vs=[]
        for z,s,sh in ((z0,(1,1),(0,0)),(z1,topscale,topshift)):
            for dx,dy in ((-1,-1),(1,-1),(1,1),(-1,1)):
                vs.append(bm.verts.new((cx+dx*hx*s[0]+sh[0], cy+dy*hy*s[1]+sh[1], z)))
        f=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
        for q in f: bm.faces.new([vs[i] for i in q])
    def leg(bm, top, bot, r0, r1, n=8):
        top=Vector(top); bot=Vector(bot); ax=(top-bot).normalized()
        u=ax.orthogonal().normalized(); w=ax.cross(u)
        a=[bm.verts.new(bot+ (u*math.cos(2*math.pi*k/n)+w*math.sin(2*math.pi*k/n))*r1) for k in range(n)]
        b=[bm.verts.new(top+ (u*math.cos(2*math.pi*k/n)+w*math.sin(2*math.pi*k/n))*r0) for k in range(n)]
        for k in range(n): bm.faces.new([a[k],a[(k+1)%n],b[(k+1)%n],b[k]])
        bm.faces.new(a[::-1]); bm.faces.new(b)
    nch=nlo=nft=0
    seats=[o for o in bpy.data.objects if re.match(r'dd_[A-Z0-9]+_ch_.*_seat$', o.name)]
    for s in seats:
        pre=s.name[:-len('seat')]; back=bpy.data.objects[pre+'back']
        legs=[o for o in bpy.data.objects if o.name.startswith(pre+'leg')]
        smn,smx=bbw(s); bmn,bmx=bbw(back)
        fl=min([bbw(l)[0].z for l in legs]+[smn.z-0.42])
        c=(smn+smx)/2; bc=(bmn+bmx)/2
        d=Vector((bc.x-c.x, bc.y-c.y, 0)).normalized()   # toward back
        yaw=math.atan2(-d.y,-d.x)-math.pi/2   # local +Y = facing (away from back)
        M=Matrix.Translation((c.x,c.y,fl))@Matrix.Rotation(yaw,4,'Z')
        coll=s.users_collection[0]; mat=s.data.materials[0]; wood=legs[0].data.materials[0] if legs else bpy.data.materials['CCOM_dc_light_wood']
        for o in [s,back]+legs: hide(o)
        bm=bmesh.new()
        box(bm,-0.235,0.235,-0.22,0.24,0.40,0.47, topscale=(1.0,1.0))           # cushioned seat (top 0.47)
        box(bm,-0.215,0.215,-0.275,-0.205,0.44,0.90, topscale=(1.16,1.0), topshift=(0,-0.10))  # tall back, wider at top, reclined
        mk(pre+'shell_dX', bm, mat, coll, M, bevel=0.022)
        bm=bmesh.new()
        for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1)):
            top=(sx*0.185, -0.16 if sy<0 else 0.19, 0.405); bot=(sx*0.225, -0.215 if sy<0 else 0.245, 0.0)
            leg(bm, top, bot, 0.017, 0.011)
        mk(pre+'legs_dX', bm, wood, coll, M)
        nch+=1
    # lounge swivel shells (photo 04)
    for s in [o for o in bpy.data.objects if re.match(r'dd_[A-Z0-9]+_lounge_\d+_seat$', o.name)]:
        pre=s.name[:-len('seat')]; back=bpy.data.objects.get(pre+'back'); base=bpy.data.objects.get(pre+'base')
        smn,smx=bbw(s); c=(smn+smx)/2
        bmn,bmx=bbw(back); bc=(bmn+bmx)/2; d=Vector((bc.x-c.x,bc.y-c.y,0)).normalized()
        yaw=math.atan2(-d.y,-d.x)-math.pi/2
        fl=bbw(base)[0].z if base else smn.z-0.25
        M=Matrix.Translation((c.x,c.y,fl))@Matrix.Rotation(yaw,4,'Z')
        coll=s.users_collection[0]; mat=s.data.materials[0]; chrome=bpy.data.materials['CCOM_dc_chrome']
        for o in (s,back,base):
            if o: hide(o)
        bm=bmesh.new()
        box(bm,-0.36,0.36,-0.33,0.36,0.36,0.46)                                   # seat pan
        box(bm,-0.36,0.36,-0.40,-0.30,0.40,0.88, topscale=(1.08,1.0), topshift=(0,-0.08))  # back
        for sx in (-1,1): box(bm, sx*0.36-0.05, sx*0.36+0.05, -0.36, 0.24, 0.40, 0.66, topscale=(1,0.85), topshift=(0,-0.06))  # wrap arms
        mk(pre+'shell_dX', bm, mat, coll, M, bevel=0.03)
        bm=bmesh.new()
        leg(bm,(0,0,0.36),(0,0,0.05),0.03,0.03,n=12)
        for k in range(4):
            a=math.pi/4+k*math.pi/2; e=(0.34*math.cos(a),0.34*math.sin(a),0.02)
            leg(bm,(0,0,0.06),e,0.018,0.012)
        mk(pre+'base_dX', bm, chrome, coll, M)
        nlo+=1
    # table posts: chrome cross feet
    for p in [o for o in bpy.data.objects if re.match(r'dd_[A-Z0-9]+_tped_', o.name) and not o.hide_render]:
        pmn,pmx=bbw(p); c=(pmn+pmx)/2
        M=Matrix.Translation((c.x,c.y,pmn.z))@Matrix.Rotation(p.matrix_world.to_euler().z,4,'Z')
        bm=bmesh.new()
        box(bm,-0.33,0.33,-0.025,0.025,0.0,0.03); box(bm,-0.025,0.025,-0.30,0.30,0.0,0.03)
        mk(p.name.replace('.','_')+'_foot_dX', bm, p.data.materials[0], p.users_collection[0], M, bevel=0.008)
        nft+=1
    print('DX chairs', nch, 'lounge', nlo, 'feet', nft, flush=True)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('DX_SAVED', flush=True)
