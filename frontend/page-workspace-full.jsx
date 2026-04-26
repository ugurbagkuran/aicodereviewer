// Workspace — active state (code loaded, 3-panel IDE)
// Left: file tree · Center: code + findings · Right: agent chat · Bottom: terminal/logs

const WorkspaceFullPage = () => {
  const [activeFile, setActiveFile] = React.useState('auth/jwt.py');

  const files = [
    { n: 'backend', type: 'folder', open: true, children: [
      { n: 'auth', type: 'folder', open: true, children: [
        { n: 'jwt.py', type: 'file', badge: 'warn' },
        { n: 'router.py', type: 'file' },
        { n: 'service.py', type: 'file' },
      ]},
      { n: 'containers', type: 'folder', open: true, children: [
        { n: 'service.py', type: 'file', badge: 'err' },
      ]},
      { n: 'agent', type: 'folder', children: [] },
      { n: 'main.py', type: 'file' },
      { n: 'requirements.txt', type: 'file' },
    ]},
    { n: 'frontend', type: 'folder', children: [] },
    { n: 'README.md', type: 'file' },
  ];

  const code = [
    { n: 38, t: 'def verify_refresh_token(token: str) -> User | None:' },
    { n: 39, t: '    """Verify a refresh token and return the associated user."""' },
    { n: 40, t: '    try:' },
    { n: 41, t: '        payload = jwt.decode(token, SECRET, algorithms=["HS256"])' },
    { n: 42, t: '    except JWTError:', highlight: 'warn' },
    { n: 43, t: '        return None' },
    { n: 44, t: '    return await users.find_one({"_id": payload["sub"]})' },
    { n: 45, t: '' },
    { n: 46, t: '# TODO: add revocation check against refresh_tokens collection', comment: true },
    { n: 47, t: '' },
    { n: 48, t: 'async def issue_tokens(user: User) -> TokenPair:' },
    { n: 49, t: '    access  = jwt.encode({"sub": user.id, "exp": now()+ACCESS_TTL}, SECRET)' },
    { n: 50, t: '    refresh = jwt.encode({"sub": user.id, "exp": now()+REFRESH_TTL}, SECRET)' },
    { n: 51, t: '    return TokenPair(access=access, refresh=refresh)' },
  ];

  const chat = [
    { who: 'user', t: 'auth/jwt.py\'deki güvenlik sorunlarını incele' },
    { who: 'agent', t: 'İki bulgu var. Önemli olan: `verify_refresh_token` refresh token\'ın revokasyon listesine bakmıyor. Kullanıcı çıkış yapsa bile token geçerli kalıyor.', findings: [
      { sev: 'warn', file: 'auth/jwt.py:42', msg: 'Missing revocation check' },
      { sev: 'info', file: 'auth/jwt.py:50', msg: 'HS256 yerine RS256 düşünülebilir' },
    ]},
    { who: 'agent', t: 'Yamayı hazırladım — refresh_tokens koleksiyonunda `revoked: true` olanları reddediyor. Uygulamamı istersen PR açabilirim.', action: true },
  ];

  const logs = [
    { c: APP.accent, t: '→ agent: analyzing auth/jwt.py' },
    { c: APP.faint, t: '→ planner: 3 dependencies resolved' },
    { c: APP.faint, t: '→ action: reading file (142 lines)' },
    { c: APP.warn, t: '[warn] line 42 · missing revocation path' },
    { c: APP.accent, t: '[ ok ] patch proposed · -3 / +11' },
    { c: APP.faint, t: '→ observer: acceptance pending' },
  ];

  return (
    <div style={{
      background: APP.bg, color: APP.fg, minHeight: '100%',
      fontFamily: APP.sans, display: 'flex', flexDirection: 'column',
    }}>
      <AppTopBar project="project-7b3a" user="seda.k">
        <Chip color={APP.accent} border={APP.accentDim}><Dot /> pod: running</Chip>
        <button style={{ ...ideBtn }}>Paylaş</button>
        <button style={{ ...ideBtn, background: APP.fg, color: APP.bg }}>PR aç →</button>
      </AppTopBar>

      {/* 3-panel */}
      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '240px 1fr 380px', minHeight: 620 }}>
        {/* FILE TREE */}
        <div style={{
          borderRight: `1px solid ${APP.line}`,
          display: 'flex', flexDirection: 'column',
          background: APP.bg,
        }}>
          <div style={{
            padding: '10px 14px', borderBottom: `1px solid ${APP.line}`,
            fontSize: 11, fontFamily: APP.mono, color: APP.faint,
            letterSpacing: '0.12em', textTransform: 'uppercase',
            display: 'flex', justifyContent: 'space-between',
          }}>
            <span>gezgin</span>
            <span>⌘P</span>
          </div>
          <div style={{ padding: '8px 0', fontFamily: APP.mono, fontSize: 13, flex: 1, overflow: 'auto' }}>
            <FileTree nodes={files} depth={0} active={activeFile} onSelect={setActiveFile} />
          </div>
          <div style={{ padding: '10px 14px', borderTop: `1px solid ${APP.line}`, fontSize: 11, fontFamily: APP.mono, color: APP.faint }}>
            142 dosya · 28.4k LOC
          </div>
        </div>

        {/* CODE + FINDINGS */}
        <div style={{ display: 'flex', flexDirection: 'column', background: APP.bg, minWidth: 0 }}>
          {/* tabs */}
          <div style={{
            display: 'flex', borderBottom: `1px solid ${APP.line}`,
            background: APP.bg, fontFamily: APP.mono, fontSize: 12,
          }}>
            {['auth/jwt.py', 'containers/service.py'].map((t, i) => (
              <div key={t} style={{
                padding: '10px 16px',
                borderRight: `1px solid ${APP.line}`,
                borderBottom: i === 0 ? `2px solid ${APP.accent}` : 'none',
                marginBottom: i === 0 ? -1 : 0,
                background: i === 0 ? APP.bg : 'transparent',
                color: i === 0 ? APP.fg : APP.dim,
                display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer',
              }}>
                <Dot color={i === 0 ? APP.warn : APP.err} size={6} glow={false} />
                {t}
                <span style={{ color: APP.faint, marginLeft: 6 }}>×</span>
              </div>
            ))}
          </div>

          {/* breadcrumb + actions */}
          <div style={{
            padding: '8px 16px', borderBottom: `1px solid ${APP.hairline}`,
            display: 'flex', justifyContent: 'space-between',
            fontFamily: APP.mono, fontSize: 11, color: APP.faint,
          }}>
            <span>backend / auth / jwt.py · python</span>
            <span>142 satır · utf-8</span>
          </div>

          {/* code */}
          <div style={{ flex: 1, overflow: 'auto', padding: '12px 0', fontFamily: APP.mono, fontSize: 13, lineHeight: 1.7 }}>
            {code.map((l) => (
              <div key={l.n} style={{
                display: 'grid', gridTemplateColumns: '52px 1fr',
                background: l.highlight === 'warn' ? 'rgba(255,200,97,0.06)' : 'transparent',
                borderLeft: l.highlight ? `2px solid ${APP.warn}` : '2px solid transparent',
                paddingLeft: 0,
              }}>
                <span style={{
                  color: APP.faint, textAlign: 'right', paddingRight: 14,
                  fontVariantNumeric: 'tabular-nums', userSelect: 'none',
                }}>{l.n}</span>
                <span style={{
                  color: l.comment ? APP.faint : APP.fg,
                  fontStyle: l.comment ? 'italic' : 'normal',
                  whiteSpace: 'pre',
                }}>
                  {l.t || '\u00a0'}
                </span>
              </div>
            ))}
          </div>

          {/* terminal/log strip */}
          <div style={{
            borderTop: `1px solid ${APP.line}`, background: APP.panel,
            maxHeight: 180, display: 'flex', flexDirection: 'column',
          }}>
            <div style={{
              padding: '8px 16px', borderBottom: `1px solid ${APP.line}`,
              display: 'flex', gap: 20, fontFamily: APP.mono, fontSize: 11,
              color: APP.faint, letterSpacing: '0.1em', textTransform: 'uppercase',
            }}>
              <span style={{ color: APP.fg, borderBottom: `1px solid ${APP.accent}`, paddingBottom: 6, marginBottom: -9 }}>agent logs</span>
              <span>terminal</span>
              <span>problems <Chip style={{ marginLeft: 6 }} color={APP.warn} border="rgba(255,200,97,0.25)">3</Chip></span>
              <span style={{ marginLeft: 'auto', color: APP.faint }}>clear</span>
            </div>
            <div style={{ padding: '10px 16px', fontFamily: APP.mono, fontSize: 12, lineHeight: 1.75, overflow: 'auto' }}>
              {logs.map((l, i) => (
                <div key={i} style={{ color: l.c }}>{l.t}</div>
              ))}
              <div style={{ color: APP.accent }}>
                $ <span style={{ animation: 'blink 1s infinite' }}>▋</span>
              </div>
            </div>
          </div>
        </div>

        {/* AGENT CHAT */}
        <div style={{
          borderLeft: `1px solid ${APP.line}`,
          background: APP.bg, display: 'flex', flexDirection: 'column', minHeight: 0,
        }}>
          <div style={{
            padding: '10px 16px', borderBottom: `1px solid ${APP.line}`,
            display: 'flex', justifyContent: 'space-between',
            fontFamily: APP.mono, fontSize: 11, color: APP.faint,
            letterSpacing: '0.12em', textTransform: 'uppercase',
          }}>
            <span><span style={{ color: APP.accent }}>◆</span> agent · gemini-2.5-pro</span>
            <span>session · 14m</span>
          </div>

          <div style={{ flex: 1, padding: 16, overflow: 'auto', display: 'flex', flexDirection: 'column', gap: 14 }}>
            {chat.map((m, i) => (
              <div key={i} style={{
                alignSelf: m.who === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '92%',
                padding: '10px 14px',
                background: m.who === 'user' ? APP.fg : APP.panelSoft,
                color: m.who === 'user' ? APP.bg : APP.fg,
                border: m.who === 'user' ? 'none' : `1px solid ${APP.line}`,
                borderRadius: 14,
                borderTopRightRadius: m.who === 'user' ? 4 : 14,
                borderTopLeftRadius: m.who === 'user' ? 14 : 4,
                fontSize: 13, lineHeight: 1.55,
              }}>
                {m.who === 'agent' && (
                  <div style={{ fontFamily: APP.mono, fontSize: 10, color: APP.accent, marginBottom: 6, letterSpacing: '0.1em' }}>
                    AGENT
                  </div>
                )}
                <div>{m.t}</div>

                {m.findings && (
                  <div style={{ marginTop: 10, display: 'flex', flexDirection: 'column', gap: 6 }}>
                    {m.findings.map((f, j) => (
                      <div key={j} style={{
                        padding: '8px 10px', background: APP.bg,
                        border: `1px solid ${APP.line}`, borderRadius: 8,
                        fontFamily: APP.mono, fontSize: 11,
                        display: 'flex', alignItems: 'center', gap: 10,
                      }}>
                        <span style={{
                          color: f.sev === 'warn' ? APP.warn : APP.dim,
                          textTransform: 'uppercase', letterSpacing: '0.08em',
                          fontSize: 10,
                        }}>{f.sev}</span>
                        <span style={{ color: APP.dim }}>{f.file}</span>
                        <span style={{ color: APP.fg, marginLeft: 'auto' }}>{f.msg}</span>
                      </div>
                    ))}
                  </div>
                )}

                {m.action && (
                  <div style={{ marginTop: 10, display: 'flex', gap: 8 }}>
                    <button style={chatBtn(true)}>Yamayı uygula</button>
                    <button style={chatBtn(false)}>Diff göster</button>
                    <button style={chatBtn(false)}>PR aç</button>
                  </div>
                )}
              </div>
            ))}

            <div style={{
              alignSelf: 'flex-start',
              fontFamily: APP.mono, fontSize: 11, color: APP.faint,
              display: 'flex', alignItems: 'center', gap: 8,
              padding: '0 4px',
            }}>
              <span style={{ display: 'flex', gap: 3 }}>
                <span style={{ width: 4, height: 4, borderRadius: '50%', background: APP.accent, animation: 'bounceDot 1.4s infinite' }} />
                <span style={{ width: 4, height: 4, borderRadius: '50%', background: APP.accent, animation: 'bounceDot 1.4s infinite .2s' }} />
                <span style={{ width: 4, height: 4, borderRadius: '50%', background: APP.accent, animation: 'bounceDot 1.4s infinite .4s' }} />
              </span>
              agent düşünüyor…
            </div>
          </div>

          {/* chat input */}
          <div style={{ padding: 12, borderTop: `1px solid ${APP.line}` }}>
            <div style={{
              padding: '10px 12px', background: APP.panelSoft,
              border: `1px solid ${APP.line}`, borderRadius: 12,
              display: 'flex', alignItems: 'center', gap: 10,
            }}>
              <span style={{ color: APP.accent, fontFamily: APP.mono, fontSize: 13 }}>›</span>
              <input
                placeholder="ajan ile konuş…"
                style={{
                  flex: 1, background: 'transparent', border: 'none', outline: 'none',
                  color: APP.fg, fontFamily: APP.sans, fontSize: 13,
                }}
              />
              <button style={{
                background: APP.fg, color: APP.bg, border: 'none',
                width: 28, height: 28, borderRadius: 8, cursor: 'pointer',
                fontSize: 13, fontWeight: 600,
              }}>↑</button>
            </div>
            <div style={{ marginTop: 6, fontSize: 10, color: APP.faint, fontFamily: APP.mono, display: 'flex', justifyContent: 'space-between' }}>
              <span>⌘K komutlar · / aksiyonlar</span>
              <span>tokens 8.2k / 64k</span>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes bounceDot {
          0%,80%,100% { transform: translateY(0); opacity: .4 }
          40% { transform: translateY(-4px); opacity: 1 }
        }
      `}</style>
    </div>
  );
};

const FileTree = ({ nodes, depth, active, onSelect }) => (
  <div>
    {nodes.map((n, i) => {
      const key = depth === 0 ? n.n : `${depth}-${n.n}-${i}`;
      if (n.type === 'folder') {
        return (
          <div key={key}>
            <div style={{
              padding: `4px 14px 4px ${14 + depth * 14}px`,
              display: 'flex', alignItems: 'center', gap: 6,
              color: APP.dim, cursor: 'pointer',
            }}>
              <span style={{ fontSize: 9, color: APP.faint }}>{n.open ? '▼' : '▶'}</span>
              <span style={{ color: APP.accent, fontSize: 12 }}>▤</span>
              {n.n}
            </div>
            {n.open && n.children && <FileTree nodes={n.children} depth={depth + 1} active={active} onSelect={onSelect} />}
          </div>
        );
      }
      const path = n.n; // simplified
      const isActive = active && active.endsWith(n.n);
      return (
        <div key={key}
          onClick={() => onSelect(n.n)}
          style={{
            padding: `4px 14px 4px ${14 + depth * 14}px`,
            display: 'flex', alignItems: 'center', gap: 6,
            color: isActive ? APP.fg : APP.dim,
            background: isActive ? 'rgba(255,255,255,0.04)' : 'transparent',
            cursor: 'pointer',
          }}>
          <span style={{ width: 9 }}/>
          <span style={{ color: APP.faint, fontSize: 11 }}>◦</span>
          <span style={{ flex: 1 }}>{n.n}</span>
          {n.badge === 'warn' && <Dot color={APP.warn} size={5} glow={false} />}
          {n.badge === 'err' && <Dot color={APP.err} size={5} glow={false} />}
        </div>
      );
    })}
  </div>
);

const ideBtn = {
  background: 'transparent', color: APP.fg, border: `1px solid ${APP.line}`,
  padding: '7px 14px', borderRadius: 8, cursor: 'pointer',
  fontFamily: APP.sans, fontSize: 13, fontWeight: 500,
};

const chatBtn = (primary) => ({
  background: primary ? APP.accent : 'transparent',
  color: primary ? APP.bg : APP.fg,
  border: primary ? 'none' : `1px solid ${APP.line}`,
  padding: '6px 12px', borderRadius: 7, cursor: 'pointer',
  fontFamily: APP.sans, fontSize: 12, fontWeight: 500,
});

window.WorkspaceFullPage = WorkspaceFullPage;
