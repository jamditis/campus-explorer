exec(open('scripts/nx/nx_build.py').read())
c=bpy.data.cameras.new('NX_TMP_aerial_patch'); c.lens=35; o=bpy.data.objects.new('NX_TMP_aerial_patch',c); bpy.context.scene.collection.objects.link(o)
o.location=(-14,26.0,158); o.rotation_euler=(0,0,0)
exec(open('scripts/nx/nx_render.py').read())
