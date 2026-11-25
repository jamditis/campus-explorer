# ws239 subset-render fix: objects appended with a non-identity transform keep an identity matrix_world until the depsgraph
# is evaluated, so cutrend189's bbox cull hid them (all m2c239 objects with their own origin went missing from WIPs).
import bpy
bpy.context.view_layer.update()
