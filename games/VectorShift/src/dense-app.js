(function () {
  "use strict";
  const C = window.VectorShiftDenseCore,
    L = DENSE_LEVELS,
    channel = window.VS_CHANNEL || "demo",
    en =
      channel !== "demo" ||
      new URLSearchParams(location.search).get("lang") === "en";
  const $ = (id) => document.getElementById(id),
    cv = $("puzzleCanvas"),
    ctx = cv.getContext("2d"),
    P = 32,
    PAD = 18,
    W = P * 0.81,
    TAU = Math.PI * 2,
    DIR = [
      [0, -1],
      [1, 0],
      [0, 1],
      [-1, 0],
    ],
    STORE = "vector-shift-dense-v1";
  const colors = [
    ["#4588d7", "#93c6f6", "#2459a3", "#31517c"],
    ["#edbd3f", "#ffeb99", "#ce8a20", "#99632c"],
    ["#85bb42", "#d3e99c", "#4f8f25", "#4d702f"],
    ["#e77d9a", "#ffc8d6", "#bd4b73", "#98506a"],
    ["#e06a48", "#ffb289", "#b3382b", "#8b4134"],
    ["#ac7fd6", "#dfc3f4", "#7f4eb5", "#694d88"],
  ];
  const tr = (zh, eng) => (en ? eng : zh);
  const words = {
    start: tr("循着它的朝向，找到出口。", "Follow their gaze. Find a way out."),
    block: tr(
      "前面有点挤，先帮它清开路。",
      "A little crowded ahead. Clear its path first.",
    ),
    released: tr("又解开了一点。", "A little more room to breathe."),
    hint: tr("这条小蛇的前方畅通。", "This one has a clear path."),
    collection: tr("挑一幅图案", "The collection"),
    close: tr("关闭", "Close"),
  };
  let store = {};
  try {
    store = JSON.parse(localStorage.getItem(STORE) || "{}") || {};
  } catch {}
  if (typeof store !== "object" || Array.isArray(store)) store = {};
  let settings = {
      sound: !!store.settings?.sound,
      haptics: !!store.settings?.haptics,
      reduce: !!store.settings?.reduce,
    },
    runs =
      store.runs && typeof store.runs === "object" && !Array.isArray(store.runs)
        ? store.runs
        : {},
    completed =
      store.completed &&
      typeof store.completed === "object" &&
      !Array.isArray(store.completed)
        ? store.completed
        : {};
  let index = 0,
    state,
    models = new Map(),
    world = { w: 1, h: 1 },
    display = { w: 1, h: 1, s: 1, dpr: 1 },
    view = { zoom: 1, x: 0, y: 0 },
    animations = [],
    raf = 0,
    selected = null,
    hinted = null,
    hintUntil = 0,
    blocked = null,
    blockUntil = 0,
    focusId = null;
  let mistakes = 0,
    hints = 0,
    baseTime = 0,
    started = performance.now(),
    finished = null,
    epoch = 0,
    finishTimer = 0,
    msgTimer = 0,
    previousFocus = null,
    audioCtx = null,
    paused = document.hidden;
  const motion = matchMedia("(prefers-reduced-motion: reduce)"),
    reduce = () => motion.matches || settings.reduce,
    lv = () => L[index],
    title = (l) => (en ? l.titleEn || l.title : l.title);
  const escape = (s) =>
    String(s).replace(
      /[&<>"']/g,
      (c) =>
        ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#39;",
        })[c],
    );
  const savedNumber = (value, integer = false) => {
    const n = Number(value);
    return Number.isFinite(n) && n >= 0 && n <= Number.MAX_SAFE_INTEGER
      ? integer
        ? Math.floor(n)
        : n
      : 0;
  };
  const icon = (n) => `<svg aria-hidden="true"><use href="#i-${n}"/></svg>`;
  const elapsed = () =>
    finished === null
      ? baseTime + (paused ? 0 : performance.now() - started)
      : finished;
  const time = (ms) => {
    const s = Math.floor(ms / 1000);
    return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
  };
  function save() {
    if (!state) return;
    runs[lv().id] = { state, elapsed: elapsed(), mistakes, hints };
    try {
      localStorage.setItem(
        STORE,
        JSON.stringify({ version: 1, index, settings, runs, completed }),
      );
    } catch {}
  }
  function message(text, type = "") {
    clearTimeout(msgTimer);
    $("feedback").textContent = text;
    $("feedback").className = "feedback " + type;
    if (text !== words.start)
      msgTimer = setTimeout(() => {
        if (state.remaining.length) {
          $("feedback").textContent = words.start;
          $("feedback").className = "feedback";
        }
      }, 2300);
  }
  function sound(kind) {
    if (settings.haptics && navigator.vibrate)
      navigator.vibrate(kind === "blocked" ? [8, 25, 8] : 7);
    if (!settings.sound) return;
    try {
      audioCtx =
        audioCtx || new (window.AudioContext || window.webkitAudioContext)();
      audioCtx.resume();
      const now = audioCtx.currentTime,
        notes =
          kind === "win"
            ? [523, 659, 784]
            : kind === "blocked"
              ? [155]
              : [440 + (state.moves % 5) * 35, 660];
      notes.forEach((n, i) => {
        const o = audioCtx.createOscillator(),
          g = audioCtx.createGain(),
          t = now + i * 0.055;
        o.frequency.setValueAtTime(n, t);
        o.frequency.exponentialRampToValueAtTime(
          n * (kind === "blocked" ? 0.8 : 1.03),
          t + 0.13,
        );
        g.gain.setValueAtTime(0, t);
        g.gain.linearRampToValueAtTime(0.035 / notes.length, t + 0.012);
        g.gain.exponentialRampToValueAtTime(0.0001, t + 0.19);
        o.connect(g);
        g.connect(audioCtx.destination);
        o.start(t);
        o.stop(t + 0.21);
      });
    } catch {}
  }
  const centers = (a) =>
    a.cells.map(([x, y]) => ({
      x: PAD + (x + 0.5) * P,
      y: PAD + (y + 0.5) * P,
    }));
  function rounded(input) {
    const v = input.filter(
        (p, i) =>
          !i ||
          i === input.length - 1 ||
          (p.x - input[i - 1].x) * (input[i + 1].y - p.y) !==
            (p.y - input[i - 1].y) * (input[i + 1].x - p.x),
      ),
      out = [{ ...v[0] }];
    let last = v[0];
    const line = (end) => {
      const from = last,
        n = Math.max(
          1,
          Math.ceil(Math.hypot(end.x - from.x, end.y - from.y) / 2),
        );
      for (let k = 1; k <= n; k++)
        out.push({
          x: from.x + ((end.x - from.x) * k) / n,
          y: from.y + ((end.y - from.y) * k) / n,
        });
      last = end;
    };
    for (let i = 1; i < v.length - 1; i++) {
      const a = v[i - 1],
        b = v[i],
        c = v[i + 1],
        l1 = Math.hypot(b.x - a.x, b.y - a.y),
        l2 = Math.hypot(c.x - b.x, c.y - b.y),
        r = Math.min(P * 0.48, l1 / 2, l2 / 2),
        enter = {
          x: b.x + ((a.x - b.x) * r) / l1,
          y: b.y + ((a.y - b.y) * r) / l1,
        },
        exit = {
          x: b.x + ((c.x - b.x) * r) / l2,
          y: b.y + ((c.y - b.y) * r) / l2,
        },
        center = { x: enter.x + exit.x - b.x, y: enter.y + exit.y - b.y };
      line(enter);
      const start = Math.atan2(enter.y - center.y, enter.x - center.x),
        end = Math.atan2(exit.y - center.y, exit.x - center.x),
        delta = Math.atan2(Math.sin(end - start), Math.cos(end - start)),
        n = Math.ceil((r * Math.abs(delta)) / 1.4);
      for (let k = 1; k <= n; k++) {
        const t = start + (delta * k) / n;
        out.push({
          x: center.x + r * Math.cos(t),
          y: center.y + r * Math.sin(t),
        });
      }
      last = exit;
    }
    if (v.length > 1) line(v[v.length - 1]);
    return out;
  }
  function path(points) {
    const p = new Path2D();
    if (points.length) {
      p.moveTo(points[0].x, points[0].y);
      for (let i = 1; i < points.length; i++)
        p.lineTo(points[i].x, points[i].y);
    }
    return p;
  }
  function head(c, p, d, col) {
    const r = W / 2;
    c.save();
    c.translate(p.x, p.y);
    c.rotate((d * Math.PI) / 2);
    const shape = new Path2D();
    shape.moveTo(-r * 0.93, r * 0.35);
    shape.quadraticCurveTo(-r * 1.12, -r * 0.35, -r * 0.67, -r * 0.88);
    shape.quadraticCurveTo(0, -r * 1.35, r * 0.67, -r * 0.88);
    shape.quadraticCurveTo(r * 1.12, -r * 0.35, r * 0.93, r * 0.35);
    shape.quadraticCurveTo(0, r * 0.74, -r * 0.93, r * 0.35);
    shape.closePath();
    const g = c.createLinearGradient(-r, -r, r, r);
    g.addColorStop(0, col[1]);
    g.addColorStop(0.42, col[0]);
    g.addColorStop(1, col[2]);
    c.fillStyle = g;
    c.strokeStyle = col[3];
    c.lineWidth = 1.25;
    c.fill(shape);
    c.stroke(shape);
    for (const x of [-r * 0.42, r * 0.42]) {
      c.beginPath();
      c.ellipse(x, -r * 0.12, r * 0.29, r * 0.36, 0, 0, TAU);
      c.fillStyle = "#fffbea";
      c.fill();
      c.strokeStyle = "rgba(70,53,33,.44)";
      c.lineWidth = 0.8;
      c.stroke();
      c.beginPath();
      c.ellipse(x, -r * 0.24, r * 0.132, r * 0.175, 0, 0, TAU);
      c.fillStyle = "#393e36";
      c.fill();
      c.beginPath();
      c.arc(x - r * 0.035, -r * 0.3, r * 0.045, 0, TAU);
      c.fillStyle = "white";
      c.fill();
    }
    c.restore();
  }
  function tube(c, points, col, d, shadow = true, showHead = true) {
    if (points.length < 2) return;
    const p = path(points);
    c.save();
    c.lineCap = "round";
    c.lineJoin = "round";
    if (shadow) {
      c.save();
      c.translate(0.65, 1.8);
      c.strokeStyle = "rgba(80,65,30,.16)";
      c.lineWidth = W + 1.4;
      c.shadowColor = "rgba(85,64,28,.15)";
      c.shadowBlur = 2.5;
      c.stroke(p);
      c.restore();
    }
    // A distance field gives bends and round caps the same continuous, top-left lighting.
    // Work in a small local bitmap; input and game geometry remain vector paths.
    const scale = 1.55,
      r = (W * scale) / 2,
      pad = r + 2,
      x = Math.floor(Math.min(...points.map((p) => p.x)) * scale - pad),
      y = Math.floor(Math.min(...points.map((p) => p.y)) * scale - pad),
      w = Math.ceil(Math.max(...points.map((p) => p.x)) * scale + pad - x),
      h = Math.ceil(Math.max(...points.map((p) => p.y)) * scale + pad - y),
      field = new Float32Array(w * h),
      nx = new Float32Array(w * h),
      ny = new Float32Array(w * h);
    field.fill(Infinity);
    for (let i = 0; i < points.length - 1; i++) {
      const a = points[i],
        b = points[i + 1],
        ax = a.x * scale - x,
        ay = a.y * scale - y,
        dx = (b.x - a.x) * scale,
        dy = (b.y - a.y) * scale,
        dd = dx * dx + dy * dy || 1,
        left = Math.max(0, Math.floor(Math.min(ax, ax + dx) - r - 1)),
        right = Math.min(w - 1, Math.ceil(Math.max(ax, ax + dx) + r + 1)),
        top = Math.max(0, Math.floor(Math.min(ay, ay + dy) - r - 1)),
        bottom = Math.min(h - 1, Math.ceil(Math.max(ay, ay + dy) + r + 1));
      for (let py = top; py <= bottom; py++)
        for (let px = left; px <= right; px++) {
          const t = Math.max(
              0,
              Math.min(1, ((px + 0.5 - ax) * dx + (py + 0.5 - ay) * dy) / dd),
            ),
            ox = px + 0.5 - ax - dx * t,
            oy = py + 0.5 - ay - dy * t,
            q = ox * ox + oy * oy,
            k = py * w + px;
          if (q < field[k]) {
            field[k] = q;
            nx[k] = ox / r;
            ny[k] = oy / r;
          }
        }
    }
    const image = document.createElement("canvas");
    image.width = w;
    image.height = h;
    const g = image.getContext("2d"),
      pixels = g.createImageData(w, h),
      rgba = pixels.data,
      rgb = col.map((s) => [
        parseInt(s.slice(1, 3), 16),
        parseInt(s.slice(3, 5), 16),
        parseInt(s.slice(5, 7), 16),
      ]);
    for (let k = 0; k < field.length; k++) {
      const q = field[k];
      if (q > (r + 0.7) * (r + 0.7)) continue;
      const dist = Math.sqrt(q),
        z = Math.sqrt(Math.max(0, 1 - q / (r * r))),
        light = Math.max(0, -nx[k] * 0.42 - ny[k] * 0.56 + z * 0.71),
        gloss =
          Math.pow(Math.max(0, -nx[k] * 0.22 - ny[k] * 0.37 + z * 0.9), 22) *
          0.4,
        edge = Math.max(0, Math.min(1, (dist - r + 1.35) / 1.2)),
        offset = k * 4;
      for (let j = 0; j < 3; j++) {
        const body = rgb[0][j] * (0.69 + 0.36 * light),
          shine = body + (255 - body) * gloss;
        rgba[offset + j] = shine * (1 - edge) + rgb[3][j] * edge;
      }
      rgba[offset + 3] = Math.min(1, Math.max(0, r + 0.6 - dist)) * 255;
    }
    g.putImageData(pixels, 0, 0);
    c.drawImage(image, x / scale, y / scale, w / scale, h / scale);
    if (showHead) head(c, points[points.length - 1], d, col);
    c.restore();
  }
  function raster(m) {
    const xs = m.points.map((p) => p.x),
      ys = m.points.map((p) => p.y),
      x = Math.min(...xs) - P,
      y = Math.min(...ys) - P,
      w = Math.max(...xs) - x + P,
      h = Math.max(...ys) - y + P,
      image = document.createElement("canvas"),
      s = 1.7;
    image.width = Math.ceil(w * s);
    image.height = Math.ceil(h * s);
    const c = image.getContext("2d");
    c.scale(s, s);
    c.translate(-x, -y);
    tube(c, m.points, m.col, m.a.d);
    return { image, x, y, w: image.width / s, h: image.height / s };
  }
  function buildModels() {
    models = new Map();
    for (const a of lv().arrows) {
      const m = {
        a,
        points: rounded(centers(a)),
        col: colors[(a.skin ?? a.id) % colors.length],
      };
      m.sprite = raster(m);
      models.set(a.id, m);
    }
  }
  function clampView() {
    view.zoom = Math.max(1, Math.min(2.8, view.zoom));
    const mx = (display.w * (view.zoom - 1)) / 2,
      my = (display.h * (view.zoom - 1)) / 2;
    view.x = Math.max(-mx, Math.min(mx, view.x));
    view.y = Math.max(-my, Math.min(my, view.y));
    $("zoomLabel").textContent =
      view.zoom > 1.01 ? tr("看全图", "Fit board") : tr("放大", "Zoom in");
    $("zoomButton")
      .querySelector("use")
      .setAttribute("href", view.zoom > 1.01 ? "#i-fit" : "#i-plus");
  }
  function resize() {
    const r = $("boardRegion").getBoundingClientRect(),
      s = Math.min(
        Math.max(1, r.width) / world.w,
        Math.max(1, r.height) / world.h,
      );
    display = {
      w: Math.round(world.w * s),
      h: Math.round(world.h * s),
      s,
      dpr: Math.min(devicePixelRatio || 1, 2.5),
    };
    $("canvasStage").style.width = display.w + "px";
    $("canvasStage").style.height = display.h + "px";
    cv.width = Math.max(1, Math.round(display.w * display.dpr));
    cv.height = Math.max(1, Math.round(display.h * display.dpr));
    clampView();
    paint();
  }
  function toScreen(p) {
    const r = cv.getBoundingClientRect();
    return {
      x:
        r.left +
        display.w / 2 +
        view.x +
        (p.x - world.w / 2) * display.s * view.zoom,
      y:
        r.top +
        display.h / 2 +
        view.y +
        (p.y - world.h / 2) * display.s * view.zoom,
    };
  }
  function toWorld(e) {
    const r = cv.getBoundingClientRect(),
      s = display.s * view.zoom;
    return {
      x: (e.clientX - r.left - display.w / 2 - view.x) / s + world.w / 2,
      y: (e.clientY - r.top - display.h / 2 - view.y) / s + world.h / 2,
    };
  }
  function highlight(id, color) {
    const m = models.get(id);
    if (!m) return;
    ctx.save();
    ctx.strokeStyle = color;
    ctx.lineWidth = W + 5;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.stroke(path(m.points));
    ctx.restore();
  }
  function ray(id, bad) {
    const m = models.get(id),
      points = C.exitRayCells(lv(), state, id) || [],
      last = points[points.length - 1],
      a = m.points[m.points.length - 1];
    let b = last
      ? { x: PAD + (last[0] + 0.5) * P, y: PAD + (last[1] + 0.5) * P }
      : { ...a };
    if (!bad) {
      b.x += DIR[m.a.d][0] * P * 0.8;
      b.y += DIR[m.a.d][1] * P * 0.8;
    }
    ctx.save();
    ctx.lineWidth = 2.2;
    ctx.strokeStyle = bad ? "#c78662" : "#7d9d60";
    ctx.setLineDash([3, 7]);
    ctx.beginPath();
    ctx.moveTo(a.x, a.y);
    ctx.lineTo(b.x, b.y);
    ctx.stroke();
    ctx.restore();
  }
  function cumulative(points) {
    const d = [0];
    for (let i = 1; i < points.length; i++)
      d.push(
        d[i - 1] +
          Math.hypot(
            points[i].x - points[i - 1].x,
            points[i].y - points[i - 1].y,
          ),
      );
    return d;
  }
  function sample(points, dist, s) {
    if (s <= 0) return points[0];
    let lo = 0,
      hi = dist.length - 1;
    if (s >= dist[hi]) return points[hi];
    while (hi - lo > 1) {
      const mid = (lo + hi) >> 1;
      if (dist[mid] < s) lo = mid;
      else hi = mid;
    }
    const k = (s - dist[lo]) / (dist[hi] - dist[lo] || 1);
    return {
      x: points[lo].x + (points[hi].x - points[lo].x) * k,
      y: points[lo].y + (points[hi].y - points[lo].y) * k,
    };
  }
  function exitMotion(id, now) {
    const m = models.get(id),
      points = m.points.map((p) => ({ ...p })),
      d = m.a.d,
      [dx, dy] = DIR[d],
      mask = C.playableSet(lv());
    let [x, y] = m.a.cells[m.a.cells.length - 1];
    while (mask.has(x + dx + "," + (y + dy))) {
      x += dx;
      y += dy;
    }
    const edge = {
        x: PAD + (x + 0.5 + dx * 0.5) * P,
        y: PAD + (y + 0.5 + dy * 0.5) * P,
      },
      last = points[points.length - 1],
      oldDist = cumulative(points),
      length = oldDist[oldDist.length - 1],
      leave = Math.hypot(edge.x - last.x, edge.y - last.y) + P * 1.5;
    points.push({ x: last.x + dx * leave, y: last.y + dy * leave });
    const dist = cumulative(points),
      total = dist[dist.length - 1];
    return {
      kind: "exit",
      id,
      start: now,
      duration: Math.min(620, 260 + total * 0.27),
      points,
      dist,
      length,
      total,
      exitDistance: length + Math.hypot(edge.x - last.x, edge.y - last.y),
      edge,
      d,
    };
  }
  function paint(now = performance.now()) {
    cancelAnimationFrame(raf);
    raf = 0;
    if (!state) return;
    ctx.setTransform(display.dpr, 0, 0, display.dpr, 0, 0);
    ctx.clearRect(0, 0, display.w, display.h);
    ctx.save();
    ctx.translate(display.w / 2 + view.x, display.h / 2 + view.y);
    ctx.scale(display.s * view.zoom, display.s * view.zoom);
    ctx.translate(-world.w / 2, -world.h / 2);
    const active = new Set(state.remaining);
    for (const [id, color, on] of [
      [hinted, "#aec76d", now < hintUntil],
      [selected, "#c2b583", true],
      [focusId, "#86aacb", true],
      [blocked, "#ce9f77", now < blockUntil],
    ])
      if (id !== null && on && active.has(id)) highlight(id, color);
    for (const id of state.remaining) {
      const m = models.get(id),
        s = m.sprite,
        a = animations.find((a) => a.kind === "blocked" && a.id === id);
      ctx.save();
      if (a) {
        const n =
          Math.sin(Math.min(1, (now - a.start) / a.duration) * Math.PI) *
          P *
          0.08;
        ctx.translate(DIR[m.a.d][0] * n, DIR[m.a.d][1] * n);
      }
      ctx.drawImage(s.image, s.x, s.y, s.w, s.h);
      ctx.restore();
    }
    for (const a of animations) {
      if (a.kind !== "exit") continue;
      const f = Math.max(0, Math.min(1, (now - a.start) / a.duration)),
        advance = a.total * f * f * (3 - 2 * f);
      if (advance >= a.exitDistance) continue;
      const end = Math.min(advance + a.length, a.exitDistance),
        points = [sample(a.points, a.dist, advance)];
      for (let k = 0; k < a.points.length; k++)
        if (a.dist[k] > advance && a.dist[k] < end) points.push(a.points[k]);
      points.push(sample(a.points, a.dist, end));
      ctx.save();
      ctx.globalAlpha = Math.min(1, (a.exitDistance - advance) / W);
      tube(
        ctx,
        points,
        models.get(a.id).col,
        a.d,
        true,
        advance + a.length < a.exitDistance,
      );
      ctx.restore();
    }
    if (hinted !== null && now < hintUntil && active.has(hinted))
      ray(hinted, false);
    if (blocked !== null && now < blockUntil && active.has(blocked))
      ray(blocked, true);
    ctx.restore();
    animations = animations.filter((a) => now - a.start < a.duration);
    if (
      animations.length ||
      (hinted !== null && now < hintUntil) ||
      (blocked !== null && now < blockUntil)
    )
      raf = requestAnimationFrame(paint);
  }
  function chrome() {
    $("levelTitle").textContent = title(lv());
    $("levelIndex").textContent =
      `${String(index + 1).padStart(2, "0")} / ${String(L.length).padStart(2, "0")}`;
    $("remainingCount").textContent = state.remaining.length;
    $("remainingLabel").textContent = tr("条待解", "to untangle");
    $("undoButton").disabled = !state.history.length;
    $("hintButton").disabled = !state.remaining.length;
    const progress = (1 - state.remaining.length / lv().arrows.length) * 100;
    $("progressFill").style.width = progress + "%";
    $("progressTrack").setAttribute(
      "aria-valuenow",
      String(Math.round(progress)),
    );
  }
  function keyboard() {
    const holder = $("keyboardLayer"),
      hadFocus = holder.contains(document.activeElement);
    holder.replaceChildren();
    for (const id of state.remaining) {
      const b = document.createElement("button");
      b.type = "button";
      b.dataset.snakeId = id;
      const a = models.get(id)?.a || lv().arrows.find((a) => a.id === id),
        number = lv().arrows.indexOf(a) + 1,
        dir = tr(
          ["上", "右", "下", "左"][a.d],
          ["up", "right", "down", "left"][a.d],
        );
      b.textContent = tr(
        `第${number}条小蛇，朝${dir}`,
        `Snake ${number}, facing ${dir}`,
      );
      b.onfocus = () => {
        focusId = id;
        paint();
      };
      b.onblur = () => {
        focusId = null;
        paint();
      };
      b.onclick = () => attempt(id);
      holder.appendChild(b);
    }
    if (hadFocus)
      holder.querySelector("button")?.focus({ preventScroll: true });
  }
  function cancel() {
    epoch++;
    clearTimeout(finishTimer);
    cancelAnimationFrame(raf);
    animations = [];
    selected = hinted = blocked = focusId = null;
    hintUntil = blockUntil = 0;
    clearTimeout(msgTimer);
  }
  function select(n, fresh = false) {
    if (state) save();
    cancel();
    index = Math.max(0, Math.min(L.length - 1, n));
    C.validateLevel(lv());
    world = {
      w: (lv().width || lv().size) * P + PAD * 2,
      h: (lv().height || lv().size) * P + PAD * 2,
    };
    state = C.newState(lv());
    mistakes = hints = baseTime = 0;
    started = performance.now();
    finished = null;
    view = { zoom: 1, x: 0, y: 0 };
    let restored = false;
    const old = runs[lv().id];
    if (!fresh && old) {
      try {
        C.validateState(lv(), old.state);
        state = old.state;
        mistakes = savedNumber(old.mistakes, true);
        hints = savedNumber(old.hints, true);
        baseTime = savedNumber(old.elapsed);
        restored = true;
      } catch {}
    }
    if (!state.remaining.length) {
      state = C.newState(lv());
      mistakes = hints = baseTime = 0;
      restored = false;
    }
    buildModels();
    keyboard();
    chrome();
    resize();
    message(
      restored
        ? tr(
            "已接上你刚才的进度。",
            "Your little tangle is right where you left it.",
          )
        : words.start,
    );
    save();
  }
  function attempt(id) {
    if (!state.remaining.includes(id) || $("gameDialog").open) return false;
    const obstacles = C.blockers(lv(), state, id);
    selected = hinted = focusId = null;
    const now = performance.now();
    if (obstacles.length) {
      mistakes++;
      blocked = id;
      blockUntil = now + 500;
      if (!reduce())
        animations.push({ kind: "blocked", id, start: now, duration: 170 });
      message(words.block, "blocked");
      sound("blocked");
      save();
      paint();
      return false;
    }
    const a = exitMotion(id, now);
    state = C.transition(lv(), state, { type: "remove", id });
    blocked = null;
    if (!reduce()) animations.push(a);
    message(words.released, "success");
    sound("release");
    chrome();
    keyboard();
    save();
    paint();
    if (!state.remaining.length) {
      finished = elapsed();
      const result = { elapsed: finished, hints, mistakes },
        old = completed[lv().id];
      if (
        !old ||
        hints < old.hints ||
        (hints === old.hints && finished < old.elapsed)
      )
        completed[lv().id] = result;
      save();
      const generation = epoch;
      finishTimer = setTimeout(
        () => {
          if (generation === epoch && !state.remaining.length) {
            sound("win");
            showWin();
          }
        },
        reduce() ? 0 : Math.min(450, a.duration),
      );
    }
    return true;
  }
  function undo() {
    if (!state.history.length) return;
    closeDialog();
    cancel();
    state = C.transition(lv(), state, { type: "undo" });
    if (finished !== null) {
      baseTime = finished;
      started = performance.now();
      finished = null;
    }
    chrome();
    keyboard();
    message(tr("已经退回上一步。", "Back where it belongs."));
    save();
    paint();
  }
  function retry() {
    closeDialog();
    select(index, true);
    message(tr("重新梳理，一点点解开。", "A fresh start."));
  }
  function hint() {
    const action = C.solve(lv(), state).actions?.[0];
    if (!action) return;
    hinted = action.id;
    hintUntil = performance.now() + 1800;
    hints++;
    message(words.hint);
    save();
    paint();
  }
  function soundChrome() {
    $("soundButton")
      .querySelector("use")
      .setAttribute("href", settings.sound ? "#i-sound" : "#i-muted");
    $("soundButton").setAttribute("aria-pressed", String(settings.sound));
    $("soundButton").setAttribute(
      "aria-label",
      settings.sound
        ? tr("关闭声音", "Turn sound off")
        : tr("打开声音", "Turn sound on"),
    );
  }
  function dialog(html) {
    previousFocus = document.activeElement;
    $("dialogContent").innerHTML = html;
    if (!$("gameDialog").open) $("gameDialog").showModal();
    $("gameShell").inert = true;
    if ($("dialogClose")) $("dialogClose").onclick = closeDialog;
    requestAnimationFrame(() =>
      ($("dialogContent").querySelector("button") || $("gameDialog")).focus(),
    );
  }
  function closeDialog() {
    if (!$("gameDialog").open) return;
    $("gameDialog").close();
    $("gameShell").inert = false;
    previousFocus?.focus?.({ preventScroll: true });
  }
  const header = (text) =>
    `<div class="dialog-top"><h2>${escape(text)}</h2><button type="button" class="close-button" id="dialogClose" aria-label="${words.close}">${icon("close")}</button></div>`;
  function collection() {
    dialog(
      `${header(words.collection)}<p class="dialog-intro">${tr("换个形状，再解开一团缤纷。", "A different shape. A new little tangle.")}</p><div class="collection-grid">${L.map((l, i) => `<button class="collection-item" data-level="${i}" aria-current="${i === index}"><canvas data-thumb="${i}" width="280" height="230" aria-hidden="true"></canvas><strong>${String(i + 1).padStart(2, "0")} · ${escape(title(l))}</strong><small>${completed[l.id] ? tr("已解开 · ", "Cleared · ") : ""}${tr(l.arrows.length + " 条交织长蛇", l.arrows.length + " winding paths")}</small></button>`).join("")}</div><div class="collection-footer"><span>${tr("绮彩长蛇", "Winding paths")}</span><a href="phase.html">${tr("相位挑战 ↗", "Phase challenges ↗")}</a></div>`,
    );
    $("dialogContent")
      .querySelectorAll("[data-level]")
      .forEach(
        (b) =>
          (b.onclick = () => {
            closeDialog();
            select(Number(b.dataset.level));
          }),
      );
    $("dialogContent")
      .querySelectorAll("[data-thumb]")
      .forEach((c) => {
        const l = L[Number(c.dataset.thumb)],
          g = c.getContext("2d"),
          w = (l.width || l.size) * P + PAD * 2,
          h = (l.height || l.size) * P + PAD * 2,
          s = Math.min(c.width / w, c.height / h);
        g.translate((c.width - w * s) / 2, (c.height - h * s) / 2);
        g.scale(s, s);
        for (const a of l.arrows)
          tube(
            g,
            rounded(centers(a)),
            colors[(a.skin ?? a.id) % 6],
            a.d,
            false,
          );
      });
  }
  function help() {
    dialog(
      `${header(tr("给它们一点空间。", "Give them a way out."))}<ol class="help-list"><li>${tr("点小蛇的头或身体。看眼睛朝向，判断它想从哪边离开。", "Tap a head or body. Its eyes show the direction it wants to go.")}</li><li>${tr("前方被别的小蛇挡住时，先清开路。点错不会扣生命。", "Clear the path ahead first. A blocked tap costs no lives.")}</li><li>${tr("可以提示、撤销或放大；双指缩放，放大后拖动查看。", "Hints, undo and zoom are always available. Pinch to zoom; drag to explore.")}</li><li>${tr("键盘：Tab 选择小蛇，Enter 或空格放行；Z 撤销，H 提示。", "Keyboard: Tab to a snake, Enter or Space to release; Z to undo, H for hints.")}</li></ol><label class="setting-row">${tr("轻触反馈", "Gentle haptics")}<input id="hapticSetting" type="checkbox" ${settings.haptics ? "checked" : ""}></label><label class="setting-row">${tr("减少动态效果", "Reduce motion")}<input id="motionSetting" type="checkbox" ${settings.reduce ? "checked" : ""}></label><button class="primary-button" id="helpDone">${tr("明白了", "Got it")}</button>`,
    );
    $("hapticSetting").onchange = (e) => {
      settings.haptics = e.target.checked;
      save();
    };
    $("motionSetting").onchange = (e) => {
      settings.reduce = e.target.checked;
      if (reduce()) {
        animations = [];
        paint();
      }
      save();
    };
    $("helpDone").onclick = closeDialog;
  }
  function showWin() {
    dialog(
      `<div class="win-icon">${icon("check")}</div><h2 class="win-title">${tr("都舒展开了。", "Room to breathe.")}</h2><p class="win-copy">${tr("每一条曲折，都找到了出口。", "Every winding path found its way.")}</p><div class="win-stats"><div><strong>${lv().arrows.length}</strong><span>${tr("已解开", "Released")}</span></div><div><strong>${time(finished)}</strong><span>${tr("用时", "Time")}</span></div><div><strong>${hints}</strong><span>${tr("提示", "Hints")}</span></div></div><button class="primary-button" id="nextPattern">${index < L.length - 1 ? tr("下一幅图案", "Next pattern") : tr("回到图案集", "The collection")}${icon("next")}</button><button class="secondary-button" id="playAgain">${tr("再解一次", "Play this one again")}</button>`,
    );
    $("nextPattern").onclick = () => {
      closeDialog();
      if (index < L.length - 1) select(index + 1);
      else collection();
    };
    $("playAgain").onclick = retry;
  }
  function distSegment(p, a, b) {
    const dx = b.x - a.x,
      dy = b.y - a.y,
      k = Math.max(
        0,
        Math.min(
          1,
          ((p.x - a.x) * dx + (p.y - a.y) * dy) / (dx * dx + dy * dy || 1),
        ),
      );
    return Math.hypot(p.x - a.x - k * dx, p.y - a.y - k * dy);
  }
  function pick(p) {
    let best = null,
      distance = Infinity;
    for (const id of state.remaining) {
      const m = models.get(id),
        h = m.points[m.points.length - 1];
      let d = Math.hypot(p.x - h.x, p.y - h.y) * 0.95;
      for (let i = 1; i < m.points.length; i += 3)
        d = Math.min(
          d,
          distSegment(
            p,
            m.points[i - 1],
            m.points[Math.min(i + 2, m.points.length - 1)],
          ),
        );
      if (d < distance) {
        distance = d;
        best = id;
      }
    }
    return distance <= W / 2 + P * 0.13 ? best : null;
  }
  const pointers = new Map();
  let gesture = null;
  function pinch() {
    const [a, b] = [...pointers.values()];
    return {
      d: Math.hypot(a.x - b.x, a.y - b.y),
      x: (a.x + b.x) / 2,
      y: (a.y + b.y) / 2,
    };
  }
  function pinchGesture() {
    const base = pinch(),
      r = cv.getBoundingClientRect();
    return {
      pinch: true,
      base,
      zoom: view.zoom,
      anchorX: (base.x - r.left - display.w / 2 - view.x) / view.zoom,
      anchorY: (base.y - r.top - display.h / 2 - view.y) / view.zoom,
      moved: true,
    };
  }
  cv.addEventListener("pointerdown", (e) => {
    if (e.button !== 0) return;
    e.preventDefault();
    cv.focus({ preventScroll: true });
    cv.setPointerCapture(e.pointerId);
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pointers.size === 1) {
      selected = pick(toWorld(e));
      gesture = {
        sx: e.clientX,
        sy: e.clientY,
        x: view.x,
        y: view.y,
        id: selected,
        moved: false,
        pinch: false,
      };
      paint();
    } else {
      selected = null;
      gesture = pinchGesture();
      $("boardTip").textContent = tr(
        "拖动查看 · 双指缩放",
        "Drag to explore · pinch to zoom",
      );
      $("boardTip").classList.add("visible");
      paint();
    }
  });
  cv.addEventListener("pointermove", (e) => {
    if (!pointers.has(e.pointerId)) return;
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pointers.size >= 2) {
      const n = pinch();
      if (!gesture?.pinch) gesture = pinchGesture();
      view.zoom = Math.max(
        1,
        Math.min(2.8, (gesture.zoom * n.d) / (gesture.base.d || 1)),
      );
      const r = cv.getBoundingClientRect();
      view.x = n.x - r.left - display.w / 2 - gesture.anchorX * view.zoom;
      view.y = n.y - r.top - display.h / 2 - gesture.anchorY * view.zoom;
      clampView();
      selected = null;
      paint();
      return;
    }
    if (!gesture || gesture.pinch) return;
    const dx = e.clientX - gesture.sx,
      dy = e.clientY - gesture.sy;
    if (Math.hypot(dx, dy) > 8) {
      gesture.moved = true;
      selected = null;
      if (view.zoom > 1) {
        view.x = gesture.x + dx;
        view.y = gesture.y + dy;
        clampView();
      }
      paint();
    }
  });
  function endPointer(e, cancelled) {
    if (!pointers.has(e.pointerId)) return;
    pointers.delete(e.pointerId);
    if (
      !cancelled &&
      gesture &&
      !gesture.pinch &&
      !gesture.moved &&
      gesture.id !== null &&
      !pointers.size
    )
      attempt(gesture.id);
    selected = null;
    if (!pointers.size) {
      gesture = null;
      $("boardTip").classList.remove("visible");
    }
    paint();
  }
  cv.addEventListener("pointerup", (e) => endPointer(e, false));
  cv.addEventListener("pointercancel", (e) => endPointer(e, true));
  cv.addEventListener("lostpointercapture", (e) => {
    if (pointers.has(e.pointerId)) endPointer(e, true);
  });
  // A browser may suppress its compatibility click immediately after a cancelled pan.
  // Activate touch buttons on release, then discard only that tap's duplicate native click.
  let touchButton = null,
    suppressedClick = null;
  document.addEventListener(
    "pointerdown",
    (e) => {
      if (e.pointerType !== "touch") return;
      suppressedClick = null;
      const button = e.target.closest("button");
      touchButton =
        button && !button.disabled
          ? { button, x: e.clientX, y: e.clientY, id: e.pointerId }
          : null;
    },
    true,
  );
  document.addEventListener(
    "pointercancel",
    () => {
      touchButton = null;
    },
    true,
  );
  document.addEventListener(
    "pointerup",
    (e) => {
      const tap = touchButton;
      if (!tap || tap.id !== e.pointerId) return;
      touchButton = null;
      if (
        e.target.closest("button") !== tap.button ||
        Math.hypot(e.clientX - tap.x, e.clientY - tap.y) > 8
      )
        return;
      e.preventDefault();
      suppressedClick = { button: tap.button, until: performance.now() + 700 };
      tap.button.click();
    },
    true,
  );
  document.addEventListener(
    "click",
    (e) => {
      if (
        e.isTrusted &&
        suppressedClick &&
        performance.now() < suppressedClick.until &&
        e.target.closest("button") === suppressedClick.button
      ) {
        e.preventDefault();
        e.stopImmediatePropagation();
        suppressedClick = null;
      }
    },
    true,
  );
  cv.addEventListener(
    "wheel",
    (e) => {
      if (!e.ctrlKey && view.zoom === 1) return;
      e.preventDefault();
      view.zoom *= Math.exp(-e.deltaY * 0.002);
      clampView();
      paint();
    },
    { passive: false },
  );
  cv.addEventListener("keydown", (e) => {
    if (!state.remaining.length) return;
    if (["ArrowRight", "ArrowDown", "ArrowLeft", "ArrowUp"].includes(e.key)) {
      e.preventDefault();
      const n = state.remaining.length,
        i = state.remaining.indexOf(focusId),
        d = e.key === "ArrowLeft" || e.key === "ArrowUp" ? -1 : 1;
      focusId = state.remaining[(i + d + n) % n];
      paint();
    } else if ((e.key === "Enter" || e.key === " ") && focusId !== null) {
      e.preventDefault();
      attempt(focusId);
    }
  });
  document.addEventListener("keydown", (e) => {
    if (
      e.defaultPrevented ||
      $("gameDialog").open ||
      e.target.matches("input,select,textarea")
    )
      return;
    if (e.key.toLowerCase() === "z") {
      e.preventDefault();
      undo();
    } else if (e.key.toLowerCase() === "h") {
      e.preventDefault();
      hint();
    }
  });
  $("gameDialog").addEventListener("cancel", (e) => {
    e.preventDefault();
    closeDialog();
  });
  $("gameDialog").addEventListener("close", () => {
    $("gameShell").inert = false;
  });
  $("gameDialog").addEventListener("click", (e) => {
    if (e.target === $("gameDialog")) {
      const r = $("gameDialog").getBoundingClientRect();
      if (
        e.clientX < r.left ||
        e.clientX > r.right ||
        e.clientY < r.top ||
        e.clientY > r.bottom
      )
        closeDialog();
    }
  });
  $("undoButton").onclick = undo;
  $("hintButton").onclick = hint;
  $("restartButton").onclick = retry;
  $("helpButton").onclick = help;
  $("collectionButton").onclick = collection;
  $("brandButton").onclick = (e) => {
    e.preventDefault();
    collection();
  };
  $("zoomButton").onclick = () => {
    view.zoom = view.zoom > 1.01 ? 1 : 1.65;
    view.x = view.y = 0;
    clampView();
    paint();
  };
  $("soundButton").onclick = () => {
    settings.sound = !settings.sound;
    soundChrome();
    save();
    if (settings.sound) sound("release");
  };
  for (const [id, zh, eng] of [
    ["undoLabel", "撤销", "Undo"],
    ["hintLabel", "给点提示", "A little hint"],
    ["restartLabel", "重新开始", "Start again"],
    ["helpLabel", "怎么玩", "How to play"],
  ])
    $(id).textContent = tr(zh, eng);
  $("collectionButton").setAttribute("aria-label", words.collection);
  if (en) {
    $("brandButton").setAttribute("aria-label", "Vector Shift collection");
    $("puzzleCanvas").setAttribute(
      "aria-label",
      "Winding paths. Select a snake with touch or arrow keys; Enter to release.",
    );
    $("progressTrack").setAttribute("aria-label", "Board progress");
    $("keyboardLayer").setAttribute("aria-label", "Available snakes");
    document
      .querySelector(".game-controls")
      .setAttribute("aria-label", "Game controls");
  }
  document.documentElement.lang = en ? "en" : "zh-CN";
  soundChrome();
  const params = new URLSearchParams(location.search),
    requested = Number(params.get("pattern")),
    initial =
      params.has("pattern") && Number.isInteger(requested)
        ? requested - 1
        : Number.isInteger(store.index)
          ? store.index
          : 0;
  select(initial, params.has("fresh"));
  new ResizeObserver(resize).observe($("boardRegion"));
  motion.addEventListener("change", () => {
    if (reduce()) animations = [];
    paint();
  });
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      baseTime = elapsed();
      paused = true;
      save();
    } else {
      started = performance.now();
      paused = false;
    }
  });
  window.addEventListener("pagehide", save);
  if (channel === "demo")
    window.VectorShiftDenseDebug = {
      levels: L,
      getLevel: lv,
      getState: () => JSON.parse(JSON.stringify(state)),
      getStats: () => ({ mistakes, hints, elapsed: elapsed(), finished }),
      setLevel: (n) => select(n - 1, true),
      getSolution: () => C.solve(lv(), state),
      tap: attempt,
      undo,
      retry,
      pointFor: (id) => {
        const m = models.get(id);
        return m ? toScreen(m.points[m.points.length - 1]) : null;
      },
      bodyPointFor: (id) => {
        const m = models.get(id);
        return m
          ? toScreen(m.points[Math.floor(m.points.length * 0.45)])
          : null;
      },
      getView: () => ({ ...view }),
      getDisplay: () => ({
        ...display,
        bodyWidthCss: W * display.s * view.zoom,
      }),
      getAnimation: () =>
        animations.map((a) => ({
          kind: a.kind,
          id: a.id,
          elapsed: performance.now() - a.start,
          duration: a.duration,
        })),
      setReduced: (v) => {
        settings.reduce = !!v;
        save();
        if (reduce()) animations = [];
        paint();
      },
      render: paint,
    };
  if (channel === "crazygames-basic") {
    let tries = 0;
    const poll = setInterval(async () => {
      if (window.CrazyGames?.SDK) {
        clearInterval(poll);
        try {
          await window.CrazyGames.SDK.init();
          window.CrazyGames.SDK.game.gameplayStart();
        } catch {}
      } else if (++tries > 40) clearInterval(poll);
    }, 150);
  }
})();
