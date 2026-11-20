// Pure. Images several tiles share (models/main/tex/, written by tools/web-export/share_tex.mjs): resolving
// their URIs, one THREE.Texture per image across tiles, and their bytes in the download progress.
// No three import: textures here are anything with dispose().

/** Folder part of a manifest path, with its slash: `lod/t_0_0.glb` -> `lod/`. */
export function dirOf(path) {
  const i = path.lastIndexOf('/');
  return i < 0 ? '' : path.slice(0, i + 1);
}

/** `uri` relative to the folder `base` (ending in a slash), with `..` folded: what the browser would fetch. */
export function resolveUri(base, uri) {
  const out = [];
  for (const part of (base + uri).split('/')) {
    if (part === '..' && out.length && out.at(-1) !== '..' && out.at(-1) !== '.') out.pop();
    else out.push(part);
  }
  return out.join('/');
}

/** URI of the image a glTF texture shows (EXT_texture_webp first, as GLTFLoader reads it), or null when embedded. */
export function imageUri(json, textureIndex) {
  const t = json.textures?.[textureIndex]; if (!t) return null;
  const uri = json.images?.[t.extensions?.EXT_texture_webp?.source ?? t.source]?.uri;
  return uri && !uri.startsWith('data:') ? uri : null;
}

/** Textures may be shared when they show the same file the same way: sampler, colour space, UV set, transform. */
export function textureKey(url, t) {
  return [url, t.wrapS, t.wrapT, t.magFilter, t.minFilter, t.flipY, t.colorSpace, t.channel, t.generateMipmaps,
    t.offset.x, t.offset.y, t.repeat.x, t.repeat.y, t.rotation, t.center.x, t.center.y].join('|');
}

/**
 * One texture per key across tiles. `acquire(owner, key, texture)` returns the texture to use (an earlier
 * owner's, or this one); `release(owner)` disposes the textures no owner uses any more; `has(texture)` tells
 * a shared texture apart from a tile's own, which the tile disposes itself.
 */
export function createTextureShare() {
  const byKey = new Map(), owned = new Map(), mine = new Set();
  return {
    acquire(owner, key, texture) {
      let e = byKey.get(key);
      if (!e) { e = { texture, users: new Set() }; byKey.set(key, e); mine.add(texture); }
      e.users.add(owner);
      if (!owned.has(owner)) owned.set(owner, new Set());
      owned.get(owner).add(key);
      return e.texture;
    },
    release(owner) {
      for (const key of owned.get(owner) ?? []) {
        const e = byKey.get(key); if (!e) continue;
        e.users.delete(owner);
        if (!e.users.size) { e.texture.dispose(); byKey.delete(key); mine.delete(e.texture); }
      }
      owned.delete(owner);
    },
    has: texture => mine.has(texture),
    clear() { for (const e of byKey.values()) e.texture.dispose(); byKey.clear(); owned.clear(); mine.clear(); },
    get size() { return byKey.size; },
  };
}

/** Bytes of the shared images `tiles` name (manifest `tex` lists), each image once. */
export function sharedBytes(tiles, sizes) {
  const files = new Set(tiles.flatMap(t => t.tex ?? []));
  let n = 0; for (const f of files) n += sizes[f] ?? 0;
  return n;
}

/** Bytes of the shared images of `tile` not counted yet; marks them counted in `seen`. */
export function newBytes(tile, seen, sizes) {
  let n = 0;
  for (const f of tile.tex ?? []) if (!seen.has(f)) { seen.add(f); n += sizes[f] ?? 0; }
  return n;
}
