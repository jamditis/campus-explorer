import { test } from 'node:test';
import assert from 'node:assert/strict';
import { fixTone } from '../viewer/tone.js';

const color = (r, g, b) => ({
  r, g, b,
  multiplyScalar(s) { this.r *= s; this.g *= s; this.b *= s; return this; },
});
const lum = c => c.r * 0.2126 + c.g * 0.7152 + c.b * 0.0722;

test('fixTone darkens Granite_Curb when the granite image was dropped', () => {
  const c = color(0.8, 0.8, 0.8);
  fixTone('Granite_Curb', c, false);
  const l = lum(c);
  assert.ok(Math.abs(l - 0.8 * 0.44) < 1e-9, `luminance ${l}`);
  assert.ok(l >= 0.25 && l <= 0.36, `mid-grey granite range, got ${l}`);
});

test('fixTone is a no-op when a base-color map is present', () => {
  const c = color(0.8, 0.8, 0.8);
  fixTone('Granite_Curb', c, true);
  assert.equal(lum(c), 0.8);
});

test('fixTone is a no-op for already mid-grey granite and for other stone', () => {
  const grey = color(0.39, 0.385, 0.375);
  const before = lum(grey);
  fixTone('WS35_grey_granite', grey, false);
  assert.equal(lum(grey), before);

  const sill = color(0.86, 0.84, 0.78);
  const sl = lum(sill);
  fixTone('MH_win_sill_cast_stone', sill, false);
  assert.equal(lum(sill), sl);

  const mid = color(0.35, 0.35, 0.35);
  fixTone('Granite_Curb', mid, false);
  assert.equal(lum(mid), 0.35);
});
