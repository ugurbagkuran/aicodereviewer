// Workspace — empty state (no code yet)
// AI chat is full-screen / centered; user picks how to bring code in.

const WorkspaceEmptyPage = () => {
  const [input, setInput] = React.useState('');
  const chat = [
    { who: 'agent', t: 'Merhaba. Ben senin code review ajanınım. Bu projeye henüz bir kod bağlanmamış.' },
    { who: 'agent', t: 'Aşağıdaki seçeneklerden birini kullanabilirsin — ya da doğrudan ne yapmak istediğini yaz.' },
  ];

  const options = [
    { icon: '◐', t: 'GitHub\'dan import et', d: 'Özel repolar için read-only token', k: 'github' },
    { icon: '◑', t: 'ZIP dosyası yükle', d: 'Lokal bir klasörü sıkıştırıp at', k: 'zip' },
    { icon: '◒', t: 'Sıfırdan başlat', d: 'Boş bir workspace, sen diktel ben yazayım', k: 'blank' },
    { icon: '◓', t: 'Bir URL yapıştır', d: 'GitHub, GitLab, ya da raw link', k: 'url' },
  ];

  return (
    <div style={{
      background: APP.bg, color: APP.fg, minHeight: '100%',
      fontFamily: APP.sans, display: 'flex', flexDirection: 'column',
    }}>
      <AppTopBar project="project-7b3a" user="seda.k">
        <Chip color={APP.dim}>pod: idle</Chip>
        <button style={{ ...navBtn2 }}>Ayarlar</button>
      </AppTopBar>

      {/* center stage */}
      <div style={{
        flex: 1, display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center',
        padding: '40px 32px', position: 'relative',
      }}>
        {/* ambient grid */}
        <div style={{
          position: 'absolute', inset: 0, pointerEvents: 'none',
          backgroundImage: `linear-gradient(${APP.line} 1px, transparent 1px), linear-gradient(90deg, ${APP.line} 1px, transparent 1px)`,
          backgroundSize: '60px 60px',
          maskImage: 'radial-gradient(ellipse at center, black 10%, transparent 65%)',
          WebkitMaskImage: 'radial-gradient(ellipse at center, black 10%, transparent 65%)',
        }} />

        <div style={{ position: 'relative', width: '100%', maxWidth: 760 }}>
          {/* header */}
          <div style={{ textAlign: 'center', marginBottom: 40 }}>
            <div style={{
              display: 'inline-flex', alignItems: 'center', gap: 10,
              padding: '7px 14px', borderRadius: 999,
              background: APP.accentDim, border: `1px solid ${APP.accentDim}`,
              fontSize: 11, color: APP.accent, fontFamily: APP.mono,
              letterSpacing: '0.1em', textTransform: 'uppercase',
              marginBottom: 24,
            }}>
              <Dot /> agent ready · project-7b3a · pod awaiting code
            </div>
            <h1 style={{
              fontSize: 'clamp(36px, 4.5vw, 56px)', fontWeight: 400,
              letterSpacing: '-0.035em', lineHeight: 1.05, margin: 0,
              textWrap: 'balance',
            }}>
              Kodunu nasıl{' '}
              <span style={{ fontStyle: 'italic', fontWeight: 300, opacity: 0.7 }}>
                getirmek
              </span>{' '}
              istersin?
            </h1>
            <p style={{ marginTop: 16, fontSize: 15, color: APP.dim, lineHeight: 1.55, maxWidth: 520, margin: '16px auto 0' }}>
              Ajan izole bir pod&apos;da seni bekliyor. Bir kaynak seç — ya da doğrudan ne yapmak istediğini anlat.
            </p>
          </div>

          {/* chat bubbles */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginBottom: 24 }}>
            {chat.map((m, i) => (
              <div key={i} style={{
                maxWidth: 560, padding: '12px 16px',
                background: APP.panelSoft, border: `1px solid ${APP.line}`,
                borderRadius: 14, borderTopLeftRadius: 4,
                fontSize: 14, color: APP.dim, lineHeight: 1.55,
                display: 'flex', gap: 10,
              }}>
                <span style={{ color: APP.accent, fontFamily: APP.mono, fontSize: 12 }}>◆</span>
                <span>{m.t}</span>
              </div>
            ))}
          </div>

          {/* option cards */}
          <div style={{
            display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 12,
            marginBottom: 28,
          }}>
            {options.map((o, i) => (
              <button key={o.k} style={{
                padding: 18, textAlign: 'left',
                background: APP.panelSoft, border: `1px solid ${APP.line}`,
                borderRadius: 12, cursor: 'pointer',
                color: APP.fg, fontFamily: APP.sans,
                display: 'flex', gap: 14, alignItems: 'flex-start',
                transition: 'all .2s',
              }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = APP.lineStrong; e.currentTarget.style.background = '#141414'; }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = APP.line; e.currentTarget.style.background = APP.panelSoft; }}>
                <span style={{
                  width: 34, height: 34, borderRadius: 8,
                  background: APP.bg, display: 'grid', placeItems: 'center',
                  color: APP.accent, fontSize: 18, flexShrink: 0,
                  border: `1px solid ${APP.line}`,
                }}>{o.icon}</span>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 14, fontWeight: 500 }}>{o.t}</div>
                  <div style={{ fontSize: 12, color: APP.faint, marginTop: 4, fontFamily: APP.mono }}>
                    {o.d}
                  </div>
                </div>
                <span style={{ color: APP.faint, fontSize: 14 }}>→</span>
              </button>
            ))}
          </div>

          {/* prompt bar */}
          <div style={{
            padding: '14px 16px',
            background: APP.panelSoft,
            border: `1px solid ${APP.line}`,
            borderRadius: 14,
            display: 'flex', alignItems: 'center', gap: 12,
            boxShadow: '0 20px 60px rgba(0,0,0,0.4)',
          }}>
            <span style={{ color: APP.accent, fontFamily: APP.mono, fontSize: 14 }}>$</span>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="ya da ajan ile konuş: “React projemi import et ve auth akışını incele”"
              style={{
                flex: 1, background: 'transparent', border: 'none', outline: 'none',
                color: APP.fg, fontFamily: APP.sans, fontSize: 14,
              }}
            />
            <Chip mono>⌘ ↵</Chip>
            <Magnetic strength={0.2}>
              <button style={{
                background: APP.fg, color: APP.bg, border: 'none',
                width: 34, height: 34, borderRadius: 10, cursor: 'pointer',
                fontSize: 14, fontWeight: 600,
              }}>↑</button>
            </Magnetic>
          </div>
          <div style={{
            marginTop: 10, fontSize: 11, color: APP.faint,
            fontFamily: APP.mono, display: 'flex', justifyContent: 'space-between',
          }}>
            <span>model: gemini-2.5-pro</span>
            <span>klasörü bu pencereye sürükleyebilirsin</span>
          </div>
        </div>
      </div>

      {/* bottom status */}
      <div style={{
        display: 'flex', justifyContent: 'space-between',
        padding: '10px 24px', borderTop: `1px solid ${APP.line}`,
        fontSize: 11, fontFamily: APP.mono, color: APP.faint,
      }}>
        <span><Dot /> pod: standby · namespace project-7b3a</span>
        <span>context: 0 files · 0 LOC</span>
        <span>latency: 142ms · us-east-1</span>
      </div>
    </div>
  );
};

const navBtn2 = {
  background: 'transparent', border: 'none', color: APP.dim,
  fontSize: 13, padding: '8px 12px', cursor: 'pointer', fontFamily: APP.sans,
};

window.WorkspaceEmptyPage = WorkspaceEmptyPage;
