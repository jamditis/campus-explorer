// Keyboard, mouse (pointer lock), touch and gamepad -> one intent object for the fly and walk controller.
// No three.js and no DOM access at import time, so node can load the pure helpers for unit tests.

const MOUSE_SENSITIVITY = 0.0022; // rad per pixel
const TOUCH_LOOK = 0.004; // rad per pixel
const STICK_RADIUS = 56; // px
const STICK_RUN = 0.9;
const STICK_ZONE = 0.45; // left share of the canvas that spawns the move stick
const PAD_DEAD = 0.15;
const PAD_LOOK_RATE = 2.4; // rad/s at full deflection
const PINCH_SCALE = 100; // px of pinch per unit of zoom
const WHEEL_SCALE = 100; // px of wheel per unit of zoom

const USED_CODES = new Set([
  'KeyW', 'KeyA', 'KeyS', 'KeyD',
  'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight',
  'ShiftLeft', 'ShiftRight', 'Space', 'KeyQ', 'KeyC', 'KeyE',
]);
const FLY_ONLY_CODES = new Set(['KeyQ', 'KeyC', 'KeyE']);

/**
 * Radial dead zone with rescaling: output is 0 at the dead zone edge and reaches 1 at full deflection.
 * @returns {[number, number]}
 */
export function applyDeadZone(x, y, dead) {
  const mag = Math.hypot(x, y);
  if (!(mag > dead)) return [0, 0];
  const scaled = Math.min(1, (mag - dead) / (1 - dead));
  const k = scaled / mag;
  return [x * k, y * k];
}

/**
 * Clamp a 2D vector to length 1, keeping its direction.
 * @returns {[number, number]}
 */
export function clampUnit(x, z) {
  const len = Math.hypot(x, z);
  if (len <= 1) return [x, z];
  return [x / len, z / len];
}

/**
 * Held keyboard codes -> movement axes. Space rises in fly mode; in walk mode it jumps, which is an edge, not an axis.
 * @param {Set<string>} pressed set of KeyboardEvent.code values
 * @param {'fly'|'walk'} mode
 * @returns {{moveX: number, moveZ: number, rise: number, run: boolean}}
 */
export function keysToAxes(pressed, mode) {
  const has = (...codes) => codes.some((c) => pressed.has(c));
  const moveX = (has('KeyD', 'ArrowRight') ? 1 : 0) - (has('KeyA', 'ArrowLeft') ? 1 : 0);
  const moveZ = (has('KeyW', 'ArrowUp') ? 1 : 0) - (has('KeyS', 'ArrowDown') ? 1 : 0);
  let rise = 0;
  if (mode === 'fly') rise = (has('Space', 'KeyE') ? 1 : 0) - (has('KeyQ', 'KeyC') ? 1 : 0);
  const [x, z] = clampUnit(moveX, moveZ);
  return { moveX: x, moveZ: z, rise, run: has('ShiftLeft', 'ShiftRight') };
}

/**
 * Finger offset from the stick centre (screen pixels, +y down) -> stick output.
 * knobX/knobY are where to draw the thumb, limited to the ring.
 * @returns {{moveX: number, moveZ: number, amount: number, knobX: number, knobY: number}}
 */
export function stickFromTouch(dx, dy, radius) {
  const dist = Math.hypot(dx, dy);
  if (!(dist > 0) || !(radius > 0)) return { moveX: 0, moveZ: 0, amount: 0, knobX: 0, knobY: 0 };
  const amount = Math.min(1, dist / radius);
  const ux = dx / dist;
  const uy = dy / dist;
  return {
    moveX: ux * amount,
    moveZ: -uy * amount,
    amount,
    knobX: ux * amount * radius,
    knobY: uy * amount * radius,
  };
}

// Squared response keeps small stick movements precise while full deflection still turns fast.
function lookCurve(x, y) {
  const mag = Math.hypot(x, y);
  return mag > 0 ? [x * mag, y * mag] : [0, 0];
}

