/* ================================================================
   EduTrack — Interactions & Micro-animations
   Dark mode · Count-up · Ripple · Skeleton loading · AOS-like reveals
   ================================================================ */
(() => {
    'use strict';

    // ── Dark Mode Toggle ───────────────────────────────────────────
    const THEME_KEY = 'edutrack-theme';
    function getTheme() { return localStorage.getItem(THEME_KEY) || 'light'; }
    function applyTheme(t) {
        document.documentElement.setAttribute('data-theme', t);
        localStorage.setItem(THEME_KEY, t);
        document.querySelectorAll('.theme-toggle i').forEach(i => {
            i.className = t === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
        });
    }
    applyTheme(getTheme());
    document.addEventListener('click', e => {
        const btn = e.target.closest('.theme-toggle');
        if (btn) applyTheme(getTheme() === 'dark' ? 'light' : 'dark');
    });

    // ── Count-Up Animation ─────────────────────────────────────────
    function animateValue(el, start, end, duration) {
        const isFloat = String(end).includes('.');
        const startTime = performance.now();
        function update(now) {
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic
            const current = start + (end - start) * eased;
            el.textContent = isFloat ? current.toFixed(1) : Math.round(current);
            if (progress < 1) requestAnimationFrame(update);
        }
        requestAnimationFrame(update);
    }

    // Observe .count-up elements
    const countObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const target = parseFloat(el.dataset.target || el.textContent);
                if (!isNaN(target) && !el.dataset.counted) {
                    el.dataset.counted = '1';
                    animateValue(el, 0, target, 1200);
                }
                countObserver.unobserve(el);
            }
        });
    }, { threshold: 0.3 });

    document.querySelectorAll('.count-up').forEach(el => countObserver.observe(el));

    // ── Button Ripple Effect ───────────────────────────────────────
    document.addEventListener('click', e => {
        const btn = e.target.closest('.btn');
        if (!btn) return;
        const ripple = document.createElement('span');
        ripple.className = 'ripple';
        const rect = btn.getBoundingClientRect();
        ripple.style.left = (e.clientX - rect.left - 10) + 'px';
        ripple.style.top = (e.clientY - rect.top - 10) + 'px';
        btn.appendChild(ripple);
        setTimeout(() => ripple.remove(), 600);
    });

    // ── Scroll Reveal (lightweight AOS alternative) ────────────────
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
                revealObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

    document.querySelectorAll('[data-reveal]').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = `opacity .6s var(--ease) ${el.dataset.delay || '0s'}, transform .6s var(--ease) ${el.dataset.delay || '0s'}`;
        revealObserver.observe(el);
    });

    // Revealed state
    const style = document.createElement('style');
    style.textContent = '.revealed { opacity: 1 !important; transform: translateY(0) !important; }';
    document.head.appendChild(style);

    // ── Card Tilt on Hover (subtle) ────────────────────────────────
    document.querySelectorAll('.stat-card').forEach(card => {
        card.addEventListener('mousemove', e => {
            const rect = card.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width - 0.5;
            const y = (e.clientY - rect.top) / rect.height - 0.5;
            card.style.transform = `translateY(-5px) scale(1.02) perspective(600px) rotateY(${x * 5}deg) rotateX(${-y * 5}deg)`;
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
        });
    });

})();
