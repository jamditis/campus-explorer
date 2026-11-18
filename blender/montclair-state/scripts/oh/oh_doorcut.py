# oh: og wall cut at the Schmitt ESE door stopped ~0.45 m above the landing (stucco/block sill under the door).
# Extend the opening down to the landing (exact boolean on 'Schmitt Hall walls'; original mesh kept as OH_walls_orig_pre_oh, REVERT=1 swaps back).
import bpy, bmesh, os, sys
from mathutils import Vector, Matrix
REV=os.environ.get('REVERT')=='1'
w=bpy.data.objects['Schmitt Hall walls']
orig=bpy.data.meshes.get('OH_walls_orig_pre_oh')
if REV:
    if orig:
        cur=w.data; w.data=orig; orig.name=cur.name+'_tmp'; cur_name=cur.name; bpy.data.meshes.remove(cur); orig.name=cur_name; orig.use_fake_user=False
    print('REVERTED')
else:
    if not orig:
        orig=w.data.copy(); orig.name='OH_walls_orig_pre_oh'; orig.use_fake_user=True
        fr=bpy.data.objects['OG_Schmitt_E_entrance_storefront_frame']; la=bpy.data.objects['OG_Schmitt_E_entrance_landing']
        fv=[fr.matrix_world@v.co for v in fr.data.vertices]; lb=[la.matrix_world@v.co for v in la.data.vertices]
        cen=sum(fv,Vector())/len(fv); lc=sum(lb,Vector())/len(lb)
        out=Vector(((lc-cen).x,(lc-cen).y,0)).normalized(); al=Vector((-out.y,out.x,0))
        # opening edges along the facade from the glass (inside the frame)
        gv=[bpy.data.objects['OG_Schmitt_E_entrance_glass'].matrix_world@v.co for v in bpy.data.objects['OG_Schmitt_E_entrance_glass'].data.vertices]
        a0=min(v.dot(al) for v in fv); a1=max(v.dot(al) for v in fv)
        print('frame along span',round(a1-a0,2))
        bm=bmesh.new(); bmesh.ops.create_cube(bm,size=1.0)
        me=bpy.data.meshes.new('OH_doorcut_tmp'); bm.to_mesh(me)
        cut=bpy.data.objects.new('OH_doorcut_tmp',me); bpy.context.scene.collection.objects.link(cut)
        mid=(a0+a1)/2; c=cen-al*cen.dot(al)+al*mid
        rot=Matrix((al,out,Vector((0,0,1)))).transposed().to_4x4()
        cut.matrix_world=Matrix.Translation((c.x,c.y,(138.76+141.62)/2))@rot@Matrix.Diagonal(((a1-a0)-0.10,3.0,141.62-138.76,1))
        mod=w.modifiers.new('OH_doorcut','BOOLEAN'); mod.operation='DIFFERENCE'; mod.solver='EXACT'; mod.object=cut
        bpy.context.view_layer.objects.active=w
        dg=bpy.context.evaluated_depsgraph_get(); ev=w.evaluated_get(dg); nm=bpy.data.meshes.new_from_object(ev)
        w.modifiers.remove(mod); old=w.data; w.data=nm; nmname=old.name; bpy.data.meshes.remove(old) if old.users==0 else None; nm.name=nmname
        bpy.data.objects.remove(cut); bpy.data.meshes.remove(me)
        print('walls faces',len(orig.polygons),'->',len(w.data.polygons), 'mats',[m.name for m in w.data.materials])
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')