// A focused button only swallows Space (which would press it); after clicking a mode button the
// focus stays there, and WASD and arrows should still move.
function isTypingTarget(el, code) {
  if (!el || typeof el !== 'object') return false;
  if (el.isContentEditable) return true;
  const tag = el.tagName;
  if (tag === 'BUTTON') return code === 'Space';
  return tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA';
}

function clamp1(v) {
  return Math.max(-1, Math.min(1, v));
}

/**
 * Wire keyboard, mouse, touch and gamepad on `canvas`; touch controls go in `overlay`.
 * update(dt) once per frame returns the shared intent object.
 */
export function createInput(canvas, overlay, options = {}) {
  const doc = canvas.ownerDocument;
  const win = doc.defaultView;
  const host = overlay || canvas.parentElement;
  const mouseSensitivity = options.mouseSensitivity ?? MOUSE_SENSITIVITY;

  const intent = { moveX: 0, moveZ: 0, lookX: 0, lookY: 0, rise: 0, run: false, jump: false, zoom: 0, active: false };

  let enabled = false;
  let mode = 'fly';
  let kind = 'keyboard';
  let locked = false;
  let lockFailed = false;
  let touchSeen = false;
  let savedTouchAction = null;

  const keys = new Set();
  let jumpPending = false;
  let lookX = 0;
  let lookY = 0;
  let zoom = 0;
  let mouseDrag = null; // pointerId of a primary-button fallback drag
  let buttonRise = 0;
  let padJumpWas = false;

  // Touch state: one move stick, any number of look touches (two of them pinch).
  let stick = null; // { id, x, y, moveX, moveZ, run }
  const lookTouches = new Map(); // id -> { x, y }
  let pinchDist = 0;

  const listeners = [];
  const changeFns = new Set();

  function on(target, type, fn, opts) {
    target.addEventListener(type, fn, opts);
    listeners.push(() => target.removeEventListener(type, fn, opts));
  }

  function emitChange() {
    for (const fn of changeFns) fn({ locked, kind });
  }

  function setKind(next) {
    if (kind === next) return;
    kind = next;
    emitChange();
  }

  // --- touch controls (DOM) ---
  const stickEl = doc.createElement('div');
  stickEl.className = 'touch-stick';
  stickEl.hidden = true;
  stickEl.setAttribute('aria-hidden', 'true');
  const thumbEl = doc.createElement('div');
  thumbEl.className = 'touch-thumb';
  stickEl.appendChild(thumbEl);

  const buttonsEl = doc.createElement('div');
  buttonsEl.className = 'touch-buttons';
  buttonsEl.hidden = true;

  function makeButton(text, label, extra) {
    const b = doc.createElement('button');
    b.type = 'button';
    b.className = `touch-btn ${extra}`;
    b.textContent = text;
    b.setAttribute('aria-label', label);
    buttonsEl.appendChild(b);
    return b;
  }
  const upBtn = makeButton('Up', 'Fly up', 'touch-up');
  const downBtn = makeButton('Down', 'Fly down', 'touch-down');
  const jumpBtn = makeButton('Jump', 'Jump', 'touch-jump');

  host.appendChild(stickEl);
  host.appendChild(buttonsEl);

  function refreshTouchUi() {
    const show = enabled && touchSeen;
    buttonsEl.hidden = !show;
    upBtn.hidden = mode !== 'fly';
    downBtn.hidden = mode !== 'fly';
    jumpBtn.hidden = mode !== 'walk';
    if (!show || !stick) stickEl.hidden = true;
  }

  function drawStick() {
    if (!stick) {
      stickEl.hidden = true;
      return;
    }
    const rect = host.getBoundingClientRect();
    stickEl.style.left = `${stick.x - rect.left}px`;
    stickEl.style.top = `${stick.y - rect.top}px`;
    thumbEl.style.transform = `translate(${stick.knobX}px, ${stick.knobY}px)`;
    stickEl.hidden = false;
  }

  function holdButton(btn, value) {
    // Pointer events (not click) so holding works and release anywhere stops the motion.
    const pressed = new Set();
    const down = (e) => {
      if (!enabled) return;
      e.preventDefault();
      touchSeen = true;
      if (e.pointerType === 'touch') setKind('touch');
      pressed.add(e.pointerId);
      try { btn.setPointerCapture(e.pointerId); } catch { /* not capturable; release still arrives */ }
      buttonRise = value;
      btn.classList.add('touch-held');
    };
    const up = (e) => {
      if (!pressed.delete(e.pointerId)) return;
      if (pressed.size > 0) return;
      btn.classList.remove('touch-held');
      if (buttonRise === value) buttonRise = 0;
    };
    on(btn, 'pointerdown', down);
    on(btn, 'pointerup', up);
    on(btn, 'pointercancel', up);
    on(btn, 'lostpointercapture', up);
    on(btn, 'contextmenu', (e) => e.preventDefault());
  }
  holdButton(upBtn, 1);
  holdButton(downBtn, -1);

  on(jumpBtn, 'pointerdown', (e) => {
    if (!enabled) return;
    e.preventDefault();
    if (e.pointerType === 'touch') setKind('touch');
    jumpPending = true;
  });
  // Keyboard or assistive activation fires click with detail 0; pointer presses were handled above.
  on(jumpBtn, 'click', (e) => {
    if (enabled && e.detail === 0) jumpPending = true;
  });
  on(jumpBtn, 'contextmenu', (e) => e.preventDefault());

  // --- keyboard ---
  on(win, 'keydown', (e) => {
    if (!USED_CODES.has(e.code)) return;
    if (!enabled || e.ctrlKey || e.altKey || e.metaKey) return;
    if (isTypingTarget(e.target, e.code) || isTypingTarget(doc.activeElement, e.code)) return;
    if (mode !== 'fly' && FLY_ONLY_CODES.has(e.code)) return;
    e.preventDefault();
    setKind('keyboard');
    if (e.code === 'Space' && mode === 'walk' && !e.repeat) jumpPending = true;
    keys.add(e.code);
  });
  // Releases are always honoured, wherever focus is, so a key never sticks.
  on(win, 'keyup', (e) => {
    if (!keys.delete(e.code)) return;
    if (enabled) e.preventDefault();
  });
  on(win, 'blur', () => releaseAll());
  on(doc, 'visibilitychange', () => {
    if (doc.hidden) releaseAll();
  });

  // --- mouse ---
  const canLock = typeof canvas.requestPointerLock === 'function';

  on(canvas, 'click', (e) => {
    if (!enabled || !canLock || locked || e.pointerType === 'touch') return;
    if (lockFailed) return;
    try {
      const p = canvas.requestPointerLock();
      if (p && typeof p.catch === 'function') p.catch(() => { lockFailed = true; });
    } catch {
      lockFailed = true;
    }
  });
  on(doc, 'pointerlockchange', () => {
    const now = doc.pointerLockElement === canvas;
    if (now === locked) return;
    locked = now;
    if (locked) setKind('keyboard');
    emitChange();
  });
  on(doc, 'pointerlockerror', () => { lockFailed = true; });
  on(doc, 'mousemove', (e) => {
    if (!enabled || !locked) return;
    lookX += e.movementX * mouseSensitivity;
    lookY -= e.movementY * mouseSensitivity;
  });

  on(canvas, 'wheel', (e) => {
    if (!enabled) return;
    e.preventDefault();
    const unit = e.deltaMode === 1 ? 16 : e.deltaMode === 2 ? 800 : 1;
    zoom -= (e.deltaY * unit) / WHEEL_SCALE;
  }, { passive: false });

  // --- pointer events: mouse drag fallback and touch ---
  on(canvas, 'pointerdown', (e) => {
    if (e.pointerType === 'touch') {
      if (!touchSeen) {
        touchSeen = true;
        refreshTouchUi();
      }
      if (!enabled) return;
      setKind('touch');
      e.preventDefault();
      try { canvas.setPointerCapture(e.pointerId); } catch { /* still get moves while over the canvas */ }
      const rect = canvas.getBoundingClientRect();
      const inStickZone = e.clientX - rect.left < rect.width * STICK_ZONE;
      if (inStickZone && !stick) {
        stick = { id: e.pointerId, x: e.clientX, y: e.clientY, moveX: 0, moveZ: 0, run: false, knobX: 0, knobY: 0 };
        drawStick();
      } else {
        lookTouches.set(e.pointerId, { x: e.clientX, y: e.clientY });
        pinchDist = currentPinch();
      }
      return;
    }
    if (!enabled || e.pointerType !== 'mouse' || e.button !== 0 || locked) return;
    // Drag-to-look only when pointer lock is not an option.
    if (canLock && !lockFailed) return;
    mouseDrag = { id: e.pointerId, x: e.clientX, y: e.clientY };
    try { canvas.setPointerCapture(e.pointerId); } catch { /* moves still arrive over the canvas */ }
  });

  on(canvas, 'pointermove', (e) => {
    if (stick && e.pointerId === stick.id) {
      const s = stickFromTouch(e.clientX - stick.x, e.clientY - stick.y, STICK_RADIUS);
      stick.moveX = s.moveX;
      stick.moveZ = s.moveZ;
      stick.run = s.amount > STICK_RUN;
      stick.knobX = s.knobX;
      stick.knobY = s.knobY;
      drawStick();
      return;
    }
    const t = lookTouches.get(e.pointerId);
    if (t) {
      const dx = e.clientX - t.x;
      const dy = e.clientY - t.y;
      t.x = e.clientX;
      t.y = e.clientY;
      if (lookTouches.size >= 2) {
        const d = currentPinch();
        zoom += (d - pinchDist) / PINCH_SCALE;
        pinchDist = d;
      } else {
        lookX += dx * TOUCH_LOOK;
        lookY -= dy * TOUCH_LOOK;
      }
      return;
    }
    if (mouseDrag && e.pointerId === mouseDrag.id) {
      if (!(e.buttons & 1)) {
        mouseDrag = null;
        return;
      }
      lookX += (e.clientX - mouseDrag.x) * mouseSensitivity;
      lookY -= (e.clientY - mouseDrag.y) * mouseSensitivity;
      mouseDrag.x = e.clientX;
      mouseDrag.y = e.clientY;
    }
  });

  function endPointer(e) {
    if (stick && e.pointerId === stick.id) {
      stick = null;
      drawStick();
    }
    if (lookTouches.delete(e.pointerId)) pinchDist = currentPinch();
    if (mouseDrag && e.pointerId === mouseDrag.id) mouseDrag = null;
  }
  on(canvas, 'pointerup', endPointer);
  on(canvas, 'pointercancel', endPointer);

  function currentPinch() {
    if (lookTouches.size < 2) return 0;
    const [a, b] = lookTouches.values();
    return Math.hypot(a.x - b.x, a.y - b.y);
  }

  function releaseAll() {
    keys.clear();
    jumpPending = false;
    buttonRise = 0;
    upBtn.classList.remove('touch-held');
    downBtn.classList.remove('touch-held');
    stick = null;
    lookTouches.clear();
    pinchDist = 0;
    mouseDrag = null;
    lookX = 0;
    lookY = 0;
    zoom = 0;
    drawStick();
  }

  function readPad() {
    const nav = win.navigator;
    if (!nav || typeof nav.getGamepads !== 'function') return null;
    let pads;
    try { pads = nav.getGamepads(); } catch { return null; }
    if (!pads) return null;
    for (const p of pads) if (p && p.connected !== false) return p;
    return null;
  }

  function zeroIntent() {
    intent.moveX = 0;
    intent.moveZ = 0;
    intent.lookX = 0;
    intent.lookY = 0;
    intent.rise = 0;
    intent.run = false;
    intent.jump = false;
    intent.zoom = 0;
    intent.active = false;
  }

  function update(dt = 0) {
    if (!enabled) {
      lookX = 0;
      lookY = 0;
      zoom = 0;
      jumpPending = false;
      zeroIntent();
      return intent;
    }

    const k = keysToAxes(keys, mode);
    let moveX = k.moveX;
    let moveZ = k.moveZ;
    let rise = k.rise + (mode === 'fly' ? buttonRise : 0);
    let run = k.run;
    let jump = jumpPending && mode === 'walk';
    let lx = lookX;
    let ly = lookY;

    if (stick) {
      moveX += stick.moveX;
      moveZ += stick.moveZ;
      run = run || stick.run;
    }

    const pad = readPad();
    if (pad) {
      const ax = (i) => (Number.isFinite(pad.axes?.[i]) ? pad.axes[i] : 0);
      const btn = (i) => {
        const b = pad.buttons?.[i];
        if (b == null) return 0;
        if (typeof b === 'number') return b;
        return b.pressed ? Math.max(b.value || 0, 1) : b.value || 0;
      };
      const [mx, my] = applyDeadZone(ax(0), ax(1), PAD_DEAD);
      const [rx0, ry0] = applyDeadZone(ax(2), ax(3), PAD_DEAD);
      const [rx, ry] = lookCurve(rx0, ry0);
      moveX += mx;
      moveZ -= my; // stick up is negative y
      lx += rx * PAD_LOOK_RATE * dt;
      ly -= ry * PAD_LOOK_RATE * dt;
      const padRun = btn(10) > 0.5 || btn(1) > 0.5 || btn(7) > 0.5;
      run = run || padRun;
      const a = btn(0) > 0.5;
      if (mode === 'walk') {
        if (a && !padJumpWas) jump = true;
      } else {
        // A has nothing to jump in fly mode, so it rises like Space does.
        rise += (a ? 1 : 0) + (btn(5) > 0.5 ? 1 : 0) - (btn(4) > 0.5 ? 1 : 0);
      }
      padJumpWas = a;
      const used = mx !== 0 || my !== 0 || rx0 !== 0 || ry0 !== 0
        || (pad.buttons || []).some((b) => (typeof b === 'number' ? b > 0.5 : b && b.pressed));
      if (used) setKind('gamepad');
    } else {
      padJumpWas = false;
    }

    [moveX, moveZ] = clampUnit(moveX, moveZ);
    rise = clamp1(rise);

    intent.moveX = moveX;
    intent.moveZ = moveZ;
    intent.lookX = lx;
    intent.lookY = ly;
    intent.rise = rise;
    intent.run = run;
    intent.jump = jump;
    intent.zoom = zoom;
    intent.active = moveX !== 0 || moveZ !== 0 || lx !== 0 || ly !== 0 || rise !== 0 || jump || zoom !== 0;

    lookX = 0;
    lookY = 0;
    zoom = 0;
    jumpPending = false;
    return intent;
  }

  function setEnabled(onFlag) {
    const next = !!onFlag;
    if (next === enabled) return;
    enabled = next;
    if (enabled) {
      savedTouchAction = canvas.style.touchAction;
      canvas.style.touchAction = 'none';
    } else {
      if (savedTouchAction !== null) canvas.style.touchAction = savedTouchAction;
      savedTouchAction = null;
      releaseAll();
      if (locked && doc.exitPointerLock) doc.exitPointerLock();
    }
    refreshTouchUi();
  }

  function setMode(next) {
    if (next !== 'fly' && next !== 'walk') return;
    if (next === mode) return;
    mode = next;
    // Space means different things in each mode; drop held state so it is not misread.
    keys.clear();
    buttonRise = 0;
    jumpPending = false;
    refreshTouchUi();
  }

  function dispose() {
    for (const off of listeners.splice(0)) off();
    changeFns.clear();
    if (enabled && savedTouchAction !== null) canvas.style.touchAction = savedTouchAction;
    if (locked && doc.pointerLockElement === canvas && doc.exitPointerLock) doc.exitPointerLock();
    enabled = false;
    stickEl.remove();
    buttonsEl.remove();
  }

  refreshTouchUi();

  return {
    intent,
    update,
    setEnabled,
    setMode,
    get locked() { return locked; },
    get kind() { return kind; },
    onChange(fn) {
      changeFns.add(fn);
      return () => changeFns.delete(fn);
    },
    dispose,
  };
}
