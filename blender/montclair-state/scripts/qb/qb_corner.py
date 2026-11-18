# qb: blue-grey slivers on narrow wall cells (Dickson SW corner, Calcia corners). pv2/ps cut real openings for the windows,
# but the PE brick shaders still paint procedural window columns (facade U/V maths, replicated below from the node values)
# on any wall face whose UV lands in one. A face that only PARTLY overlaps a shader window (corner piers, wrap-around at a
# corner, cells beside cut openings) shows a glass-coloured strip -> slot 1 = copy of the wall shader with the window mask off.
# Faces that hold a shader window's FULL WIDTH (intended shader-only windows, e.g. Calcia corner bays) are left alone.
# REVERT=1 -> all slot 0, slot removed, copies deleted. UNVERIFIED.
import bpy, os
REV=os.environ.get('REVERT')=='1'
# name: (object, copy name, U pitch, U lo, U hi, V offset, V pitch, V lo, V hi)  (window where lo < (x-off) mod pitch < hi)
CFG={'Dickson':('Dickson Hall walls','QB_Dickson_brick_no_shader_windows_UNVERIFIED',2.4,0.5,1.9,0.0,4.6,1.0,3.6),
     'Calcia':('Calcia Hall walls','QB_Calcia_brick_no_shader_windows_UNVERIFIED',2.4,0.75,1.65,0.1,4.4,0.6,3.8)}
for key in os.environ.get('QB_CORNER_OBJS','Dickson,Calcia').split(','):
    OBN,CN,UP,ULO,UHI,VOF,VP,VLO,VHI=CFG[key]
    o=bpy.data.objects[OBN]; me=o.data
    if CN in bpy.data.materials:
        for p in me.polygons:
            if p.material_index==1: p.material_index=0
        i=[k for k,m in enumerate(me.materials) if m and m.name==CN]
        if i: me.materials.pop(index=i[0])
        bpy.data.materials.remove(bpy.data.materials[CN])
        if 'UNVERIFIED_qb' in o: del o['UNVERIFIED_qb']
        print('REVERTED corner',key)
    if REV: continue
    assert len(me.materials)==1, (key,len(me.materials))
    base=o.material_slots[0].material; cp=base.copy(); cp.name=CN; N=cp.node_tree.nodes; L=cp.node_tree.links
    for l in list(L):
        if l.from_node.name=='Math.015' and l.to_node.name in ('Mix.001','Map Range'): L.remove(l)
    [x for x in N['Mix.001'].inputs if x.identifier=='Factor_Float'][0].default_value=0.0
    N['Map Range'].inputs['Value'].default_value=0.0
    uv=me.uv_layers['facade'].data; WT=float(o.get('win_top',99)); full=0
    def ov(a,b,per,lo,hi,cl=-1e9,ch=1e9):
        k0=int((a-hi)//per)-1; k1=int((b-lo)//per)+1; part=False; whole=False
        for k in range(k0,k1+1):
            L0=max(lo+k*per,cl); H0=min(hi+k*per,ch)
            if H0-L0<0.03: continue
            if min(b,H0)-max(a,L0)>0.03:
                part=True
                if a<=L0+0.01 and b>=H0-0.01: whole=True
        return part,whole
    flag=[]
    for p in me.polygons:
        if abs(p.normal.z)>0.3 or p.area<0.02: continue
        us=[uv[li].uv[0] for li in p.loop_indices]; vv=[uv[li].uv[1] for li in p.loop_indices]
        v0=max(min(vv),0.8); v1=min(max(vv),WT)
        if v1-v0<0.03: continue
        pc,wc=ov(min(us),max(us),UP,ULO,UHI); pr,wr=ov(v0-VOF,v1-VOF,VP,VLO,VHI,0.8-VOF,WT-VOF)
        if not (pc and pr): continue
        if wc: full+=1; continue   # column whole in U: window only split in V (continues in the next cell) -> keep
        flag.append(p.index)
    me.materials.append(cp); assert len(me.materials)==2
    if o.material_slots[1].link!='DATA': o.material_slots[1].link='DATA'
    for i in flag: me.polygons[i].material_index=1
    o['UNVERIFIED_qb']='qb (Nov 2 2026): %d wall faces that only partly overlap a shader window use %s (no painted window slivers)'%(len(flag),CN)
    print('QB_CORNER',key,'flagged',len(flag),'whole-window faces left',full,flag[:30])
