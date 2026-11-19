# ws222d: dark wedge at the Kasser landing SW corner (crossing end): WS214 underfill v289 (-255.541,-53.259) sat at 125.156,
# 1.6 cm above the landing corner (125.14) and the raised WS215 edge (125.143), so the asphalt lapped over the corner. Set to
# 125.135 (flush crossing, 5 mm under the walk corners).
import bpy
e=[o for o in bpy.data.objects if o.name.startswith('WS214_N_berm_tip_gap_asphalt')][0]; M=e.matrix_world; MI=M.inverted()
for i,z in ((289,125.135),):
    v=e.data.vertices[i]; w=M@v.co; assert abs(w.x+255.541)<0.01 and abs(w.y+53.259)<0.01, tuple(w)
    print('F222D v%d z %.3f -> %.3f'%(i,w.z,z),flush=True); w.z=z; v.co=MI@w
e.data.update()
