/* ==========================================================
   Team data comes from data.js (written by fetch_data.py).
   Do not edit the numbers here. Run fetch_data.py instead.
   ========================================================== */
const TEAMS = LEAGUE_DATA.teams;

// Fallback colors, used only if a team isn't in keys.py's get_team_colors()
// const COLORS = ['#d35400','#e63946','#2a9d8f','#f4a261','#6a4c93',
//                 '#43aa8b','#f9c74f','#577590','#d62828','#8ac926',
//                 '#ff8fab','#264653'];

// Team colors from keys.py, saved by fetch_data.py
const TEAM_COLORS = LEAGUE_DATA.colors || {};
const teamColor = i => TEAM_COLORS[TEAMS[i].name] || COLORS[i % COLORS.length];

Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
Chart.defaults.font.size = 12;

const weekCount = TEAMS[0].weekly.length;
const weekLabels = Array.from({ length: weekCount }, (_, i) => `Wk ${i + 1}`);

/* ---------- 1. Season points (horizontal bars) ---------- */
const totals = TEAMS
  .map((t, i) => ({ name: t.name, total: t.weekly.reduce((a, b) => a + b, 0), idx: i }))
  .sort((a, b) => b.total - a.total);

new Chart(document.getElementById('standingsChart'), {
  type: 'bar',
  data: {
    labels: totals.map(t => t.name),
    datasets: [{
      data: totals.map(t => +t.total.toFixed(1)),
      backgroundColor: totals.map(t => teamColor(t.idx)),
      borderRadius: 4
    }]
  },
  options: {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: { x: { beginAtZero: true } }
  }
});

/* ---------- 2. Cumulative points race (lines) ---------- */
const racePoints = TEAMS.map((t, i) => {
  let running = 0;
  return {
    label: t.name,
    data: t.weekly.map(p => { running += p; return +running.toFixed(1); }),
    borderColor: teamColor(i),
    backgroundColor: teamColor(i),
    borderWidth: 2,
    pointRadius: 2,
    tension: 0.3
  };
});

new Chart(document.getElementById('raceChart'), {
  type: 'line',
  data: { labels: weekLabels, datasets: racePoints },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'nearest', intersect: false },
    plugins: {
      legend: { position: 'bottom', labels: { boxWidth: 12 } }
    },
    scales: { y: { beginAtZero: false } }
  }
});

/* ---------- 2b. Cumulative points against (lines) ---------- */
const againstLines = TEAMS.map((t, i) => {
  let running = 0;
  return {
    label: t.name,
    data: t.weekly_against.map(p => { running += p; return +running.toFixed(1); }),
    borderColor: teamColor(i),
    backgroundColor: teamColor(i),
    borderWidth: 2,
    pointRadius: 2,
    tension: 0.3
  };
});

new Chart(document.getElementById('againstChart'), {
  type: 'line',
  data: { labels: weekLabels, datasets: againstLines },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'nearest', intersect: false },
    plugins: {
      legend: { position: 'bottom', labels: { boxWidth: 12 } }
    },
    scales: { y: { beginAtZero: false } }
  }
});

/* ---------- 3. Weekly scores (bars, pick a week) ---------- */
const weekSelect = document.getElementById('weekSelect');
weekLabels.forEach((label, i) => {
  const opt = document.createElement('option');
  opt.value = i;
  opt.textContent = label;
  weekSelect.appendChild(opt);
});

const weekChart = new Chart(document.getElementById('weekChart'), {
  type: 'bar',
  data: { labels: [], datasets: [{ data: [], backgroundColor: [], borderRadius: 4 }] },
  options: {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: { x: { beginAtZero: true } }
  }
});

function showWeek(w) {
  const rows = TEAMS
    .map((t, i) => ({ name: t.name, score: t.weekly[w], idx: i }))
    .sort((a, b) => b.score - a.score);
  weekChart.data.labels = rows.map(r => r.name);
  weekChart.data.datasets[0].data = rows.map(r => r.score);
  weekChart.data.datasets[0].backgroundColor = rows.map(r => teamColor(r.idx));
  weekChart.update();
}

weekSelect.addEventListener('change', e => showWeek(+e.target.value));
showWeek(weekCount - 1); // start on the most recent week
weekSelect.value = weekCount - 1;

/* ---------- 4. Standings over time (rank grid) ---------- */

// Rank of every team after a given week, using the same tiebreaker as standings.py
// (wins first, then total points)
function rankAt(week) {
  const rec = {};
  TEAMS.forEach(t => {
    rec[t.name] = {
      wins: 0,
      pf: t.weekly.slice(0, week).reduce((a, b) => a + b, 0)
    };
  });

  LEAGUE_DATA.matchups
    .filter(m => m.week <= week)
    .forEach(m => {
      if (m.home_score > m.away_score) rec[m.home].wins++;
      else if (m.away_score > m.home_score) rec[m.away].wins++;
    });

  const order = Object.keys(rec).sort(
    (a, b) => rec[b].wins - rec[a].wins || rec[b].pf - rec[a].pf
  );

  const ranks = {};
  order.forEach((name, i) => { ranks[name] = i + 1; });
  return ranks;
}

// Dark orange for 1st, pale orange for last
function heatColor(rank, total) {
  const t = total > 1 ? (rank - 1) / (total - 1) : 0;
  const from = [211, 84, 0];
  const to = [255, 241, 224];
  const c = from.map((f, i) => Math.round(f + (to[i] - f) * t));
  return { bg: `rgb(${c.join(',')})`, text: t < 0.45 ? '#fff' : '#3d2611' };
}

function renderRankGrid() {
  const table = document.getElementById('rankGrid');
  const total = TEAMS.length;
  const perWeek = Array.from({ length: weekCount }, (_, i) => rankAt(i + 1));

  // Sort rows by the most recent standings
  const latest = perWeek[weekCount - 1];
  const rowOrder = [...TEAMS].sort((a, b) => latest[a.name] - latest[b.name]);

  const header = `<tr><th class="team-col">Team</th>${weekLabels
    .map(label => `<th>${label.replace('Wk ', 'W')}</th>`).join('')}</tr>`;

  const body = rowOrder.map(t => {
    const cells = perWeek.map(ranks => {
      const rank = ranks[t.name];
      const { bg, text } = heatColor(rank, total);
      return `<td style="background:${bg};color:${text}">${rank}</td>`;
    }).join('');
    return `<tr><td class="team-col">${t.name}</td>${cells}</tr>`;
  }).join('');

  table.innerHTML = `<thead>${header}</thead><tbody>${body}</tbody>`;
}

renderRankGrid();