/* ============================================================
   桥见 · 飞夺泸定桥 —— 二维降级地球仪（Canvas 2D）
   当浏览器不支持 WebGL 时自动启用，功能保持一致：
   拖拽旋转 / 滚轮缩放 / 悬停显示节点 / 自动缓慢自转。
   使用正射投影（orthographic）绘制，视觉上仍是三维球体效果。
   ============================================================ */

window.initGlobe2D = function (SITES) {
  const container = document.getElementById('globe');
  const tipEl = document.getElementById('tip');

  const cv = document.createElement('canvas');
  cv.style.width = '100%';
  cv.style.height = '100%';
  cv.style.display = 'block';
  cv.style.cursor = 'grab';
  container.appendChild(cv);
  const g = cv.getContext('2d');

  const W = () => container.clientWidth || 800;
  const H = () => container.clientHeight || 520;

  function resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    cv.width = W() * dpr;
    cv.height = H() * dpr;
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  window.addEventListener('resize', resize);
  new ResizeObserver(resize).observe(container);
  resize();

  /* ---------- 状态 ----------
     投影推导：z1 = sinp·sin(t−yaw)，x1 = −sinp·cos(t−yaw)；
     节点正对观察者需 t−yaw = π/2，即 yaw = t − π/2 */
  let yaw = (102.23 + 180) * Math.PI / 180 - Math.PI / 2;
  let pitch = 0.18;    // 俯仰
  let zoom = 1;
  let velY = 0.0012;
  let dragging = false, lastX = 0, lastY = 0;
  let hovered = null;

  const D2R = Math.PI / 180;

  /* ---------- 经纬度 -> 三维单位向量 ---------- */
  function dir(lon, lat) {
    const p = (90 - lat) * D2R;
    const t = (lon + 180) * D2R;
    return [
      -Math.sin(p) * Math.cos(t),
      Math.cos(p),
      Math.sin(p) * Math.sin(t),
    ];
  }

  /* ---------- 三维向量 -> 屏幕坐标（正射投影） ---------- */
  function project(v) {
    // 先按 pitch 绕 X 轴旋转，再按 yaw 绕 Y 轴旋转
    const cy = Math.cos(yaw), sy = Math.sin(yaw);
    const x1 = v[0] * cy - v[2] * sy;
    const z1 = v[0] * sy + v[2] * cy;
    const cp = Math.cos(pitch), sp = Math.sin(pitch);
    const y2 = v[1] * cp - z1 * sp;
    const z2 = v[1] * sp + z1 * cp;

    const cx = W() / 2;
    const cyy = H() / 2;
    const R = Math.min(W(), H()) * 0.38 * zoom;
    return {
      x: cx + x1 * R,
      y: cyy - y2 * R,
      z: z2,
      visible: z2 > -0.02,
      r: R,
    };
  }

  /* ---------- 示意性大陆轮廓 ---------- */
  const LAND = [
    [[-10,36],[0,44],[10,45],[20,42],[28,41],[36,36],[44,38],[52,40],[60,45],
     [70,42],[80,30],[88,22],[95,20],[102,10],[108,20],[115,23],[122,30],
     [130,34],[140,38],[145,44],[155,52],[165,60],[175,65],[180,68],
     [170,72],[150,75],[130,74],[110,76],[90,76],[70,72],[50,70],[30,70],
     [20,68],[10,60],[5,58],[0,52],[-5,48],[-10,36]],
    [[-17,15],[-10,5],[5,4],[12,4],[20,0],[28,-5],[32,-12],[35,-20],
     [32,-28],[25,-34],[18,-34],[12,-28],[8,-18],[5,-5],[0,5],[-8,8],[-17,15]],
    [[-168,66],[-150,70],[-130,70],[-110,68],[-95,70],[-80,68],[-65,60],
     [-58,48],[-70,42],[-80,32],[-90,30],[-100,20],[-110,22],[-118,30],
     [-125,40],[-130,50],[-140,58],[-155,60],[-168,66]],
    [[-80,8],[-70,10],[-60,8],[-50,0],[-42,-8],[-38,-15],[-45,-23],
     [-55,-28],[-62,-35],[-68,-45],[-73,-52],[-75,-45],[-70,-32],
     [-70,-20],[-78,-8],[-80,8]],
    [[113,-22],[122,-18],[130,-12],[140,-12],[147,-18],[152,-26],
     [148,-36],[140,-38],[130,-34],[120,-34],[113,-22]],
    [[-45,60],[-30,68],[-22,76],[-30,82],[-50,82],[-60,76],[-55,66],[-45,60]],
    [[-180,-72],[-120,-78],[-60,-76],[0,-74],[60,-76],[120,-74],[180,-72],
     [180,-90],[-180,-90],[-180,-72]],
  ];

  const SITE_VECS = SITES.map(s => ({ ...s, v: dir(s.lon, s.lat) }));

  /* ---------- 绘制 ---------- */
  function draw() {
    const w = W(), h = H();
    g.clearRect(0, 0, w, h);

    const cx = w / 2, cyy = h / 2;
    const R = Math.min(w, h) * 0.38 * zoom;

    // 外层光晕
    const halo = g.createRadialGradient(cx, cyy, R * 0.92, cx, cyy, R * 1.22);
    halo.addColorStop(0, 'rgba(201,67,47,0.30)');
    halo.addColorStop(1, 'rgba(201,67,47,0)');
    g.fillStyle = halo;
    g.beginPath(); g.arc(cx, cyy, R * 1.22, 0, Math.PI * 2); g.fill();

    // 海洋球体
    const ocean = g.createRadialGradient(
      cx - R * 0.35, cyy - R * 0.4, R * 0.15, cx, cyy, R);
    ocean.addColorStop(0, '#2b4760');
    ocean.addColorStop(0.55, '#1d3142');
    ocean.addColorStop(1, '#101c27');
    g.save();
    g.beginPath(); g.arc(cx, cyy, R, 0, Math.PI * 2); g.clip();
    g.fillStyle = ocean; g.fillRect(cx - R, cyy - R, R * 2, R * 2);

    // 经纬网
    g.strokeStyle = 'rgba(200,150,70,0.16)';
    g.lineWidth = 1;
    for (let lon = -180; lon < 180; lon += 20) {
      g.beginPath();
      let started = false;
      for (let lat = -90; lat <= 90; lat += 3) {
        const p = project(dir(lon, lat));
        if (!p.visible) { started = false; continue; }
        started ? g.lineTo(p.x, p.y) : g.moveTo(p.x, p.y);
        started = true;
      }
      g.stroke();
    }
    for (let lat = -60; lat <= 60; lat += 20) {
      g.beginPath();
      let started = false;
      for (let lon = -180; lon <= 180; lon += 4) {
        const p = project(dir(lon, lat));
        if (!p.visible) { started = false; continue; }
        started ? g.lineTo(p.x, p.y) : g.moveTo(p.x, p.y);
        started = true;
      }
      g.stroke();
    }

    // 大陆（背面先画暗色，正面画亮色）
    LAND.forEach(poly => {
      const pts = poly.map(([lo, la]) => project(dir(lo, la)));
      const anyVisible = pts.some(p => p.visible);
      if (!anyVisible) return;
      g.beginPath();
      pts.forEach((p, i) => i ? g.lineTo(p.x, p.y) : g.moveTo(p.x, p.y));
      g.closePath();
      g.fillStyle = 'rgba(84,76,65,0.92)';
      g.fill();
      g.strokeStyle = 'rgba(139,128,112,0.65)';
      g.lineWidth = 1.2;
      g.stroke();
    });

    // 球体明暗（立体感）
    const shade = g.createRadialGradient(
      cx - R * 0.4, cyy - R * 0.45, R * 0.1, cx, cyy, R * 1.05);
    shade.addColorStop(0, 'rgba(255,245,225,0.10)');
    shade.addColorStop(0.6, 'rgba(0,0,0,0)');
    shade.addColorStop(1, 'rgba(0,0,0,0.55)');
    g.fillStyle = shade;
    g.fillRect(cx - R, cyy - R, R * 2, R * 2);
    g.restore();

    // 球体边缘细线
    g.strokeStyle = 'rgba(232,180,95,0.35)';
    g.lineWidth = 1.5;
    g.beginPath(); g.arc(cx, cyy, R, 0, Math.PI * 2); g.stroke();

    // 路线连线
    g.strokeStyle = 'rgba(232,180,95,0.55)';
    g.lineWidth = 1.4;
    for (let i = 0; i < SITE_VECS.length - 1; i++) {
      const a = project(SITE_VECS[i].v);
      const b = project(SITE_VECS[i + 1].v);
      if (!a.visible && !b.visible) continue;
      g.beginPath();
      g.moveTo(a.x, a.y);
      const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
      g.quadraticCurveTo(mx, my - R * 0.12, b.x, b.y);
      g.stroke();
    }

    // 节点
    SITE_VECS.forEach(s => {
      const p = project(s.v);
      if (!p.visible) return;
      const big = s.role === 'focus' || s.role === 'key';
      const color = s.role === 'focus' ? '#ffd98a'
        : s.role === 'key' ? '#c9432f'
        : (s.role === 'start' || s.role === 'end') ? '#9db8a8' : '#e8b45f';
      const rad = big ? 5 : 3.2;
      const isHover = hovered === s.name;
      const pulse = big ? 1 + Math.sin(Date.now() / 420) * 0.35 : 1;

      // 光晕
      g.beginPath();
      g.arc(p.x, p.y, rad * (isHover ? 3.4 : 2.6) * pulse, 0, Math.PI * 2);
      g.fillStyle = hexA(color, isHover ? 0.34 : 0.2);
      g.fill();

      g.beginPath();
      g.arc(p.x, p.y, rad, 0, Math.PI * 2);
      g.fillStyle = color;
      g.fill();
      g.strokeStyle = 'rgba(253,246,236,0.85)';
      g.lineWidth = 1.2;
      g.stroke();

      if (big) {
        g.font = '600 12px "PingFang SC","Microsoft YaHei",sans-serif';
        g.fillStyle = isHover ? '#fff' : 'rgba(240,228,208,0.92)';
        g.textAlign = 'center';
        g.fillText(s.name, p.x, p.y - rad - 8);
      }
    });
  }

  function hexA(hex, a) {
    const n = parseInt(hex.slice(1), 16);
    return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
  }

  /* ---------- 交互 ---------- */
  const onDown = e => {
    dragging = true;
    const p = e.touches ? e.touches[0] : e;
    lastX = p.clientX; lastY = p.clientY;
    cv.style.cursor = 'grabbing';
  };
  const onMove = e => {
    const p = e.touches ? e.touches[0] : e;
    if (dragging) {
      yaw -= (p.clientX - lastX) * 0.008;
      pitch = Math.max(-0.9, Math.min(0.9, pitch + (p.clientY - lastY) * 0.006));
      lastX = p.clientX; lastY = p.clientY;
    } else {
      // 悬停检测
      const rect = cv.getBoundingClientRect();
      const mx = p.clientX - rect.left;
      const my = p.clientY - rect.top;
      let found = null;
      SITE_VECS.forEach(s => {
        const pr = project(s.v);
        if (!pr.visible) return;
        const dx = pr.x - mx, dy = pr.y - my;
        if (dx * dx + dy * dy < 220) found = s.name;
      });
      hovered = found;
      if (hovered) {
        const s = SITE_VECS.find(x => x.name === hovered);
        tipEl.innerHTML = `<b>${s.name}</b><i>${s.year}</i>`;
        tipEl.classList.add('on');
        cv.style.cursor = 'pointer';
      } else {
        tipEl.classList.remove('on');
        cv.style.cursor = dragging ? 'grabbing' : 'grab';
      }
    }
  };
  const onUp = () => { dragging = false; cv.style.cursor = 'grab'; };
  const onWheel = e => {
    e.preventDefault();
    zoom = Math.max(0.65, Math.min(1.9, zoom - e.deltaY * 0.0012));
  };

  cv.addEventListener('mousedown', onDown);
  window.addEventListener('mousemove', onMove);
  window.addEventListener('mouseup', onUp);
  cv.addEventListener('touchstart', onDown, { passive: true });
  cv.addEventListener('touchmove', onMove, { passive: true });
  cv.addEventListener('touchend', onUp);
  cv.addEventListener('wheel', onWheel, { passive: false });

  /* ---------- 循环 ---------- */
  function loop() {
    if (!dragging) yaw -= velY;
    draw();
    requestAnimationFrame(loop);
  }
  loop();
};
