/* ============================================================
   桥见 · 飞夺泸定桥 —— 三维艺术化示意模型（three.js 程序化建模）
   ------------------------------------------------------------
   性质声明：本场景为「艺术化复原示意」，仅表达泸定桥的结构意象
   （13 根铁索、桥板、桥头建筑、大渡河峡谷），不作为任何历史事实
   的证据，不呈现战斗细节。所有元素为程序化建模，无外部模型文件。
   交互：左键拖拽环视 / 滚轮缩放 / 悬停高亮铁索 / 点击查看说明。
   ============================================================ */

async function main() {
  const THREE = await import('../lib/three.module.min.js');

  const container = document.getElementById('stage');
  const tipEl = document.getElementById('tip');
  const card = document.getElementById('card');
  const cardTitle = document.getElementById('card-title');
  const cardBody = document.getElementById('card-body');

  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#0d1a20');
  scene.fog = new THREE.Fog('#0d1a20', 14, 34);

  // const camera = new THREE.PerspectiveCamera(46, 1, 0.1, 100);
  // const target = new THREE.Vector3(0, 0.6, 0);

  const camera = new THREE.PerspectiveCamera(46, 1, 0.1, 100);
const target = new THREE.Vector3(0, 1.0, 0);

// 初始化相机位置，并朝向桥梁中心
camera.position.set(0, 9, 15);
camera.lookAt(target);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  // 必须将 WebGL 画布挂载到页面容器，否则场景不会显示。
  container.appendChild(renderer.domElement);

  /* ---------- 光照 ---------- */
  // scene.add(new THREE.AmbientLight(0xffffff, 1.0));
  // const sun = new THREE.DirectionalLight(0xffe6bf, 1.5);
  // sun.position.set(6, 9, 4);
  // scene.add(sun);
  // const rimL = new THREE.DirectionalLight(0x6fa0c0, 0.5);
  // rimL.position.set(-6, 3, -5);
  // scene.add(rimL);
  // 环境光：提高暗部的可见度
scene.add(new THREE.AmbientLight(0xffffff, 2.0));

// 主光源：照亮桥面、铁索和山体
const sun = new THREE.DirectionalLight(0xffe6bf, 2.5);
sun.position.set(4, 10, 6);
scene.add(sun);

// 补光：照亮桥梁另一侧
const fillLight = new THREE.DirectionalLight(0xffffff, 1.5);
fillLight.position.set(-6, 5, 8);
scene.add(fillLight);

// 轮廓光：增强铁索与背景的区分
const rimL = new THREE.DirectionalLight(0x9bc9e0, 1.0);
rimL.position.set(-6, 4, -5);
scene.add(rimL);

  /* ---------- 两岸山体（示意） ---------- */
  function makeMountain(x, z, s, h) {
    const geo = new THREE.ConeGeometry(s, h, 7, 3);
    const pos = geo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      pos.setX(i, pos.getX(i) + (Math.random() - 0.5) * s * 0.35);
      pos.setZ(i, pos.getZ(i) + (Math.random() - 0.5) * s * 0.35);
    }
    geo.computeVertexNormals();
    const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
      // color: 0x3d4a42, roughness: 1, flatShading: true,
      color: 0x68786a,
roughness: 0.95,
flatShading: true,
    }));
    m.position.set(x, h / 2 - 0.4, z);
    scene.add(m);
  }
  [[-9, -4, 3.2, 5], [-10.5, 2, 2.6, 4], [9, -4, 3.4, 5.5], [10.5, 3, 2.8, 4.2],
   [-7, -8, 3, 4], [7, -8, 3.2, 4.6], [-11, -2, 2.4, 3.4], [11.5, 0, 2.4, 3.4]]
    .forEach(([x, z, s, h]) => makeMountain(x, z, s, h));

  /* ---------- 大渡河水面（顶点动画） ---------- */
  const waterGeo = new THREE.PlaneGeometry(30, 16, 60, 32);
  const waterMat = new THREE.MeshStandardMaterial({
    color: 0x397987, roughness: 0.3, metalness: 0.15,
    transparent: true, opacity: 0.92,
  });
  const water = new THREE.Mesh(waterGeo, waterMat);
  water.rotation.x = -Math.PI / 2;
  water.position.y = -0.4;
  scene.add(water);
  const waterBase = waterGeo.attributes.position.array.slice();

  /* ---------- 桥的几何参数 ---------- */
  const SPAN = 10;           // 桥跨度
  const Y = 0.9;             // 桥面高
  const SAG = 0.55;          // 铁索垂度
  const N_CHAIN = 13;        // 13 根铁索
  const CHAIN_GAP = 0.26;    // 铁索间距

  // 铁索：悬链线近似（二次贝塞尔）
  function chainPoints(z) {
    const a = new THREE.Vector3(-SPAN / 2, Y, z);
    const b = new THREE.Vector3(SPAN / 2, Y, z);
    const mid = new THREE.Vector3(0, Y - SAG, z);
    return new THREE.QuadraticBezierCurve3(a, mid, b);
  }

  // const chainMat = new THREE.MeshStandardMaterial({
  //   color: 0x8a8f96, roughness: 0.45, metalness: 0.85,
  // });
  const chainMat = new THREE.MeshStandardMaterial({
  color: 0xc0c5c9,
  roughness: 0.35,
  metalness: 0.45,
});
  const chains = [];
  const chainGroup = new THREE.Group();
  scene.add(chainGroup);

  for (let i = 0; i < N_CHAIN; i++) {
    const z = (i - (N_CHAIN - 1) / 2) * CHAIN_GAP;
    const curve = chainPoints(z);
    // 用多段小圆环模拟铁环链
    const chain = new THREE.Group();
    const N = 56;
    const pts = curve.getPoints(N);
    for (let k = 0; k < N - 1; k++) {
      const p = pts[k];
      const link = new THREE.Mesh(
        new THREE.TorusGeometry(0.045, 0.013, 8, 14),
        chainMat
      );
      link.position.copy(p);
      const tan = pts[k + 1].clone().sub(p);
      link.lookAt(link.position.clone().add(tan));
      link.rotateX(Math.PI / 2);
      chain.add(link);
    }
    chain.userData = {
      idx: i + 1,
      curve,
      label: `第 ${i + 1} 根铁索`,
      body: `泸定桥由 13 根铁索构成（已核验史实，见史料档案 S01/S02/S03）。` +
            `红军到达时，守敌已拆除大部分桥板。本场景以艺术化方式呈现铁索意象。`,
    };
    chainGroup.add(chain);
    chains.push(chain);
  }

  /* ---------- 残存桥板（示意：大部分已被拆除） ---------- */
  const plankMat = new THREE.MeshStandardMaterial({
    color: 0x6d5233, roughness: 0.9,
  });
  const plankGeo = new THREE.BoxGeometry(0.22, 0.028, CHAIN_GAP * 0.92);
  // 仅底部 4 根铁索之间铺设少量桥板，艺术化表达"桥板大多被拆"
  for (let k = 0; k < 5; k++) {
    const zi = 4 + k;   // 底部的几根链位
    const z = (zi - (N_CHAIN - 1) / 2) * CHAIN_GAP;
    const curve = chainPoints(z);
    for (let j = 3; j < 22; j += 4) {
      const p = curve.getPoint(j / 24);
      const plank = new THREE.Mesh(plankGeo, plankMat);
      plank.position.set(p.x, p.y - 0.03, z);
      plank.rotation.z = -Math.atan2(
        curve.getPoint(j / 24 + 0.01).y - p.y, 0.4);
      chainGroup.add(plank);
    }
  }

  /* ---------- 桥头建筑（两岸桥台，示意） ---------- */
  function makeAbutment(x) {
    const gp = new THREE.Group();
    const stone = new THREE.MeshStandardMaterial({
      color: 0x817466, roughness: 0.9, flatShading: true,
    });
    // 桥台主体
    const base = new THREE.Mesh(new THREE.BoxGeometry(1.5, 2.6, 4.2), stone);
    base.position.set(0, 0.9, 0);
    // 门洞（用两个侧柱 + 顶梁拼出）
    const pillar1 = new THREE.Mesh(new THREE.BoxGeometry(1.5, 2.6, 1.4), stone);
    pillar1.position.set(0, 0.9, -2.8);
    const pillar2 = pillar1.clone();
    pillar2.position.z = 2.8;
    // 顶檐
    const roof = new THREE.Mesh(
      new THREE.BoxGeometry(1.8, 0.18, 4.6),
      new THREE.MeshStandardMaterial({ color: 0x3b332c, roughness: 0.9 }));
    roof.position.set(0, 2.3, 0);
    const roof2 = roof.clone();
    roof2.position.y = 2.55; roof2.scale.set(0.82, 1, 0.9);
    // 匾额（金色牌子）
    const plaque = new THREE.Mesh(
      new THREE.BoxGeometry(0.06, 0.5, 1.6),
      new THREE.MeshStandardMaterial({ color: 0xb98a2f, metalness: 0.6, roughness: 0.35 }));
    plaque.position.set(-0.78, 1.7, 0);

    gp.add(base, pillar1, pillar2, roof, roof2, plaque);
    gp.position.set(x, 0, 0);
    scene.add(gp);
  }
  makeAbutment(-SPAN / 2 - 0.7);
  makeAbutment(SPAN / 2 + 0.7);

  /* ---------- 两岸地名标注（Sprite 文字） ---------- */
  function makeLabel(text, x, y, z) {
    const cv = document.createElement('canvas');
    cv.width = 256; cv.height = 96;
    const g = cv.getContext('2d');
    g.font = '600 44px "PingFang SC","Microsoft YaHei",sans-serif';
    g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillStyle = 'rgba(253,246,236,0.95)';
    g.shadowColor = 'rgba(0,0,0,0.7)'; g.shadowBlur = 8;
    g.fillText(text, 128, 48);
    const tex = new THREE.CanvasTexture(cv);
    tex.colorSpace = THREE.SRGBColorSpace;
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({
      map: tex, transparent: true, depthTest: false,
    }));
    sp.scale.set(2.4, 0.9, 1);
    sp.position.set(x, y, z);
    scene.add(sp);
  }
  makeLabel('西岸 · 海子山方向', -SPAN / 2 - 0.7, 3.4, 0);
  makeLabel('东岸 · 东灵山方向', SPAN / 2 + 0.7, 3.4, 0);
  makeLabel('大渡河', 0, 0.35, 7.5);

  /* ---------- 手写轨道控制（避免额外依赖） ---------- */
  // let theta = 0.42, phi = 1.18, radius = 15;
  let theta = 0.25, phi = 0.95, radius = 17;
  let dragging = false, lx = 0, ly = 0;
  let hovered = null;

  const el = renderer.domElement;
  el.style.cursor = 'grab';

  const onDown = e => {
    dragging = true;
    lx = e.clientX; ly = e.clientY;
    el.style.cursor = 'grabbing';
  };
  const onMove = e => {
    const rect = el.getBoundingClientRect();
    const mx = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    const my = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    mouse.set(mx, my);
    if (dragging) {
      theta -= (e.clientX - lx) * 0.005;
      phi = Math.max(0.35, Math.min(1.45, phi - (e.clientY - ly) * 0.004));
      lx = e.clientX; ly = e.clientY;
    }
  };
  const onUp = () => { dragging = false; el.style.cursor = 'grab'; };
  const onWheel = e => {
    e.preventDefault();
    radius = Math.max(6, Math.min(26, radius + e.deltaY * 0.012));
  };
  el.addEventListener('mousedown', onDown);
  window.addEventListener('mousemove', onMove);
  window.addEventListener('mouseup', onUp);
  el.addEventListener('wheel', onWheel, { passive: false });
  el.addEventListener('touchstart', e => {
    const t = e.touches[0];
    dragging = true; lx = t.clientX; ly = t.clientY;
  }, { passive: true });
  el.addEventListener('touchmove', e => {
    const t = e.touches[0];
    if (dragging) {
      theta -= (t.clientX - lx) * 0.005;
      phi = Math.max(0.35, Math.min(1.45, phi - (t.clientY - ly) * 0.004));
      lx = t.clientX; ly = t.clientY;
    }
  }, { passive: true });
  el.addEventListener('touchend', () => { dragging = false; });

  /* ---------- 拾取 ---------- */
  const ray = new THREE.Raycaster();
  const mouse = new THREE.Vector2(-10, -10);
  const linkMeshes = [];
  chains.forEach(c => c.children.forEach(m => {
    m.userData.root = c;
    linkMeshes.push(m);
  }));

  el.addEventListener('click', () => {
    if (hovered) {
      const d = hovered.userData;
      cardTitle.textContent = d.label;
      cardBody.textContent = d.body;
      card.classList.add('on');
    } else {
      card.classList.remove('on');
    }
  });

  /* ---------- 自适应 ---------- */
  // const resize = () => {
  //   const w = container.clientWidth || 800;
  //   const h = container.clientHeight || 560;
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

  if (!width || !height) return;

  renderer.setSize(width, height, false);

  camera.aspect = width / height;
  camera.updateProjectionMatrix();

  renderer.render(scene, camera);
}

