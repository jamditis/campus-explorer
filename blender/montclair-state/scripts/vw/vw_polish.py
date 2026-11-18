# vw polish: rebuild piers/bands so horizontal bands sit BETWEEN piers (no overlapping junction cubes)
import bpy, bmesh, os, json, math
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1'
ROOT = '/workspace/nj-scenes/montclair-state'
OUT = ROOT + '/data/vw'
CN = 'VW_Bohn_W_face_windows_UNVERIFIED'
NOTE = ('Bohn W-face recessed eggcrate after MSU Digital Commons slides 1251/1519; '
        'column counts/pier/window/recess widths UNVERIFIED; opaque-reflective glass; '
        'proud overlay on solid massing (no boolean cut)')
BAY = 2.95; PIER_W = 0.48; BAND_H = 0.42; DEPTH = 0.40
GLASS_T = 0.04; GLASS_OFF = 0.015; FLOOR = 2.75; MARGIN_Z = 0.12; MARGIN_T = 0.10

def remove_obj(o):
    me=o.data; t=o.type
    bpy.data.objects.remove(o, do_unlink=True)
    if me and me.users==0:
        if t=='MESH': bpy.data.meshes.remove(me)
        elif t=='CAMERA': bpy.data.cameras.remove(me)

# remove only mesh overlays; keep cams + mats
for o in [o for o in list(bpy.data.objects) if o.get('vw_obj') and o.type=='MESH']:
    remove_obj(o)

col = bpy.data.collections.get(CN) or bpy.data.collections.new(CN)
if CN not in [c.name for c in bpy.context.scene.collection.children]:
    bpy.context.scene.collection.children.link(col)

M_CONC = bpy.data.materials.get('VW_Bohn_W_concrete_UNVERIFIED')
M_GLASS = bpy.data.materials.get('VW_Bohn_W_glass_opaque_reflective_UNVERIFIED')
M_REVEAL = bpy.data.materials.get('VW_Bohn_W_reveal_UNVERIFIED')
# darken glass a touch for oblique readability
b = M_GLASS.node_tree.nodes['Principled BSDF']
b.inputs['Base Color'].default_value = (0.035, 0.045, 0.055, 1)
b.inputs['Roughness'].default_value = 0.045

class MB:
    def __init__(s, name, mats):
        s.bm=bmesh.new(); s.name=name; s.mats=mats
    def box2(s, c, u, n, w, d0, d1, z0, z1, mi=0):
        u=Vector((u.x,u.y,0)).normalized(); n=Vector((n.x,n.y,0)).normalized(); cxy=Vector((c.x,c.y,0))
        corners=[]
        for z in (z0,z1):
            for a,dd in ((-1,d0),(1,d0),(1,d1),(-1,d1)):
                p=cxy+u*(a*w/2)+n*dd; corners.append(s.bm.verts.new((p.x,p.y,z)))
        for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):
            try: s.bm.faces.new([corners[i] for i in f]).material_index=mi
            except ValueError: pass
    def done(s):
        bmesh.ops.recalc_face_normals(s.bm, faces=s.bm.faces)
        me=bpy.data.meshes.new(s.name); s.bm.to_mesh(me); s.bm.free()
        for m in s.mats: me.materials.append(m)
        o=bpy.data.objects.new(s.name,me); col.objects.link(o)
        o['vw_obj']=1; o['UNVERIFIED']=NOTE
        for p in me.polygons: p.use_smooth=False
        return o

