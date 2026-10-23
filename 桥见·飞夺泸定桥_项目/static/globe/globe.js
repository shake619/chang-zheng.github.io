/* ============================================================
   桥见 · 飞夺泸定桥 —— 3D 交互地球仪（three.js / WebGL）
   ------------------------------------------------------------
   设计要点：
   1. 地球纹理由 Canvas 程序化绘制（示意性世界地图，非卫星影像），
      不使用任何来源不明的地图素材，不用于地理测量。
   2. 长征节点坐标仅表达相对位置关系，弧线为「示意连线」，
      不代表已核验的精确行军路线。
   3. 交互：拖拽旋转 / 滚轮缩放 / 悬停显示节点信息 / 点击节点查看详情。
   4. 兼容：若浏览器不支持 WebGL（老旧显卡、远程桌面等），
      自动降级为 Canvas 2D 版本（globe2d.js），并在界面提示。
   5. 依赖：../vendor/three.module.min.js（本地文件，离线可用）。
   ============================================================ */

const SITES = [
  { name: '瑞金',   lon: 116.03, lat: 25.89, year: '1934.10',     role: 'start' },
  { name: '湘江',   lon: 111.05, lat: 25.62, year: '1934.12' },
  { name: '通道',   lon: 109.78, lat: 26.16, year: '1934.12' },
  { name: '黎平',   lon: 109.14, lat: 26.23, year: '1934.12' },
  { name: '遵义',   lon: 106.93, lat: 27.73, year: '1935.01',     role: 'key' },
  { name: '赤水',   lon: 105.80, lat: 28.42, year: '1935.02' },
  { name: '金沙江', lon: 102.30, lat: 26.60, year: '1935.05' },
  { name: '安顺场', lon: 102.29, lat: 29.35, year: '1935.05.25' },
  { name: '泸定桥', lon: 102.23, lat: 29.90, year: '1935.05.29',  role: 'focus' },
  { name: '夹金山', lon: 102.75, lat: 30.85, year: '1935.06' },
  { name: '毛儿盖', lon: 103.20, lat: 32.65, year: '1935.08' },
  { name: '腊子口', lon: 103.65, lat: 34.15, year: '1935.09' },
  { name: '吴起镇', lon: 108.18, lat: 36.93, year: '1935.10',     role: 'end' },
];

const container = document.getElementById('globe');
const tipEl = document.getElementById('tip');

/* ---------- WebGL 可用性检测，失败则降级 ---------- */
function hasWebGL() {
  try {
    const c = document.createElement('canvas');
    return !!(window.WebGLRenderingContext &&
      (c.getContext('webgl2') || c.getContext('webgl') ||
       c.getContext('experimental-webgl')));
  } catch (e) { return false; }
}

function fallback(reason) {
  // globe2d.js 已作为经典脚本内联在页面中，直接调用
  if (window.initGlobe2D) {
    window.initGlobe2D(SITES);
  } else {
    container.innerHTML =
      '<div class="g-fail">当前浏览器未能加载地球仪组件，' +
      '请改用 Chrome / Edge 最新版本打开本页。</div>';
  }

  const note = document.getElementById('gl');
  if (note) note.textContent = '当前设备未启用三维加速，已切换为二维示意版本（功能相同）。';
}

if (!hasWebGL()) {
  fallback('no-webgl');
} else {
  main().catch(err => {
    console.warn('三维渲染初始化失败，切换二维版本：', err);
    fallback(String(err && err.message || err));
  });
}