window.addEventListener("resize", resize);

if (window.ResizeObserver) {
  new ResizeObserver(resize).observe(container);
}

resize();

  /* ---------- 动画 ---------- */
  const clock = new THREE.Clock();
  function animate() {
    requestAnimationFrame(animate);
    const t = clock.getElapsedTime();

    // 相机绕目标点
    camera.position.set(
      target.x + radius * Math.sin(phi) * Math.cos(theta),
      target.y + radius * Math.cos(phi),
      target.z + radius * Math.sin(phi) * Math.sin(theta));
    camera.lookAt(target);

    // 水面波动
    const pos = waterGeo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      const bx = waterBase[i * 3], by = waterBase[i * 3 + 1];
      pos.setZ(i, Math.sin(bx * 0.7 + t * 1.4) * 0.09
                + Math.cos(by * 0.9 + t * 1.1) * 0.07);
    }
    pos.needsUpdate = true;
    waterGeo.computeVertexNormals();

    // 铁索悬停高亮
    ray.setFromCamera(mouse, camera);
    const hits = ray.intersectObjects(linkMeshes, false);
    let root = hits.length ? hits[0].object.userData.root : null;

    chains.forEach(c => {
      const hl = c === hovered;
      c.children.forEach(m => {
        m.material = hl ? highlightMat : chainMat;
      });
    });

    if (root !== hovered) {
      hovered = root;
      if (hovered) {
        tipEl.innerHTML = `<b>${hovered.userData.label}</b><i>点击查看说明</i>`;
        tipEl.classList.add('on');
        el.style.cursor = 'pointer';
      } else {
        tipEl.classList.remove('on');
        el.style.cursor = 'grab';
      }
    }

    renderer.render(scene, camera);
  }
  const highlightMat = new THREE.MeshStandardMaterial({
    color: 0xe8b45f, roughness: 0.3, metalness: 0.9,
  });

  // 启动渲染循环；否则只创建场景但不会绘制画面。
  animate();
}

main().catch(err => {
  const c = document.getElementById('stage');
  if (c) c.innerHTML =
    `<div class="b-fail">三维模型未能启动：${String(err && err.message || err)}。` +
    `请使用支持 WebGL 的现代浏览器（Chrome / Edge）查看。</div>`;
});
