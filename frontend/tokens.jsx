// Design tokens + shared UI atoms

export const APP = {
  bg: '#0a0a0a',
  bg2: '#0f1210',
  panel: '#0d0d0d',
  panelSoft: '#111313',
  fg: '#ededed',
  dim: 'rgba(237,237,237,0.62)',
  faint: 'rgba(237,237,237,0.38)',
  hairline: 'rgba(255,255,255,0.06)',
  line: 'rgba(255,255,255,0.08)',
  lineStrong: 'rgba(255,255,255,0.14)',
  accent: '#7dffb3',
  accentDim: 'rgba(125,255,179,0.12)',
  warn: '#ffc861',
  err: '#ff7a6e',
  sans: '"Inter Tight", system-ui, sans-serif',
  mono: '"JetBrains Mono", ui-monospace, monospace',
};

export const Logo = ({ size = 22, withWordmark = true, version = 'v0.3.1' }) => (
  <div style={{ display: 'inline-flex', alignItems: 'center', gap: 10 }}>
    <div style={{
      width: size, height: size, borderRadius: size * 0.27,
      background: APP.fg, color: APP.bg,
      display: 'grid', placeItems: 'center',
      fontWeight: 700, fontSize: size * 0.55, letterSpacing: '-0.04em',
      fontFamily: APP.sans,
    }}>r</div>
    {withWordmark && (
      <>
        <span style={{ fontWeight: 500, letterSpacing: '-0.02em', fontFamily: APP.sans }}>revu</span>
        {version && (
          <span style={{
            fontSize: 11, color: APP.faint, fontFamily: APP.mono,
            fontVariantNumeric: 'tabular-nums',
          }}>{version}</span>
        )}
      </>
    )}
  </div>
);

export const AppTopBar = ({ project, user = 'seda.k', children }) => (
  <div style={{
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    padding: '14px 24px',
    borderBottom: `1px solid ${APP.line}`,
    background: APP.bg,
    fontFamily: APP.sans,
    flexShrink: 0,
  }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: 18 }}>
      <Logo />
      {project && (
        <>
          <span style={{ color: APP.faint, fontFamily: APP.mono, fontSize: 13 }}>/</span>
          <span style={{ fontSize: 13, color: APP.dim, fontFamily: APP.mono }}>{user}</span>
          <span style={{ color: APP.faint, fontFamily: APP.mono, fontSize: 13 }}>/</span>
          <span style={{ fontSize: 13, color: APP.fg, fontFamily: APP.mono }}>{project}</span>
          <span style={{
            fontSize: 11, padding: '3px 8px', borderRadius: 4,
            background: APP.accentDim, color: APP.accent,
            fontFamily: APP.mono, letterSpacing: '0.05em',
          }}>● running</span>
        </>
      )}
    </div>
    <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
      {children}
      <div style={{
        width: 28, height: 28, borderRadius: '50%',
        background: 'linear-gradient(135deg, #7dffb3, #4a9fff)',
        display: 'grid', placeItems: 'center',
        color: APP.bg, fontWeight: 600, fontSize: 12,
        fontFamily: APP.sans,
      }}>S</div>
    </div>
  </div>
);

export const Chip = ({ children, color = APP.dim, bg = 'transparent', border = APP.line, mono = true, style = {} }) => (
  <span style={{
    display: 'inline-flex', alignItems: 'center', gap: 6,
    padding: '4px 9px', borderRadius: 4,
    background: bg, color, border: `1px solid ${border}`,
    fontSize: 11, fontFamily: mono ? APP.mono : APP.sans,
    letterSpacing: '0.02em',
    ...style,
  }}>{children}</span>
);

export const Dot = ({ color = APP.accent, size = 6, glow = true }) => (
  <span style={{
    display: 'inline-block', width: size, height: size, borderRadius: '50%',
    background: color, boxShadow: glow ? `0 0 8px ${color}` : 'none',
    flexShrink: 0,
  }} />
);