/* ============================ 主程序 ============================ */
async function main() {
  const THREE = await import('../vendor/three.module.min.js');

  const R = 1;
  const scene = new THREE.Scene();

  const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
  camera.position.set(0, 0, 4);
  camera.lookAt(0, 0, 0);

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true
    });
  } catch (e) {
    throw new Error('WebGL 上下文创建失败');
  }

  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.domElement.style.display = 'block';
  renderer.domElement.style.width = '100%';
  renderer.domElement.style.height = '100%';

  container.appendChild(renderer.domElement);
  /* ---------- 程序化地球纹理 ---------- */
  function makeEarthTexture() {
    const W = 2048, H = 1024;
    const cv = document.createElement('canvas');
    cv.width = W; cv.height = H;
    const g = cv.getContext('2d');

    const sea = g.createLinearGradient(0, 0, 0, H);
    sea.addColorStop(0.0, '#16222e');
    sea.addColorStop(0.5, '#1d3142');
    sea.addColorStop(1.0, '#16222e');
    g.fillStyle = sea;
    g.fillRect(0, 0, W, H);

    // 示意性大陆轮廓（简化多边形，非精确地理数据）
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
    const project = (lon, lat) => [(lon + 180) / 360 * W, (90 - lat) / 180 * H];

    LAND.forEach(poly => {
      g.beginPath();
      poly.forEach(([lon, lat], i) => {
        const [x, y] = project(lon, lat);
        i === 0 ? g.moveTo(x, y) : g.lineTo(x, y);
      });
      g.closePath();
      g.fillStyle = '#544c41';
      g.fill();
      g.strokeStyle = '#8b8070';
      g.lineWidth = 2;
      g.stroke();
    });

    g.strokeStyle = 'rgba(200,150,70,0.18)';
    g.lineWidth = 1.2;
    for (let lon = -180; lon <= 180; lon += 15) {
      const x = (lon + 180) / 360 * W;
      g.beginPath(); g.moveTo(x, 0); g.lineTo(x, H); g.stroke();
    }
    for (let lat = -75; lat <= 75; lat += 15) {
      const y = (90 - lat) / 180 * H;
      g.beginPath(); g.moveTo(0, y); g.lineTo(W, y); g.stroke();
    }
    g.strokeStyle = 'rgba(200,150,70,0.35)';
    g.lineWidth = 2.5;
    g.beginPath(); g.moveTo(0, H / 2); g.lineTo(W, H / 2); g.stroke();

    const tex = new THREE.CanvasTexture(cv);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = 8;
    return tex;
  }

  /* ---------- 地球本体 ---------- */
  const earth = new THREE.Mesh(
    new THREE.SphereGeometry(R, 96, 96),
    new THREE.MeshStandardMaterial({
      map: makeEarthTexture(), roughness: 0.92, metalness: 0.04,
    })
  );
  scene.add(earth);

  /* ---------- 大气光晕 ---------- */
  const glow = new THREE.Mesh(
    new THREE.SphereGeometry(R * 1.14, 64, 64),
    new THREE.ShaderMaterial({
      transparent: true, side: THREE.BackSide,
      uniforms: { uColor: { value: new THREE.Color('#c9432f') } },
      vertexShader: `varying vec3 vN;
        void main(){ vN = normalize(normalMatrix * normal);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
      fragmentShader: `varying vec3 vN; uniform vec3 uColor;
        void main(){ float i = pow(0.60 - dot(vN, vec3(0.0,0.0,1.0)), 3.0);
        gl_FragColor = vec4(uColor, 1.0) * i; }`,
    })
  );
  scene.add(glow);

  /* ---------- 光照 ---------- */
  scene.add(new THREE.AmbientLight(0xfff3e0, 0.8));
  const key = new THREE.DirectionalLight(0xffe9c9, 1.3);
  key.position.set(3.2, 2.2, 3.5);
  scene.add(key);
  const rim = new THREE.DirectionalLight(0x8c1c13, 0.6);
  rim.position.set(-3, -1, -2);
  scene.add(rim);

  /* ---------- 工具函数 ---------- */
  const toVec3 = (lon, lat, radius = R) => {
    const phi = (90 - lat) * Math.PI / 180;
    const theta = (lon + 180) * Math.PI / 180;
    return new THREE.Vector3(
      -radius * Math.sin(phi) * Math.cos(theta),
      radius * Math.cos(phi),
      radius * Math.sin(phi) * Math.sin(theta)
    );
  };

  /* ---------- 路线弧线 ---------- */
  const arcs = new THREE.Group();
  scene.add(arcs);
  const arcMat = new THREE.LineBasicMaterial({
    color: 0xe8b45f, transparent: true, opacity: 0.7,
  });
  for (let i = 0; i < SITES.length - 1; i++) {
    const p1 = toVec3(SITES[i].lon, SITES[i].lat);
    const p2 = toVec3(SITES[i + 1].lon, SITES[i + 1].lat);
    const mid = p1.clone().add(p2).multiplyScalar(0.5);
    mid.normalize().multiplyScalar(R + 0.2 + p1.distanceTo(p2) * 0.22);
    const curve = new THREE.QuadraticBezierCurve3(p1, mid, p2);
    const geo = new THREE.BufferGeometry().setFromPoints(curve.getPoints(64));
    arcs.add(new THREE.Line(geo, arcMat));
  }

  /* ---------- 节点标记 ---------- */
  const markerGroup = new THREE.Group();
  scene.add(markerGroup);
  const markers = [];
  const COLOR = { normal: 0xe8b45f, key: 0xc9432f, focus: 0xffd98a, start: 0x9db8a8, end: 0x9db8a8 };

  SITES.forEach(site => {
    const pos = toVec3(site.lon, site.lat, R + 0.006);
    const big = site.role === 'focus' || site.role === 'key';
    const color = COLOR[site.role || 'normal'];

    const dot = new THREE.Mesh(
      new THREE.SphereGeometry(big ? 0.021 : 0.013, 16, 16),
      new THREE.MeshBasicMaterial({ color })
    );
    dot.position.copy(pos);

    const ring = new THREE.Mesh(
      new THREE.RingGeometry(big ? 0.030 : 0.020, big ? 0.042 : 0.028, 32),
      new THREE.MeshBasicMaterial({
        color, transparent: true, opacity: 0.5, side: THREE.DoubleSide,
      })
    );
    ring.position.copy(pos);
    ring.lookAt(0, 0, 0);

    dot.userData = { site, ring };
    markerGroup.add(dot, ring);
    markers.push(dot);

    if (big) {
      const pulse = new THREE.Mesh(
        new THREE.SphereGeometry(0.038, 16, 16),
        new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.18 })
      );
      pulse.position.copy(pos);
      pulse.userData = { isPulse: true };
      markerGroup.add(pulse);
    }
  });

  /* ---------- 星点背景 ---------- */
  const starGeo = new THREE.BufferGeometry();
  const sp = new Float32Array(900 * 3);
  for (let i = 0; i < 900; i++) {
    const r = 6 + Math.random() * 6;
    const t = Math.random() * Math.PI * 2;
    const p = Math.acos(2 * Math.random() - 1);
    sp[i * 3] = r * Math.sin(p) * Math.cos(t);
    sp[i * 3 + 1] = r * Math.cos(p);
    sp[i * 3 + 2] = r * Math.sin(p) * Math.sin(t);
  }
  starGeo.setAttribute('position', new THREE.BufferAttribute(sp, 3));
  scene.add(new THREE.Points(starGeo, new THREE.PointsMaterial({
    color: 0xe9d7b6, size: 0.032, transparent: true, opacity: 0.5,
  })));

  /* ---------- 交互状态 ---------- */
  let dragging = false, lastX = 0, lastY = 0;
  let velY = 0.0015, velX = 0, camDist = 3.05;
  let hovered = null;
  const ray = new THREE.Raycaster();
  const mouse = new THREE.Vector2(-10, -10);

  const el = renderer.domElement;
  el.style.cursor = 'grab';

  const onDown = e => {
    dragging = true;
    const p = e.touches ? e.touches[0] : e;
    lastX = p.clientX; lastY = p.clientY;
    el.style.cursor = 'grabbing';
  };
  const onMove = e => {
    const p = e.touches ? e.touches[0] : e;
    const rect = el.getBoundingClientRect();
    mouse.x = ((p.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((p.clientY - rect.top) / rect.height) * 2 + 1;
    if (dragging) {
      velY = (p.clientX - lastX) * 0.004;
      velX = (p.clientY - lastY) * 0.003;
      lastX = p.clientX; lastY = p.clientY;
    }
  };
  const onUp = () => { dragging = false; el.style.cursor = 'grab'; };
  const onWheel = e => {
    e.preventDefault();
    camDist = Math.min(5.0, Math.max(1.8, camDist + e.deltaY * 0.0015));
  };

  el.addEventListener('mousedown', onDown);
  window.addEventListener('mousemove', onMove);
  window.addEventListener('mouseup', onUp);
  el.addEventListener('touchstart', onDown, { passive: true });
  el.addEventListener('touchmove', onMove, { passive: true });
  el.addEventListener('touchend', onUp);
  el.addEventListener('wheel', onWheel, { passive: false });

  /* 点击节点：向父页面发送消息（Streamlit 侧可扩展联动） */
  el.addEventListener('click', () => {
    if (hovered) {
      const s = hovered.userData.site;
      tipEl.innerHTML = `<b>${s.name}</b><i>${s.year}</i>`;
      tipEl.classList.add('on');
    }
  });

  /* ---------- 尺寸自适应 ---------- */
  // const resize = () => {
  //   const w = container.clientWidth || 800;
  //   const h = container.clientHeight || 520;
  //   renderer.setSize(w, h, false);
  //   camera.aspect = w / h;
  //   camera.updateProjectionMatrix();
  // };
  // window.addEventListener('resize', resize);
  // new ResizeObserver(resize).observe(container);
  // resize();

  function resize() {
  const width = container.clientWidth;
  const height = container.clientHeight;

  if (width <= 0 || height <= 0) return;

  renderer.setSize(width, height, false);

  camera.aspect = width / height;
  camera.updateProjectionMatrix();

  renderer.render(scene, camera);
}

window.addEventListener('resize', resize);
new ResizeObserver(resize).observe(container);
resize();

  /* ---------- 初始视角对准泸定桥 ----------
     推导：three.js 绕 Y 轴旋转 ry 后，点 (x,z) 满足 x·cos(ry)+z·sin(ry)=0
     时位于正对相机的经线上，解得 ry = π/2 − (lon+180)° */
  (function aim() {
    const s = SITES.find(x => x.role === 'focus');
    const ry = Math.PI / 2 - (s.lon + 180) * Math.PI / 180;
    earth.rotation.y = ry;
    markerGroup.rotation.copy(earth.rotation);
    arcs.rotation.copy(earth.rotation);
  })();

  /* ---------- 动画循环 ---------- */
  const clock = new THREE.Clock();
  function animate() {
    requestAnimationFrame(animate);
    const t = clock.getElapsedTime();

    if (!dragging) {
      velY += (0.0015 - velY) * 0.02;
      velX *= 0.94;
    }
    earth.rotation.y += velY;
    earth.rotation.x = Math.max(-0.55, Math.min(0.55, earth.rotation.x + velX * 0.35));
    markerGroup.rotation.copy(earth.rotation);
    arcs.rotation.copy(earth.rotation);

    camera.position.z += (camDist - camera.position.z) * 0.09;

    markerGroup.children.forEach(o => {
      if (o.userData.isPulse) {
        o.scale.setScalar(1 + Math.sin(t * 2.2) * 0.3);
        o.material.opacity = 0.2 - Math.sin(t * 2.2) * 0.08;
      }
    });

    ray.setFromCamera(mouse, camera);
    const hits = ray.intersectObjects(markers, false);
    const hit = hits.length ? hits[0].object : null;
    if (hit !== hovered) {
      if (hovered) hovered.userData.ring.material.opacity = 0.5;
      hovered = hit;
      if (hovered) {
        const s = hovered.userData.site;
        tipEl.innerHTML = `<b>${s.name}</b><i>${s.year}</i>`;
        tipEl.classList.add('on');
        el.style.cursor = 'pointer';
      } else {
        tipEl.classList.remove('on');
        el.style.cursor = 'grab';
      }
    }
    if (hovered) {
      hovered.userData.ring.material.opacity = 1;
      hovered.userData.ring.scale.setScalar(1 + Math.sin(t * 6) * 0.1);
    }

    renderer.render(scene, camera);
  }
  animate();
}