# rebuild targets same as main
targets=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    if not (o.name.startswith('TL_Bohn_Hall_') or o.name=='TK_Bohn_Hall_232853538_base_UNVERIFIED'): continue
    if 'PH' in o.name: continue
    me=o.data; mw=o.matrix_world
    if 'ti_dir' not in me.attributes: continue
    z0g=me.attributes['ti_z0'].data[0].value
    for pi,p in enumerate(me.polygons):
        n=(mw.to_3x3()@p.normal).normalized()
        if abs(n.z)>0.5 or n.x>-0.70: continue
        z1a=me.attributes['ti_z1'].data[pi].value
        if abs(z1a-z0g)<1.0: continue
        d=me.attributes['ti_dir'].data[pi].vector
        U=Vector((d.x,d.y,0)).normalized(); N=Vector((n.x,n.y,0)).normalized()
        if abs(U.dot(N))>0.3: U=Vector((-N.y,N.x,0)).normalized()
        if U.y<0: U=-U
        verts=[mw@me.vertices[i].co for i in p.vertices]
        ts=[v.x*U.x+v.y*U.y for v in verts]; zs=[v.z for v in verts]
        t0,t1=min(ts),max(ts); width=t1-t0
        if width<5.5: continue
        z0v,z1v=min(zs),max(zs)
        if z1v-z0v<2.0: continue
        cx=sum(v.x for v in verts)/len(verts); cy=sum(v.y for v in verts)/len(verts)
        if abs(cx-204.7)<6 and abs(cy-384.4)<8: ncols,tag=4,'west_tower'
        elif width>=18: ncols,tag=max(2,int(round(width/BAY))),'mid_step'
        else: ncols,tag=max(2,int(round(width/BAY))),('wide' if width>=10 else 'narrow')
        targets.append(dict(cx=cx,cy=cy,n=N.copy(),u=U.copy(),t0=t0,t1=t1,width=width,z0=z0v,z1=z1v,ncols=ncols,tag=tag,face_c=Vector((cx,cy,(z0v+z1v)/2))))
targets=sorted(targets,key=lambda t:(-t['width'],t['cx'],t['cy']))
kept=[]
for t in targets:
    if any(abs(t['cx']-k['cx'])<1 and abs(t['cy']-k['cy'])<1 and abs(t['z0']-k['z0'])<1 for k in kept): continue
    kept.append(t)
targets=kept

mb_pier=MB('VW_Bohn_W_piers_bands_UNVERIFIED',[M_CONC])
mb_rev=MB('VW_Bohn_W_reveals_UNVERIFIED',[M_REVEAL])
mb_gl=MB('VW_Bohn_W_glass_UNVERIFIED',[M_GLASS])
cells=0
for t in targets:
    U,N=t['u'],t['n']
    t0,t1=t['t0']+MARGIN_T,t['t1']-MARGIN_T
    width=t1-t0; ncols=t['ncols']; bay=width/ncols
    z_lo=t['z0']+MARGIN_Z; z_hi=t['z1']-MARGIN_Z
    n_storeys=max(1,int(round((z_hi-z_lo)/FLOOR)))
    storey_h=(z_hi-z_lo)/n_storeys
    t_ref=t['face_c'].x*U.x+t['face_c'].y*U.y
    def at(tt): return Vector((t['face_c'].x,t['face_c'].y,0))+U*(tt-t_ref)
    for i in range(ncols+1):
        mb_pier.box2(at(t0+i*bay),U,N,PIER_W,-0.01,DEPTH,z_lo,z_hi,0)
    # bands BETWEEN piers only
    for i in range(ncols):
        tt=t0+(i+0.5)*bay; c=at(tt); bw=bay-PIER_W-0.04
        for s_i in range(n_storeys+1):
            if s_i==0: z0b,z1b=z_lo,z_lo+BAND_H
            elif s_i==n_storeys: z0b,z1b=z_hi-BAND_H,z_hi
            else:
                zc=z_lo+s_i*storey_h; z0b,z1b=zc-BAND_H/2,zc+BAND_H/2
            mb_pier.box2(c,U,N,bw,-0.01,DEPTH,z0b,z1b,0)
    for i in range(ncols):
        tt=t0+(i+0.5)*bay; c=at(tt); win_w=bay-PIER_W-0.06
        if win_w<0.55: continue
        for s_i in range(n_storeys):
            z0s=z_lo+s_i*storey_h; z1s=z_lo+(s_i+1)*storey_h
            z0w=z0s+BAND_H+0.03; z1w=z1s-BAND_H-0.03
            if z1w-z0w<0.75: continue
            mb_rev.box2(c,U,N,win_w+0.05,GLASS_OFF,DEPTH-0.01,z0w-0.02,z1w+0.02,0)
            mb_gl.box2(c,U,N,win_w,GLASS_OFF,GLASS_OFF+GLASS_T,z0w,z1w,0)
            cells+=1
o1=mb_pier.done(); o2=mb_rev.done(); o3=mb_gl.done()
print('VW polish piers',len(o1.data.polygons),'reveals',len(o2.data.polygons),'glass',len(o3.data.polygons),'cells',cells,'objs',len(bpy.data.objects))
json.dump({'polish':'bands_between_piers','cells':cells,'n_objs':len(bpy.data.objects)}, open(OUT+'/polish.json','w'))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
