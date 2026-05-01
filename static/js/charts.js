/* ================================================================
   EduTrack — Chart.js (Gen Z Neon Theme)
   ================================================================ */
(() => {
    'use strict';

    const C = {
        blue:      'rgba(59,130,246,1)',    blueBg:    'rgba(59,130,246,.15)',
        purple:    'rgba(139,92,246,1)',     purpleBg:  'rgba(139,92,246,.15)',
        green:     'rgba(16,185,129,1)',     greenBg:   'rgba(16,185,129,.15)',
        orange:    'rgba(245,158,11,1)',     orangeBg:  'rgba(245,158,11,.15)',
        cyan:      'rgba(6,182,212,1)',      cyanBg:    'rgba(6,182,212,.15)',
        pink:      'rgba(236,72,153,1)',     pinkBg:    'rgba(236,72,153,.15)',
        red:       'rgba(239,68,68,1)',      redBg:     'rgba(239,68,68,.15)',
    };
    const PALETTE = [C.blue, C.purple, C.green, C.orange, C.cyan, C.pink];
    const PALETTE_BG = [C.blueBg, C.purpleBg, C.greenBg, C.orangeBg, C.cyanBg, C.pinkBg];

    // Defaults
    Chart.defaults.font.family = "'Poppins', sans-serif";
    Chart.defaults.font.size = 12;
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
    Chart.defaults.plugins.legend.labels.padding = 16;
    Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(15,12,41,.92)';
    Chart.defaults.plugins.tooltip.titleFont = { weight: '600', size: 13 };
    Chart.defaults.plugins.tooltip.bodyFont = { size: 12 };
    Chart.defaults.plugins.tooltip.cornerRadius = 10;
    Chart.defaults.plugins.tooltip.padding = 14;
    Chart.defaults.plugins.tooltip.displayColors = true;
    Chart.defaults.animation = { duration: 1200, easing: 'easeOutQuart' };

    const charts = {};
    function make(id, config) {
        if (charts[id]) charts[id].destroy();
        const el = document.getElementById(id);
        if (!el) return null;
        charts[id] = new Chart(el.getContext('2d'), config);
        return charts[id];
    }

    // ── Gradient helper ────────────────────────────────────────────
    function grad(ctx, c1, c2, vertical) {
        const g = vertical
            ? ctx.createLinearGradient(0, 0, 0, ctx.canvas.height)
            : ctx.createLinearGradient(0, 0, ctx.canvas.width, 0);
        g.addColorStop(0, c1); g.addColorStop(1, c2);
        return g;
    }

    // ================================================================
    // STUDENT CHARTS
    // ================================================================
    if (typeof perfData !== 'undefined' && perfData) {
        const rows = perfData.rows || [];
        const labels = rows.map(r => r.subject);

        // Bar Chart
        if (document.getElementById('marksBarChart')) {
            const ctx = document.getElementById('marksBarChart').getContext('2d');
            make('marksBarChart', {
                type: 'bar',
                data: {
                    labels,
                    datasets: [
                        { label: 'Obtained', data: rows.map(r => r.total), backgroundColor: grad(ctx, C.blue, C.purple, true), borderRadius: 8, barPercentage: .5 },
                        { label: 'Max Marks', data: rows.map(r => r.total_max), backgroundColor: C.purpleBg, borderColor: C.purple, borderWidth: 1, borderRadius: 8, barPercentage: .5 },
                    ],
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { position: 'top' }, tooltip: { callbacks: { afterLabel: ctx => `${rows[ctx.dataIndex].percentage}%` } } },
                    scales: { y: { beginAtZero: true, grid: { color: 'rgba(139,92,246,.06)' } }, x: { grid: { display: false } } },
                },
            });
        }

        // Pie Chart
        if (document.getElementById('attendancePieChart')) {
            const present = rows.reduce((s, r) => s + r.present, 0);
            const absent = rows.reduce((s, r) => s + (r.total_classes - r.present), 0);
            make('attendancePieChart', {
                type: 'doughnut',
                data: {
                    labels: ['Present', 'Absent'],
                    datasets: [{ data: [present, absent], backgroundColor: [C.green, C.red], borderWidth: 0, hoverOffset: 12 }],
                },
                options: {
                    responsive: true, maintainAspectRatio: false, cutout: '68%',
                    plugins: { legend: { position: 'bottom' }, tooltip: { callbacks: { label: c => { const t = present + absent; return ` ${c.label}: ${c.raw} (${((c.raw/t)*100).toFixed(1)}%)`; } } } },
                },
            });
        }

        // Line Chart
        if (document.getElementById('trendLineChart')) {
            const ctx = document.getElementById('trendLineChart').getContext('2d');
            const fillGrad = grad(ctx, 'rgba(102,126,234,.25)', 'rgba(102,126,234,.02)', true);
            make('trendLineChart', {
                type: 'line',
                data: {
                    labels,
                    datasets: [{
                        label: 'Subject %', data: rows.map(r => r.percentage),
                        borderColor: C.purple, backgroundColor: fillGrad, fill: true, tension: .4,
                        pointRadius: 5, pointHoverRadius: 9, pointBackgroundColor: '#fff', pointBorderColor: C.purple, pointBorderWidth: 2,
                    }],
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { position: 'top' } },
                    scales: { y: { beginAtZero: true, max: 100, grid: { color: 'rgba(139,92,246,.06)' }, ticks: { callback: v => v + '%' } }, x: { grid: { display: false } } },
                },
            });
        }

        // Full-page charts
        if (document.getElementById('fullBarChart')) {
            make('fullBarChart', {
                type: 'bar',
                data: { labels, datasets: [
                    { label: 'Internal', data: rows.map(r => r.internal), backgroundColor: C.blue, borderRadius: 6, barPercentage: .6 },
                    { label: 'Assignment', data: rows.map(r => r.assignment), backgroundColor: C.purple, borderRadius: 6, barPercentage: .6 },
                    { label: 'External', data: rows.map(r => r.external), backgroundColor: C.green, borderRadius: 6, barPercentage: .6 },
                ] },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'top' } }, scales: { y: { beginAtZero: true, grid: { color: 'rgba(139,92,246,.06)' } }, x: { grid: { display: false } } } },
            });
        }
        if (document.getElementById('fullLineChart')) {
            const ctx = document.getElementById('fullLineChart').getContext('2d');
            make('fullLineChart', {
                type: 'line',
                data: { labels, datasets: [
                    { label: 'Subject %', data: rows.map(r => r.percentage), borderColor: C.purple, backgroundColor: grad(ctx, C.purpleBg, 'transparent', true), fill: true, tension: .4, pointRadius: 6, pointHoverRadius: 9, pointBackgroundColor: '#fff', pointBorderColor: C.purple, pointBorderWidth: 2 },
                    { label: 'Attendance %', data: rows.map(r => r.attendance_pct), borderColor: C.green, backgroundColor: grad(ctx, C.greenBg, 'transparent', true), fill: true, tension: .4, pointRadius: 6, pointHoverRadius: 9, pointBackgroundColor: '#fff', pointBorderColor: C.green, pointBorderWidth: 2 },
                ] },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'top' } }, scales: { y: { beginAtZero: true, max: 100, grid: { color: 'rgba(139,92,246,.06)' }, ticks: { callback: v => v+'%' } }, x: { grid: { display: false } } } },
            });
        }
        if (document.getElementById('fullPieChart')) {
            make('fullPieChart', {
                type: 'doughnut',
                data: { labels, datasets: [{ label: 'Subject %', data: rows.map(r => r.percentage), backgroundColor: PALETTE, borderWidth: 0, hoverOffset: 14 }] },
                options: { responsive: true, maintainAspectRatio: false, cutout: '55%', plugins: { legend: { position: 'bottom' } } },
            });
        }
    }

    // ================================================================
    // FACULTY CHARTS
    // ================================================================
    if (typeof subjectAverages !== 'undefined' && document.getElementById('facultyBarChart')) {
        const sNames = Object.keys(subjectAverages), sAvgs = Object.values(subjectAverages);
        const ctx = document.getElementById('facultyBarChart').getContext('2d');
        let fChart = make('facultyBarChart', {
            type: 'bar',
            data: { labels: sNames, datasets: [{ label: 'Class Avg %', data: sAvgs, backgroundColor: grad(ctx, C.blueBg, C.purpleBg, true), borderColor: C.purple, borderWidth: 2, borderRadius: 8, barPercentage: .5 }] },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'top' } }, scales: { y: { beginAtZero: true, max: 100, grid: { color: 'rgba(139,92,246,.06)' }, ticks: { callback: v => v+'%' } }, x: { grid: { display: false } } } },
        });
        const sel = document.getElementById('chartStudentSelect');
        if (sel && typeof studentsDataForChart !== 'undefined') {
            sel.addEventListener('change', function() {
                const sid = parseInt(this.value);
                const ds = [{ label: 'Class Avg %', data: sAvgs, backgroundColor: grad(ctx, C.blueBg, C.purpleBg, true), borderColor: C.purple, borderWidth: 2, borderRadius: 8, barPercentage: .5 }];
                if (sid) {
                    const s = studentsDataForChart.find(x => x.student_id === sid);
                    if (s) ds.push({ label: s.name, data: sNames.map(n => { const r = s.subjects.find(x => x.subject === n); return r ? r.percentage : 0; }), backgroundColor: C.pinkBg, borderColor: C.pink, borderWidth: 2, borderRadius: 8, barPercentage: .5 });
                }
                fChart.data.datasets = ds; fChart.update();
            });
        }
    }

    // ── Faculty filter / sort / search ─────────────────────────────
    const si = document.getElementById('searchInput'), fb = document.getElementById('filterBranch'), fs = document.getElementById('filterSemester'), rt = document.getElementById('rankingsTable');
    function filterT() {
        if (!rt) return;
        const q = (si?.value || '').toLowerCase(), b = fb?.value || '', s = fs?.value || '';
        rt.querySelectorAll('tbody tr').forEach(r => {
            const ok = (!q || (r.dataset.name||'').includes(q) || (r.dataset.enroll||'').includes(q)) && (!b || r.dataset.branch === b) && (!s || r.dataset.semester === s);
            r.style.display = ok ? '' : 'none';
        });
    }
    if (si) si.addEventListener('input', filterT);
    if (fb) fb.addEventListener('change', filterT);
    if (fs) fs.addEventListener('change', filterT);

    if (rt) rt.querySelectorAll('.sortable').forEach(th => {
        th.addEventListener('click', () => {
            const k = th.dataset.sort, tb = rt.querySelector('tbody'), rows = Array.from(tb.querySelectorAll('tr')), asc = th.classList.toggle('sort-asc');
            rows.sort((a, b) => { if (k === 'name') return asc ? (a.dataset.name||'').localeCompare(b.dataset.name||'') : (b.dataset.name||'').localeCompare(a.dataset.name||''); return asc ? parseFloat(a.dataset[k]||0) - parseFloat(b.dataset[k]||0) : parseFloat(b.dataset[k]||0) - parseFloat(a.dataset[k]||0); });
            rows.forEach(r => tb.appendChild(r));
        });
    });

    // ── Student modal ──────────────────────────────────────────────
    let mBar = null, mPie = null;
    document.querySelectorAll('.view-student-btn').forEach(btn => {
        btn.addEventListener('click', async function() {
            const sid = this.dataset.sid;
            try {
                const res = await fetch(`/api/student/${sid}/data`), data = await res.json();
                if (!res.ok) throw new Error(data.error);
                const st = data.student, p = data.performance;
                document.getElementById('modalStudentName').innerHTML = `<i class="bi bi-person-lines-fill me-2"></i>${st.name}`;
                document.getElementById('modalEnroll').textContent = st.enrollment_no;
                document.getElementById('modalBranch').textContent = st.branch;
                document.getElementById('modalSemester').textContent = st.semester;
                document.getElementById('modalOverall').textContent = p.overall_pct + '%';
                const tb = document.querySelector('#modalTable tbody'); tb.innerHTML = '';
                p.rows.forEach(r => {
                    const sc = r.status==='Pass'?'bg-success':'bg-danger', ac = r.attendance_pct>=75?'bg-success':(r.attendance_pct>=60?'bg-warning text-dark':'bg-danger');
                    tb.innerHTML += `<tr><td class="fw-semibold">${r.subject}</td><td class="text-center">${Math.round(r.internal)}/${Math.round(r.internal_max)}</td><td class="text-center">${Math.round(r.assignment)}/${Math.round(r.assignment_max)}</td><td class="text-center">${Math.round(r.external)}/${Math.round(r.external_max)}</td><td class="text-center fw-bold">${Math.round(r.total)}/${Math.round(r.total_max)}</td><td class="text-center"><span class="badge ${ac}">${r.attendance_pct}%</span></td><td class="text-center"><span class="badge ${sc}">${r.status}</span></td></tr>`;
                });
                if (mBar) mBar.destroy();
                mBar = new Chart(document.getElementById('modalBarChart').getContext('2d'), { type:'bar', data:{ labels:p.rows.map(r=>r.subject), datasets:[{ label:'Obtained', data:p.rows.map(r=>r.total), backgroundColor:C.purple, borderRadius:8, barPercentage:.5 },{ label:'Max', data:p.rows.map(r=>r.total_max), backgroundColor:C.purpleBg, borderColor:C.purple, borderWidth:1, borderRadius:8, barPercentage:.5 }] }, options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'top'}}, scales:{y:{beginAtZero:true, grid:{color:'rgba(139,92,246,.06)'}}, x:{grid:{display:false}}} } });
                const prT = p.rows.reduce((s,r)=>s+r.present,0), abT = p.rows.reduce((s,r)=>s+(r.total_classes-r.present),0);
                if (mPie) mPie.destroy();
                mPie = new Chart(document.getElementById('modalPieChart').getContext('2d'), { type:'doughnut', data:{ labels:['Present','Absent'], datasets:[{ data:[prT,abT], backgroundColor:[C.green,C.red], borderWidth:0, hoverOffset:10 }] }, options:{ responsive:true, maintainAspectRatio:false, cutout:'62%', plugins:{legend:{position:'bottom'}} } });
            } catch(e) { console.error(e); if (typeof showToast==='function') showToast('Failed to load','danger'); }
        });
    });
})();
