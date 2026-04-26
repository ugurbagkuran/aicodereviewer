// Dashboard — project list (table-style rows), search + filters + stats

const DashboardPage = () => {
  const [query, setQuery] = React.useState('');
  const [filter, setFilter] = React.useState('all');
  const [sort, setSort] = React.useState('activity');

  const projects = [
    { id: 'a3f', name: 'checkout-api', lang: 'python', status: 'running',  findings: 3, lines: '28.4k', activity: '2 dk önce', pod: 'proj-a3f8', owner: 'seda.k' },
    { id: 'b71', name: 'orion-frontend', lang: 'typescript', status: 'idle',    findings: 7, lines: '42.1k', activity: '18 dk önce', pod: 'proj-b71e', owner: 'seda.k' },
    { id: 'c29', name: 'sensor-gateway', lang: 'go', status: 'running', findings: 1, lines: '9.8k',  activity: '1 s önce', pod: 'proj-c29d', owner: 'team' },
    { id: 'd14', name: 'ml-pipeline', lang: 'python', status: 'done', findings: 0, lines: '14.2k', activity: '3 s önce', pod: 'proj-d14a', owner: 'seda.k' },
    { id: 'e55', name: 'billing-core', lang: 'rust', status: 'error',   findings: 12, lines: '31.6k', activity: 'dün', pod: 'proj-e55b', owner: 'team' },
    { id: 'f92', name: 'notes-mobile', lang: 'typescript', status: 'idle', findings: 4, lines: '18.3k', activity: '2 gün önce', pod: 'proj-f92c', owner: 'seda.k' },
    { id: 'g04', name: 'auth-service', lang: 'java', status: 'done',    findings: 0, lines: '22.7k', activity: '3 gün önce', pod: 'proj-g04d', owner: 'team' },
    { id: 'h18', name: 'revu-backend', lang: 'python', status: 'running', findings: 2, lines: '38.9k', activity: '5 dk önce', pod: 'proj-h18e', owner: 'seda.k' },
  ];

  const statusColor = { running: APP.accent, idle: APP.faint, done: APP.dim, error: APP.err };
  const langColor = { python: '#4a9fff', typescript: '#6cf', go: '#7dffb3', rust: '#ff7a6e', java: '#ffc861' };

  const filtered = projects
    .filter(p => filter === 'all' || p.status === filter)
    .filter(p => !query || p.name.toLowerCase().includes(query.toLowerCase()));

  return (
    <div style={{ background: APP.bg, color: APP.fg, minHeight: '100%', fontFamily: APP.sans }}>
      <AppTopBar>
        <button style={navBtn}>Dokümanlar</button>
        <button style={navBtn}>Bildirimler</button>
      </AppTopBar>

      <div style={{ padding: '40px 32px', maxWidth: 1400, margin: '0 auto' }}>
        {/* header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'end', marginBottom: 8 }}>
          <div>
            <div style={{ fontSize: 11, color: APP.faint, textTransform: 'uppercase', letterSpacing: '0.15em', fontFamily: APP.mono, marginBottom: 10 }}>
              <span style={{ color: APP.accent }}>##</span> ~/dashboard
            </div>
            <h1 style={{ fontSize: 48, fontWeight: 400, letterSpacing: '-0.035em', lineHeight: 1, margin: 0 }}>
              Projeler.
            </h1>
          </div>
          <Magnetic strength={0.15}>
            <button style={{
              background: APP.fg, color: APP.bg, border: 'none',
              padding: '12px 18px', borderRadius: 10, cursor: 'pointer',
              fontFamily: APP.sans, fontSize: 14, fontWeight: 500,
              display: 'inline-flex', alignItems: 'center', gap: 8,
            }}>
              <span style={{ fontSize: 18, lineHeight: 1 }}>+</span>
              <TextScramble text="Yeni proje" duration={400} />
            </button>
          </Magnetic>
        </div>

        {/* metric strip */}
        <div style={{
          marginTop: 32, display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)',
          border: `1px solid ${APP.line}`, borderRadius: 12, overflow: 'hidden',
        }}>
          {[
            { l: 'aktif pod', v: 3, s: '/ 8', c: APP.accent },
            { l: 'bu hafta review', v: 142, s: '', c: APP.fg },
            { l: 'bekleyen bulgu', v: 29, s: '', c: APP.warn },
            { l: 'kota', v: 68, s: '%', c: APP.fg },
          ].map((m, i) => (
            <div key={i} style={{
              padding: '18px 22px',
              borderLeft: i > 0 ? `1px solid ${APP.line}` : 'none',
              background: APP.bg,
            }}>
              <div style={{
                fontSize: 11, color: APP.faint, fontFamily: APP.mono,
                letterSpacing: '0.12em', textTransform: 'uppercase',
              }}>{m.l}</div>
              <div style={{ fontSize: 30, fontWeight: 300, letterSpacing: '-0.03em', marginTop: 8, color: m.c }}>
                <Ticker value={m.v} />{m.s}
              </div>
            </div>
          ))}
        </div>

        {/* toolbar */}
        <div style={{
          marginTop: 32, display: 'flex', gap: 12, alignItems: 'center',
          padding: '10px 12px',
          border: `1px solid ${APP.line}`, borderRadius: 10,
          background: APP.panelSoft,
        }}>
          <span style={{ color: APP.accent, fontFamily: APP.mono, fontSize: 14, paddingLeft: 6 }}>$</span>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="grep projects… (yaz ve filtrele)"
            style={{
              flex: 1, background: 'transparent', border: 'none', outline: 'none',
              color: APP.fg, fontFamily: APP.mono, fontSize: 13,
            }}
          />
          <div style={{ display: 'flex', gap: 4 }}>
            {[['all', 'hepsi'], ['running', 'çalışan'], ['idle', 'boş'], ['done', 'tamam'], ['error', 'hata']].map(([k, v]) => (
              <button key={k} onClick={() => setFilter(k)} style={{
                padding: '6px 10px', borderRadius: 6,
                background: filter === k ? APP.bg : 'transparent',
                color: filter === k ? APP.fg : APP.dim,
                border: `1px solid ${filter === k ? APP.line : 'transparent'}`,
                cursor: 'pointer', fontFamily: APP.mono, fontSize: 12,
              }}>{v}</button>
            ))}
          </div>
          <div style={{ width: 1, height: 22, background: APP.line }} />
          <select value={sort} onChange={(e) => setSort(e.target.value)} style={{
            background: 'transparent', color: APP.dim, border: 'none',
            fontFamily: APP.mono, fontSize: 12, outline: 'none', cursor: 'pointer',
          }}>
            <option value="activity" style={{ background: APP.bg }}>sort: aktivite</option>
            <option value="name" style={{ background: APP.bg }}>sort: isim</option>
            <option value="findings" style={{ background: APP.bg }}>sort: bulgu</option>
          </select>
        </div>

        {/* table */}
        <div style={{
          marginTop: 20, border: `1px solid ${APP.line}`, borderRadius: 12,
          overflow: 'hidden', background: APP.bg,
        }}>
          {/* head */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1.8fr 0.8fr 0.7fr 0.7fr 0.9fr 1fr 36px',
            padding: '12px 20px', gap: 16,
            borderBottom: `1px solid ${APP.line}`,
            background: APP.panelSoft,
            fontSize: 11, fontFamily: APP.mono,
            color: APP.faint, letterSpacing: '0.1em', textTransform: 'uppercase',
          }}>
            <span>proje</span>
            <span>dil</span>
            <span>bulgu</span>
            <span>satır</span>
            <span>durum</span>
            <span>aktivite</span>
            <span></span>
          </div>

          {filtered.map((p, i) => (
            <div key={p.id} style={{
              display: 'grid',
              gridTemplateColumns: '1.8fr 0.8fr 0.7fr 0.7fr 0.9fr 1fr 36px',
              padding: '16px 20px', gap: 16, alignItems: 'center',
              borderBottom: i < filtered.length - 1 ? `1px solid ${APP.hairline}` : 'none',
              cursor: 'pointer', transition: 'background .15s',
            }}
            onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.02)'}
            onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}>
              <div>
                <div style={{ fontSize: 14, color: APP.fg, fontWeight: 500, letterSpacing: '-0.01em' }}>
                  {p.name}
                </div>
                <div style={{ fontSize: 11, color: APP.faint, fontFamily: APP.mono, marginTop: 3 }}>
                  {p.pod} · {p.owner}
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 7, fontSize: 12, fontFamily: APP.mono, color: APP.dim }}>
                <Dot color={langColor[p.lang]} size={6} glow={false} />
                {p.lang}
              </div>
              <div style={{ fontSize: 13, fontFamily: APP.mono, color: p.findings > 5 ? APP.warn : p.findings > 0 ? APP.fg : APP.faint }}>
                {p.findings > 0 ? `${p.findings} bulgu` : 'temiz'}
              </div>
              <div style={{ fontSize: 13, fontFamily: APP.mono, color: APP.dim, fontVariantNumeric: 'tabular-nums' }}>
                {p.lines}
              </div>
              <div>
                <Chip color={statusColor[p.status]} border={p.status === 'running' ? APP.accentDim : APP.line}>
                  <Dot color={statusColor[p.status]} size={5} glow={p.status === 'running'} />
                  {p.status}
                </Chip>
              </div>
              <div style={{ fontSize: 12, color: APP.dim, fontFamily: APP.mono }}>
                {p.activity}
              </div>
              <div style={{ color: APP.faint, fontSize: 18, textAlign: 'right' }}>→</div>
            </div>
          ))}

          {filtered.length === 0 && (
            <div style={{ padding: 40, textAlign: 'center', color: APP.faint, fontFamily: APP.mono, fontSize: 13 }}>
              → no matches. try another query.
            </div>
          )}
        </div>

        <div style={{
          marginTop: 16, display: 'flex', justifyContent: 'space-between',
          fontSize: 11, color: APP.faint, fontFamily: APP.mono,
        }}>
          <span>{filtered.length} / {projects.length} proje gösteriliyor</span>
          <span>idle pod checker: next run in 4m 12s</span>
        </div>
      </div>
    </div>
  );
};

const navBtn = {
  background: 'transparent', border: 'none', color: APP.dim,
  fontSize: 13, padding: '8px 12px', cursor: 'pointer', fontFamily: APP.sans,
};

window.DashboardPage = DashboardPage;
