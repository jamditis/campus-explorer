"""Denoise a multilayer EXR from render_views.py (EXR=1) with OIDN in the compositor; writes JPEG with the scene's view transform.
blender -b --factory-startup --python denoise_exr.py -- in.exr out.jpg view_transform look exposure"""
import bpy, sys
a = sys.argv[sys.argv.index('--') + 1:]; src, dst, vt, look, expo = a[0], a[1], a[2], a[3], float(a[4])
sc = bpy.context.scene
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
im = bpy.data.images.load(src); im.reload(); _ = im.pixels[0] if im.size[0] else None
rx, ry = (int(a[5]), int(a[6])) if len(a) > 6 else tuple(im.size); sc.render.resolution_x, sc.render.resolution_y = rx, ry; print('SIZE', rx, ry); sc.render.resolution_percentage = 100
sc.view_settings.view_transform = vt; sc.view_settings.look = look; sc.view_settings.exposure = expo
sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 92; sc.render.filepath = dst
sc.use_nodes = True; nt = sc.node_tree; nt.nodes.clear()
n_im = nt.nodes.new('CompositorNodeImage'); n_im.image = im
dn = nt.nodes.new('CompositorNodeDenoise'); dn.prefilter = 'ACCURATE'
out = nt.nodes.new('CompositorNodeComposite')
o = {s.name: s for s in n_im.outputs}; print('PASSES', list(o))
nt.links.new(o.get('Image') or o['Combined'], dn.inputs['Image']); nt.links.new(o['Denoising Normal'], dn.inputs['Normal']); nt.links.new(o['Denoising Albedo'], dn.inputs['Albedo'])
nt.links.new(dn.outputs['Image'], out.inputs['Image'])
bpy.ops.render.render(write_still=True); print('DENOISED', dst)
