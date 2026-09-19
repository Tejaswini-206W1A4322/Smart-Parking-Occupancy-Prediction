"""Builds the HTML/JS for the immersive 3D hero section on the landing page.

Rendered via st.components.v1.html so the Three.js/GSAP scripts execute.
This keeps the dark, glowing aesthetic fully contained inside its own iframe.
"""

from utils.ui import _logo_base64


def hero_html(height=520):
    logo_b64 = _logo_base64()
    logo_tag = f'<img class="hero-logo" src="data:image/png;base64,{logo_b64}"/>' if logo_b64 else ""

    return f"""
    <div class="hero-wrap">
      <canvas id="hero-canvas"></canvas>

      <div class="hero-content">
        <div class="hero-logo-card">{logo_tag}</div>
        <h1 class="hero-title">AI-Driven Smart<br/>Occupancy Prediction</h1>
        <p class="hero-sub">
          Real-time parking availability powered by live bookings<br/>
          and XGBoost machine learning — always one step ahead.
        </p>
        <div class="hero-actions">
          <button class="hero-cta" id="hero-cta-btn">🚗 &nbsp;Explore Smart Parking</button>
          <button class="hero-secondary" onclick="window.parent.document.getElementById('sign-in') && window.parent.document.getElementById('sign-in').scrollIntoView({{behavior:'smooth'}})">
            🔐 &nbsp;Sign In
          </button>
        </div>
        <div class="hero-hint">↓ &nbsp;Sign in or create your account below</div>
        <div class="hero-stats">
          <div class="hero-stat"><span class="hero-stat-val">98%</span><span class="hero-stat-lbl">Accuracy</span></div>
          <div class="hero-stat-sep">·</div>
          <div class="hero-stat"><span class="hero-stat-val">12+</span><span class="hero-stat-lbl">Live Lots</span></div>
          <div class="hero-stat-sep">·</div>
          <div class="hero-stat"><span class="hero-stat-val">10s</span><span class="hero-stat-lbl">Response Time</span></div>
        </div>
      </div>
    </div>

    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&family=Outfit:wght@400;700;800;900&display=swap');
      * {{ box-sizing: border-box; }}
      body {{ margin: 0; overflow: hidden; background: transparent; }}
      .hero-wrap {{
        position: relative;
        width: 100%;
        height: {height}px;
        background: radial-gradient(ellipse at 30% 40%, #0D1F3C 0%, #080D1A 55%, #040810 100%);
        border-radius: 22px;
        overflow: hidden;
        border: 1px solid rgba(99,102,241,0.22);
        box-shadow: 0 20px 60px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.05);
        font-family: 'Inter', 'Outfit', sans-serif;
      }}
      #hero-canvas {{ position: absolute; inset: 0; width: 100%; height: 100%; display: block; }}
      .hero-content {{
        position: relative; z-index: 2; height: 100%;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        text-align: center; padding: 28px;
        pointer-events: none;
      }}
      .hero-logo-card {{
        background: #fff;
        border-radius: 14px;
        padding: 8px 14px;
        box-shadow: 0 0 40px rgba(59,130,246,0.30), 0 8px 24px rgba(0,0,0,0.5);
        margin-bottom: 20px;
        display: inline-block;
      }}
      .hero-logo-card img {{ height: 42px; display: block; }}
      .hero-title {{
        color: #FFFFFF;
        font-size: 2.4rem;
        font-weight: 900;
        line-height: 1.2;
        margin: 0 0 12px 0;
        letter-spacing: -0.02em;
        text-shadow: 0 0 40px rgba(99,102,241,0.50), 0 2px 4px rgba(0,0,0,0.4);
      }}
      .hero-sub {{
        color: #CBD5E1;
        font-size: 1rem;
        margin: 0 0 28px 0;
        max-width: 500px;
        font-weight: 400;
        line-height: 1.6;
        text-shadow: 0 1px 3px rgba(0,0,0,0.4);
      }}
      .hero-actions {{
        display: flex; gap: 14px; align-items: center;
        pointer-events: auto; margin-bottom: 20px;
        flex-wrap: wrap; justify-content: center;
      }}
      .hero-cta {{
        cursor: pointer;
        border: none;
        border-radius: 999px;
        padding: 13px 32px;
        font-size: 0.95rem;
        font-weight: 800;
        color: #fff;
        background: linear-gradient(135deg, #3B82F6, #6366F1);
        box-shadow: 0 0 0 0 rgba(99,102,241,0.5), 0 8px 24px rgba(99,102,241,0.40);
        transition: transform 0.22s ease, box-shadow 0.22s ease;
        font-family: 'Inter', sans-serif;
        letter-spacing: 0.01em;
      }}
      .hero-cta:hover {{
        transform: translateY(-3px) scale(1.04);
        box-shadow: 0 12px 36px rgba(99,102,241,0.70);
      }}
      .hero-secondary {{
        cursor: pointer;
        border: 1.5px solid rgba(255,255,255,0.22);
        border-radius: 999px;
        padding: 12px 28px;
        font-size: 0.95rem;
        font-weight: 700;
        color: #f1f5f9;
        background: rgba(255,255,255,0.06);
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
        transition: all 0.22s ease;
        font-family: 'Inter', sans-serif;
        letter-spacing: 0.01em;
      }}
      .hero-secondary:hover {{
        background: rgba(99,102,241,0.20);
        border-color: rgba(99,102,241,0.50);
        box-shadow: 0 8px 24px rgba(99,102,241,0.30);
        transform: translateY(-2px);
      }}
      .hero-hint {{
        color: #94A3B8;
        font-size: 0.8rem;
        font-weight: 500;
        animation: hero-bob 2s ease-in-out infinite;
        margin-bottom: 22px;
      }}
      @keyframes hero-bob {{
        0%, 100% {{ transform: translateY(0); opacity: .6; }}
        50%        {{ transform: translateY(6px); opacity: 1; }}
      }}
      .hero-stats {{
        display: flex;
        gap: 10px;
        align-items: center;
        background: rgba(255,255,255,0.04);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 999px;
        padding: 10px 24px;
        pointer-events: none;
      }}
      .hero-stat {{ display: flex; flex-direction: column; align-items: center; }}
      .hero-stat-val {{
        font-size: 0.95rem; font-weight: 900; color: #A5B4FC;
        line-height: 1;
      }}
      .hero-stat-lbl {{
        font-size: 0.68rem; color: #94A3B8; font-weight: 500;
        text-transform: uppercase; letter-spacing: .06em; margin-top: 2px;
      }}
      .hero-stat-sep {{ color: rgba(255,255,255,0.2); font-size: 1.2rem; padding: 0 4px; }}

      @media (max-width: 640px) {{
        .hero-title {{ font-size: 1.75rem; }}
        .hero-sub {{ font-size: 0.9rem; }}
        .hero-actions {{ gap: 10px; }}
        .hero-stats {{ padding: 8px 14px; }}
      }}
    </style>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
      (function() {{
        const wrap   = document.querySelector('.hero-wrap');
        const canvas = document.getElementById('hero-canvas');
        const W = wrap.clientWidth, H = wrap.clientHeight;

        const scene    = new THREE.Scene();
        const camera   = new THREE.PerspectiveCamera(50, W / H, 0.1, 1000);
        camera.position.z = 6;

        const renderer = new THREE.WebGLRenderer({{ canvas, antialias: true, alpha: true }});
        renderer.setSize(W, H);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        const group = new THREE.Group();

        // Core solid shape
        const coreGeo = new THREE.IcosahedronGeometry(1.05, 1);
        const coreMat = new THREE.MeshBasicMaterial({{ color: 0x3B82F6, wireframe: false, transparent: true, opacity: 0.08 }});
        group.add(new THREE.Mesh(coreGeo, coreMat));

        // Wireframe layers
        const w1Geo = new THREE.IcosahedronGeometry(1.55, 1);
        const w1Mat = new THREE.MeshBasicMaterial({{ color: 0x6366F1, wireframe: true, transparent: true, opacity: 0.80 }});
        const w1 = new THREE.Mesh(w1Geo, w1Mat);
        group.add(w1);

        const w2Geo = new THREE.IcosahedronGeometry(2.0, 0);
        const w2Mat = new THREE.MeshBasicMaterial({{ color: 0x3B82F6, wireframe: true, transparent: true, opacity: 0.25 }});
        group.add(new THREE.Mesh(w2Geo, w2Mat));

        const w3Geo = new THREE.IcosahedronGeometry(2.5, 0);
        const w3Mat = new THREE.MeshBasicMaterial({{ color: 0xA5B4FC, wireframe: true, transparent: true, opacity: 0.10 }});
        group.add(new THREE.Mesh(w3Geo, w3Mat));

        // Floating particles
        const pCount = 180;
        const pGeo   = new THREE.BufferGeometry();
        const pPos   = new Float32Array(pCount * 3);
        for (let i = 0; i < pCount; i++) {{
          pPos[i*3]   = (Math.random() - 0.5) * 14;
          pPos[i*3+1] = (Math.random() - 0.5) * 9;
          pPos[i*3+2] = (Math.random() - 0.5) * 9 - 2;
        }}
        pGeo.setAttribute('position', new THREE.BufferAttribute(pPos, 3));
        const pMat = new THREE.PointsMaterial({{ color: 0x6366F1, size: 0.032, transparent: true, opacity: 0.55 }});
        const particles = new THREE.Points(pGeo, pMat);

        scene.add(group);
        scene.add(particles);

        let targetX = 0, targetY = 0, hovering = false;

        wrap.addEventListener('mousemove', (e) => {{
          const rect = wrap.getBoundingClientRect();
          targetX = ((e.clientX - rect.left) / rect.width  * 2 - 1) * 0.55;
          targetY = ((e.clientY - rect.top)  / rect.height * 2 - 1) * 0.35;
        }});
        wrap.addEventListener('mouseenter', () => hovering = true);
        wrap.addEventListener('mouseleave', () => {{ hovering = false; targetX = 0; targetY = 0; }});

        let scale = 1;
        function animate() {{
          requestAnimationFrame(animate);
          group.rotation.y += 0.003;
          group.rotation.x += 0.001;
          group.rotation.y += (targetX - group.rotation.y * 0.12) * 0.018;
          group.rotation.x += (targetY - group.rotation.x * 0.12) * 0.018;

          const tScale = hovering ? 1.10 : 1.0;
          scale += (tScale - scale) * 0.07;
          group.scale.set(scale, scale, scale);
          w1Mat.opacity = hovering ? 1.0 : 0.80;

          particles.rotation.y += 0.0005;
          renderer.render(scene, camera);
        }}
        animate();

        window.addEventListener('resize', () => {{
          const w = wrap.clientWidth, h = wrap.clientHeight;
          camera.aspect = w / h;
          camera.updateProjectionMatrix();
          renderer.setSize(w, h);
        }});

        document.getElementById('hero-cta-btn').addEventListener('click', () => {{
          scale = 1.25;
          const target = window.parent.document.getElementById('sign-in');
          if (target) target.scrollIntoView({{ behavior: 'smooth' }});
        }});
      }})();
    </script>
    """