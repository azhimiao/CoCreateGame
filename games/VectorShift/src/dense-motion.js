/* Shared path, timing and reservations for the Canvas view and deterministic QA.
 * Every launch reserves its original body plus its complete forward exit ray.
 * Reservations last until the tail has left. Unrelated snakes can move together.
 */
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.VectorShiftDenseMotion = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";
  const DIR = [
    [0, -1],
    [1, 0],
    [0, 1],
    [-1, 0],
  ];
  function cumulative(points) {
    const out = [0];
    for (let i = 1; i < points.length; i++)
      out.push(
        out[i - 1] +
          Math.hypot(
            points[i].x - points[i - 1].x,
            points[i].y - points[i - 1].y,
          ),
      );
    return out;
  }
  function sample(points, dist, s) {
    if (s <= 0) return { ...points[0] };
    let lo = 0,
      hi = dist.length - 1;
    if (s >= dist[hi]) return { ...points[hi] };
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
  function travelCells(level, a) {
    const cells = a.cells.map((c) => c.slice()),
      [dx, dy] = DIR[a.d];
    let [x, y] = a.cells.at(-1);
    while (true) {
      x += dx;
      y += dy;
      if (
        x < 0 ||
        y < 0 ||
        x >= (level.width || level.size) ||
        y >= (level.height || level.size)
      )
        break;
      cells.push([x, y]);
    }
    return cells;
  }
  function conflicts(level, id, flights) {
    const a = level.arrows.find((a) => a.id === id);
    if (!a) return [];
    const path = new Set(travelCells(level, a).map((c) => c.join(",")));
    return flights
      .filter(
        (f) =>
          f.kind === "exit" &&
          f.id !== id &&
          travelCells(
            level,
            level.arrows.find((a) => a.id === f.id),
          ).some((c) => path.has(c.join(","))),
      )
      .map((f) => f.id);
  }
  // Integrate a short smooth acceleration and finish at cruising speed off-canvas.
  // Long snakes keep a comparable speed instead of squeezing every path into 620ms.
  function advance(plan, elapsed) {
    if (elapsed <= 0) return 0;
    if (elapsed >= plan.duration) return plan.distance;
    const t = elapsed / 1000,
      r = plan.ramp / 1000;
    if (t < r) {
      const u = t / r;
      return plan.speed * r * (u * u * u - 0.5 * u * u * u * u);
    }
    return Math.min(plan.distance, plan.speed * (t - r * 0.5));
  }
  function plan(level, a, points, now, pitch, padding, bodyWidth) {
    const [dx, dy] = DIR[a.d],
      last = points.at(-1),
      width = (level.width || level.size) * pitch + padding * 2,
      height = (level.height || level.size) * pitch + padding * 2;
    const edgeDistance =
        dx === 1
          ? width - last.x
          : dx === -1
            ? last.x
            : dy === 1
              ? height - last.y
              : last.y,
      margin = bodyWidth * 0.75 + 4,
      route = points.map((p) => ({ ...p })),
      bodyDistances = cumulative(route),
      length = bodyDistances.at(-1),
      extension = edgeDistance + margin;
    route.push({ x: last.x + dx * extension, y: last.y + dy * extension });
    const dist = cumulative(route),
      distance = length + extension,
      speed = pitch * 25,
      ramp = 110;
    return {
      kind: "exit",
      id: a.id,
      d: a.d,
      start: now,
      points: route,
      dist,
      length,
      distance,
      speed,
      ramp,
      duration: (distance / speed) * 1000 + ramp * 0.5,
    };
  }
  function frame(plan, elapsed) {
    const start = advance(plan, elapsed);
    if (start >= plan.distance)
      return { done: true, points: [], advance: start };
    const end = Math.min(start + plan.length, plan.distance),
      points = [sample(plan.points, plan.dist, start)];
    for (let i = 0; i < plan.points.length; i++)
      if (plan.dist[i] > start && plan.dist[i] < end)
        points.push(plan.points[i]);
    points.push(sample(plan.points, plan.dist, end));
    return {
      done: false,
      points,
      advance: start,
      head: points.at(-1),
      tail: points[0],
    };
  }
  return Object.freeze({
    cumulative,
    sample,
    travelCells,
    conflicts,
    plan,
    advance,
    frame,
  });
});
