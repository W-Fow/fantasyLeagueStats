/* ==========================================================
   Stats page. Reads LEAGUE_DATA from data.js (fetch_data.py).
   ========================================================== */
const TEAMS = LEAGUE_DATA.teams;
const N = TEAMS.length;

// Fallback colors, used only if a team isn't in keys.py's get_team_colors()
const COLORS = ['#d35400','#e63946','#2a9d8f','#f4a261','#6a4c93',
                '#43aa8b','#f9c74f','#577590','#d62828','#8ac926',
                '#ff8fab','#264653'];
const TEAM_COLORS = LEAGUE_DATA.colors || {};
const teamColor = name => {
  const i = TEAMS.findIndex(t => t.name === name);
  return TEAM_COLORS[name] || COLORS[i % COLORS.length];
};

Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
Chart.defaults.font.size = 12;

const weekCount = LEAGUE_DATA.completed_weeks;

/* ---------- Expected wins ---------- */
// For each week: teams beaten + 0.5 * teams tied, divided by (N - 1). Summed over weeks.
function expectedWinsByTeam() {
  const out = {};
  TEAMS.forEach(t => { out[t.name] = 0; });

  for (let w = 0; w < weekCount; w++) {
    TEAMS.forEach(t => {
      const score = t.weekly[w];
      let beat = 0, tied = 0;
      TEAMS.forEach(other => {
        if (other === t) return;
        const s = other.weekly[w];
        if (score > s) beat++;
        else if (score === s) tied++;
      });
      out[t.name] += (beat + 0.5 * tied) / (N - 1);
    });
  }
  return out;
}

// Actual wins from real matchups (ties count 0.5, matching the expected-wins rule)
function actualWinsByTeam() {
  const out = {};
  TEAMS.forEach(t => { out[t.name] = 0; });
  LEAGUE_DATA.matchups.forEach(m => {
    if (m.home_score > m.away_score) out[m.home] += 1;
    else if (m.away_score > m.home_score) out[m.away] += 1;
    else { out[m.home] += 0.5; out[m.away] += 0.5; }
  });
  return out;
}

const expected = expectedWinsByTeam();
const actual = actualWinsByTeam();

const rows = TEAMS.map(t => ({
  name: t.name,
  actual: actual[t.name],
  expected: expected[t.name],
  luck: actual[t.name] - expected[t.name]
}));

/* ---------- Table (sorted by expected wins) ---------- */
const byExpected = [...rows].sort((a, b) => b.expected - a.expected);

const fmtLuck = v => {
  const txt = (v > 0 ? '+' : '') + v.toFixed(2);
  const cls = v > 0.005 ? 'luck-pos' : v < -0.005 ? 'luck-neg' : '';
  return `<span class="${cls}">${txt}</span>`;
};

document.getElementById('expectedTable').innerHTML = `
  <thead>
    <tr><th>#</th><th>Team</th><th>Actual W</th><th>Expected W</th><th>Luck</th></tr>
  </thead>
  <tbody>
    ${byExpected.map((r, i) => `
      <tr>
        <td>${i + 1}</td>
        <td class="team-name">${r.name}</td>
        <td>${r.actual % 1 ? r.actual.toFixed(1) : r.actual}</td>
        <td>${r.expected.toFixed(2)}</td>
        <td>${fmtLuck(r.luck)}</td>
      </tr>`).join('')}
  </tbody>`;

/* ---------- Luck chart (sorted luckiest to unluckiest) ---------- */
const byLuck = [...rows].sort((a, b) => b.luck - a.luck);

new Chart(document.getElementById('luckChart'), {
  type: 'bar',
  data: {
    labels: byLuck.map(r => r.name),
    datasets: [{
      data: byLuck.map(r => +r.luck.toFixed(2)),
      backgroundColor: byLuck.map(r => teamColor(r.name)),
      borderRadius: 4
    }]
  },
  options: {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: { x: { title: { display: true, text: 'Actual wins minus expected wins' } } }
  }
});

/* ---------- Actual vs expected ---------- */
new Chart(document.getElementById('winsChart'), {
  type: 'bar',
  data: {
    labels: byExpected.map(r => r.name),
    datasets: [
      { label: 'Expected', data: byExpected.map(r => +r.expected.toFixed(2)), backgroundColor: '#f0b98a', borderRadius: 4 },
      { label: 'Actual', data: byExpected.map(r => r.actual), backgroundColor: '#d35400', borderRadius: 4 }
    ]
  },
  options: {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { position: 'bottom', labels: { boxWidth: 12 } } },
    scales: { x: { beginAtZero: true } }
  }
});