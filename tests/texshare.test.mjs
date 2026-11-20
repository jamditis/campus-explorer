import { test } from 'node:test';
import assert from 'node:assert/strict';
import { dirOf, resolveUri, imageUri, textureKey, createTextureShare, sharedBytes, newBytes } from '../viewer/texshare.js';
import { Texture, SRGBColorSpace, MirroredRepeatWrapping } from '../vendor/three.module.js';

test('a tile resolves image URIs against its own folder, as the glTF spec says', () => {
  assert.equal(dirOf('t_0_0.glb'), '');
  assert.equal(dirOf('lod/t_0_0.glb'), 'lod/');
  assert.equal(resolveUri('./models/main/', 'tex/a.webp'), './models/main/tex/a.webp');
  assert.equal(resolveUri('./models/main/lod/', '../tex/a.webp'), './models/main/tex/a.webp');
  assert.equal(resolveUri('./models/main/' + dirOf('lod/t.glb'), '../tex/a.webp'), './models/main/tex/a.webp');
});

test('imageUri finds the image of a texture, through EXT_texture_webp, or null when it is embedded', () => {
  const json = {
    textures: [{ extensions: { EXT_texture_webp: { source: 1 } } }, { source: 0 }, { source: 2 }],
    images: [{ bufferView: 3, mimeType: 'image/png' }, { uri: '../tex/a.webp' }, { uri: 'data:image/png;base64,AA' }],
  };
  assert.equal(imageUri(json, 0), '../tex/a.webp');
  assert.equal(imageUri(json, 1), null);
  assert.equal(imageUri(json, 2), null);
  assert.equal(imageUri(json, 9), null);
});

test('one texture key per image and way of sampling it', () => {
  const a = new Texture(), b = new Texture();
  a.colorSpace = b.colorSpace = SRGBColorSpace;
  assert.equal(textureKey('u', a), textureKey('u', b));
  assert.notEqual(textureKey('u', a), textureKey('v', a));
  b.wrapS = MirroredRepeatWrapping; assert.notEqual(textureKey('u', a), textureKey('u', b));
  const c = new Texture(); c.colorSpace = SRGBColorSpace; c.repeat.set(2, 2); assert.notEqual(textureKey('u', a), textureKey('u', c));
  const d = new Texture(); assert.notEqual(textureKey('u', a), textureKey('u', d)); // a normal map is not sRGB
});

test('a shared texture is disposed with its last tile, not its first', () => {
  const share = createTextureShare(), disposed = [];
  const tex = n => ({ n, dispose() { disposed.push(n); } });
  const t1 = tex(1), t2 = tex(2);
  assert.equal(share.acquire('tileA', 'k', t1), t1);
  assert.equal(share.acquire('tileB', 'k', t2), t1); // the second tile gets the first one's texture
  assert.equal(share.acquire('tileA', 'k', t1), t1); // twice from one tile counts once
  assert.ok(share.has(t1)); assert.ok(!share.has(t2));
  share.release('tileA'); assert.deepEqual(disposed, []);
  share.release('tileB'); assert.deepEqual(disposed, [1]);
  assert.equal(share.size, 0);
  share.acquire('tileC', 'k', t2); share.acquire('tileC', 'j', t1); share.clear();
  assert.deepEqual(disposed.sort(), [1, 1, 2]);
  assert.equal(share.size, 0);
});

test('shared image bytes count once in the total, and once when they arrive', () => {
  const sizes = { 'tex/a.webp': 100, 'tex/b.webp': 7 };
  const tiles = [{ tex: ['tex/a.webp', 'tex/b.webp'] }, { tex: ['tex/a.webp'] }, {}];
  assert.equal(sharedBytes(tiles, sizes), 107);
  assert.equal(sharedBytes([tiles[1]], sizes), 100);
  const seen = new Set();
  assert.equal(newBytes(tiles[1], seen, sizes), 100);
  assert.equal(newBytes(tiles[0], seen, sizes), 7);
  assert.equal(newBytes(tiles[0], seen, sizes), 0);
  assert.equal(newBytes({ tex: ['tex/missing.webp'] }, seen, sizes), 0); // an older manifest without sizes
});
