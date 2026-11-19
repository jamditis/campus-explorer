// Material albedo fixes that do not depend on three.js (unit-tested from node --test).
// The exporter keeps a Mix/Multiply colour factor and drops any image not fed straight
// into Base Color. Granite_Curb is Multiply(Granite002A mean ~0.44 linear, factor 0.8),
// so the glTF factor 0.8 is not the Blender albedo (~0.35). The viewer then applies a
// mean-normalised CC0 stone texture, and the curbs read near-white. Restore
// factor × texture mean when the image is absent. `color` is a three.js Color (or a
// stand-in with r,g,b and multiplyScalar).
export function fixTone(name, color, hasMap) {
  if (hasMap || !color) return color;
  if (/granite/i.test(name) && /curb/i.test(name)) {
    const l = color.r * 0.2126 + color.g * 0.7152 + color.b * 0.0722;
    if (l > 0.5) color.multiplyScalar(0.44); // Granite002A mean ~0.44 linear
  }
  return color;
}
