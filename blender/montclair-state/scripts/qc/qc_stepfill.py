# qc: pre-existing open gap at Calcia's west step (y 196.9-198.35): the pt wall-top infill stops at y 196.93, so between the
# low west wall top (z 144.45-145.20) and the roof/infill top (147.42) there was a ~1.4 m x 2.5 m hole, plus a triangle above
# the sloped top of the south-facing step face (x -106.81..-105.73). Both are closed by brick infill faces in the exact wall
# planes, bridging the exact wall-top vertices (no overlap with existing faces). Facade UVs from a least-squares fit of the
# adjacent wall cells (66 / 67), no-window brick shader copy. REVERT=1 removes the object. UNVERIFIED.
import bpy, bmesh, os
import numpy as np
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; ON='QC_Calcia_west_step_gap_infill_UNVERIFIED'
if ON in bpy.data.objects:
    o=bpy.data.objects[ON]; m=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(m); print('REVERTED_QC_STEPFILL')
if not REV:
    w=bpy.data.objects['Calcia Hall walls']; me=w.data; mw=w.matrix_world; uv=me.uv_layers['facade'].data
    def fit(fi):  # 3D -> UV affine (least squares) of wall cell fi
        p=me.polygons[fi]; P=[mw@me.vertices[me.loops[l].vertex_index].co for l in p.loop_indices]; U=[uv[l].uv for l in p.loop_indices]
        A=np.array([[q.x,q.y,q.z,1] for q in P]); X,_,_,_=np.linalg.lstsq(A,np.array([[u.x,u.y] for u in U]),rcond=None)
        return lambda q: (float(np.dot([q.x,q.y,q.z,1],X[:,0])),float(np.dot([q.x,q.y,q.z,1],X[:,1])))
    # find wall cells by their known corner coordinates (robust to index changes)
    def cell_with(*pts):
        for p in me.polygons:
            V=[mw@me.vertices[v].co for v in p.vertices]
            if all(any((v-Vector(q)).length<0.01 for v in V) for q in pts): return p.index
        raise Exception('cell not found %s'%(pts,))
    T=147.42
    W=[(-106.897,196.932,144.447),(-106.89,197.033,144.501),(-106.835,197.93,144.977),(-106.809,198.353,145.202)]
    c66=cell_with(W[2],W[3]); c67=cell_with((-106.809,198.353,145.202),(-105.73,198.29,147.366))
    f66=fit(c66); f67=fit(c67)
    bm=bmesh.new(); ul=bm.loops.layers.uv.new('facade')
    def face(pts,f):
        vs=[bm.verts.new(Vector(q)) for q in pts]; fc=bm.faces.new(vs)
        for l in fc.loops: l[ul].uv=f(l.vert.co)
        return fc
    strip=W+[(W[3][0],W[3][1],T),(W[0][0],W[0][1],T)]
    face(list(reversed(strip)),f66)
    face([(-105.73,198.29,147.366),(-105.73,198.29,T),(-106.809,198.353,T),(-106.809,198.353,145.202)],f67)
    m=bpy.data.meshes.new(ON); bm.to_mesh(m); bm.free()
    m.materials.append(bpy.data.materials['QB_Calcia_brick_no_shader_windows_UNVERIFIED'])
    o=bpy.data.objects.new(ON,m); w.users_collection[0].objects.link(o)
    for p in m.polygons: print('QC_STEPFILL face n',tuple(round(x,2) for x in p.normal),'area %.2f'%p.area)
    print('QC_STEPFILL cells',c66,c67)
