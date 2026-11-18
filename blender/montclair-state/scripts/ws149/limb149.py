# ws149: crown-raise (limb-up) campus trees whose leaf cards hang < 2.4 m over PAVING (walks/drives/lots/plazas).
# Evidence/design: treepave149.json (ray probe of every T_* leaf card down onto paving objects); campus/municipal practice
# (ANSI A300 pruning, typical NJ municipal codes) keeps >= 8 ft (2.4 m) clear over sidewalks; MSU walks in Joe's refs show
# limbed-up trees along walks. Deciduous only (conifers over paving: 0 here are left — they are skirted on lawns; UNVERIFIED).
# Method: one shared limbed variant per species mesh (memory-cheap), swapped onto the listed instances only; lawn trees untouched.
import bpy, bmesh, json, math
# ANSI A300 / arborist practice: keep live crown ratio >= 2/3, so a 2.4 m raise only on trees >= 7.2 m tall; smaller trees stay as-is.
L=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws149/treepave149.json'))
MINCARDS=20
DEC=('RedMaple','LondonPlane','PinOak','SugarMaple','TulipPoplar','HoneyLocust','Sweetgum')
pick=[r for r in L if r[2]>=MINCARDS and any(k in r[1] for k in DEC) and 'HIDDEN' not in r[0]]
var={}; n=0; top={}; skip=0
for name,mesh,cnt,clr,loc in pick:
    o=bpy.data.objects.get(name)
    if o is None or o.data.name!=mesh: continue
    sz=max(o.scale.z,1e-3)
    if mesh not in top: top[mesh]=max(v.co.z for v in o.data.vertices)
    if top[mesh]*sz<7.2: skip+=1; continue
    key=(mesh,math.ceil(2*2.4/sz)/2)
    if key not in var:
        src=bpy.data.meshes[mesh]; me=src.copy(); me.name=(mesh[:40]+'_limb24_ws149_'+str(key[1]))[:63]
        leaf={i for i,m in enumerate(me.materials) if m and 'Leaf' in m.name}
        zc=key[1]
        bm=bmesh.new(); bm.from_mesh(me)
        kl=[f for f in bm.faces if f.material_index in leaf and f.calc_center_median().z<zc]
        # bark: remove whole branch ISLANDS (linked bark faces) whose centroid is below the cut, never the trunk island
        bf=[f for f in bm.faces if f.material_index not in leaf]; seen=set(); kb=[]
        isl=[]
        for f0 in bf:
            if f0.index in seen: continue
            st=[f0]; seen.add(f0.index); comp=[]
            while st:
                f=st.pop(); comp.append(f)
                for e in f.edges:
                    for g in e.link_faces:
                        if g.index not in seen and g.material_index not in leaf: seen.add(g.index); st.append(g)
            isl.append(comp)
        trunk=max(isl,key=lambda c:max(v.co.z for f in c for v in f.verts)-min(v.co.z for f in c for v in f.verts)) if isl else []
        for c in isl:
            if c is trunk: continue
            cz=sum(f.calc_center_median().z for f in c)/len(c)
            if cz<zc: kb+=c
        rt=len(isl)
        bmesh.ops.delete(bm,geom=kl+kb,context='FACES'); bm.to_mesh(me); bm.free(); me.update()
        var[key]=me; print("LIMB149_VARIANT",me.name,"bark_islands",rt,"leaf_del",len(kl),"bark_del",len(kb))
    o.data=var[key]; n+=1; print("LIMB149_TREE",name,round(top[mesh]*sz,1),"m tall, cut local",key[1])
print("LIMB149_SWAPPED",n,"skipped_short",skip,"of",len(pick),"variants",len(var))
