import bpy
from mathutils import Vector
G=bpy.data.objects['TJ_Blanton_entrance_1_glass_UNVERIFIED']; F=bpy.data.objects['TJ_Blanton_entrance_1_frame_UNVERIFIED']
gv=[G.matrix_world@v.co for v in G.data.vertices]; c=sum(gv,Vector())/len(gv)
fv=[F.matrix_world@v.co for v in F.data.vertices]; fc=sum(fv,Vector())/len(fv)
n=(fc-c); n.z=0; n.normalize()
loc=c+n*9+Vector((0,0,9)); cd=bpy.data.cameras.new('TU_TMP'); cd.lens=30
co=bpy.data.objects.new('TU_TMP',cd); bpy.context.scene.collection.objects.link(co); co.location=loc
co.rotation_euler=(c+Vector((0,0,0.5))-loc).to_track_quat('-Z','Y').to_euler(); print('TMPCAM',loc,c)
