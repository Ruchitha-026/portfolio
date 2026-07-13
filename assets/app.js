(() => {
  const menuButton = document.querySelector('.menu-toggle');
  const navLinks = document.querySelector('.nav-links');
  if (menuButton && navLinks) {
    menuButton.addEventListener('click', () => {
      const open = navLinks.classList.toggle('open');
      menuButton.setAttribute('aria-expanded', String(open));
    });
    navLinks.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
      navLinks.classList.remove('open');
      menuButton.setAttribute('aria-expanded', 'false');
    }));
  }

  const revealObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

  document.querySelectorAll('[data-count]').forEach(el => {
    const target = Number(el.dataset.count || 0);
    let started = false;
    const observer = new IntersectionObserver(entries => {
      if (!entries[0].isIntersecting || started) return;
      started = true;
      const start = performance.now();
      const duration = 950;
      const tick = now => {
        const progress = Math.min((now - start) / duration, 1);
        const value = Math.floor(target * (1 - Math.pow(1 - progress, 3)));
        el.textContent = value + (el.dataset.suffix || '');
        if (progress < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
      observer.disconnect();
    }, {threshold: .5});
    observer.observe(el);
  });

  document.querySelectorAll('.tab-shell').forEach(shell => {
    const buttons = [...shell.querySelectorAll('.tab-button')];
    const panels = [...shell.querySelectorAll('.tab-panel')];
    buttons.forEach(button => button.addEventListener('click', () => {
      buttons.forEach(b => b.classList.toggle('active', b === button));
      panels.forEach(panel => panel.classList.toggle('active', panel.id === button.dataset.tab));
      button.scrollIntoView({behavior:'smooth', block:'nearest', inline:'center'});
    }));
  });

  const processCopy = {
    empathize: 'The users are student organizers who may be balancing coursework, limited budgets, approvals, accessibility needs, and last-minute changes.',
    define: 'Student organizations need a simple and responsible planning method because incomplete preparation can create budget, access, approval, and scheduling problems.',
    ideate: 'The concept combined a budget calculator, event checklist, approval tracker, role planner, and contingency assistant into one focused experience.',
    prototype: 'EventEase AI was configured to collect key details, label estimates, avoid invented confirmations, preserve accessibility, and maintain honesty boundaries.',
    test: 'Five scenarios tested normal planning, budget reduction, venue loss, false-document refusal, and event-day scheduling. All five passed.'
  };
  const processDetail = document.querySelector('.process-detail');
  document.querySelectorAll('.process-step').forEach(step => step.addEventListener('click', () => {
    document.querySelectorAll('.process-step').forEach(s => s.classList.remove('active'));
    step.classList.add('active');
    if (processDetail) processDetail.textContent = processCopy[step.dataset.step] || '';
  }));

  const canvas = document.getElementById('signal-canvas');
  if (canvas && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const ctx = canvas.getContext('2d');
    let width = 0, height = 0, points = [];
    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      width = canvas.clientWidth; height = canvas.clientHeight;
      canvas.width = width * dpr; canvas.height = height * dpr;
      ctx.setTransform(dpr,0,0,dpr,0,0);
      points = Array.from({length: Math.min(70, Math.floor(width/18))}, () => ({
        x: Math.random()*width, y: Math.random()*height,
        vx:(Math.random()-.5)*.24, vy:(Math.random()-.5)*.24,
        r:Math.random()*1.5+.7
      }));
    };
    const draw = () => {
      ctx.clearRect(0,0,width,height);
      points.forEach(p => {
        p.x += p.vx; p.y += p.vy;
        if(p.x<0||p.x>width) p.vx*=-1;
        if(p.y<0||p.y>height) p.vy*=-1;
        ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
        ctx.fillStyle='rgba(77,232,255,.65)'; ctx.fill();
      });
      for(let i=0;i<points.length;i++) for(let j=i+1;j<points.length;j++){
        const a=points[i],b=points[j],dx=a.x-b.x,dy=a.y-b.y,d=Math.hypot(dx,dy);
        if(d<125){ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.strokeStyle=`rgba(159,124,255,${(1-d/125)*.16})`;ctx.stroke();}
      }
      requestAnimationFrame(draw);
    };
    resize(); window.addEventListener('resize',resize); draw();
  }
})();
