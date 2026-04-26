// Variant HYBRID — Editorial typography × Terminal hero
// Big 9vw quiet headlines, Swiss grid, off-white accent — but the hero
// media is a live terminal window with phosphor-green CLI. Best of both.

const HybridLanding = () => {
  const heroRef = React.useRef(null);
  const [tickIdx, setTickIdx] = React.useState(0);

  const terminalLines = [
    { t: '$ revu analyze ./src --agent=strict', k: 'cmd' },
    { t: '→ isolating project in k8s namespace project-7b3a…', k: 'sys' },
    { t: '→ booting sidecar · workspace=/workspace', k: 'sys' },
    { t: '→ planner: mapping 142 files, 28.4k LOC', k: 'sys' },
    { t: '[ ok ] context built in 1.8s', k: 'ok' },
    { t: '[warn] src/auth/jwt.py:42 — missing refresh-token revocation', k: 'warn' },
    { t: '[ ok ] patch proposed · -3 / +11', k: 'ok' },
    { t: '[crit] containers/service.py:218 — exec blocklist is not a sandbox', k: 'err' },
    { t: '→ suggesting gVisor runtime class + seccomp profile', k: 'sys' },
    { t: '[done] 3 findings · acceptance pending', k: 'done' },
  ];

  React.useEffect(() => {
    const id = setInterval(() => setTickIdx((i) => (i + 1) % (terminalLines.length + 5)), 700);
    return () => clearInterval(id);
  }, []);

  const c = {
    bg: '#0a0a0a',
    fg: '#ededed',
    dim: 'rgba(237,237,237,0.6)',
    faint: 'rgba(237,237,237,0.35)',
    line: 'rgba(255,255,255,0.08)',
    lineStrong: 'rgba(255,255,255,0.14)',
    accent: '#7dffb3',
    panel: '#0f1210',
  };

  const kindColor = (k) => ({
    cmd: c.accent, sys: c.faint, ok: c.accent,
    warn: '#ffc861', err: '#ff7a6e', done: c.accent,
  }[k] || c.fg);

  const steps = [
    { n: '01', k: 'BAĞLA', cmd: 'revu connect <repo>', t: 'Repo veya klasör', d: 'GitHub\'tan bağla ya da doğrudan bir klasör sürükle. Özel repolar için read-only token yeterli.' },
    { n: '02', k: 'İZLE', cmd: 'revu agent run --stream', t: 'Canlı akış', d: 'Ajan dosyaları haritalar, bağlamı çıkarır ve adım adım incelemesini canlı olarak akıtır — ne yaptığını görürsün.' },
    { n: '03', k: 'UYGULA', cmd: 'revu patch apply', t: 'Tek tık PR', d: 'Güvenlik, performans ve stil bulguları. Her biri için önerilen yamayı tek tıkla PR\'a dönüştür.' },
  ];

  const faqs = [
    { q: 'Kodumu nasıl analiz ediyorsunuz?', a: 'Her proje için izole bir Kubernetes pod üzerinde geçici bir çalışma alanı oluşturuyoruz. Analiz bittiğinde, belirlenen sürede aktivite olmazsa pod otomatik olarak sonlandırılıyor. Kodunuz hiçbir zaman sürekli bir sunucuda saklanmıyor.' },
    { q: 'Hangi dilleri destekliyor?', a: 'Şu anda Python, TypeScript/JavaScript, Go, Rust ve Java için derinlemesine analiz sağlıyoruz. Diğer diller için genel statik incelemeler mevcut, derin destek yol haritamızda.' },
    { q: 'Verim güvende mi?', a: 'Her proje kendi Kubernetes namespace\'inde çalışır, kendi ağ politikalarına sahiptir ve diğer projelerle iletişim kuramaz. Sidecar çalıştırma katmanında komut engelleme listesi var; kalıcı disk yok.' },
    { q: 'Self-host seçeneği var mı?', a: 'Evet. Enterprise planda Helm chart ile kendi K8s kümenize kurabilirsiniz. Private VPC içinde çalışır, ağa hiç çıkmaz.' },
    { q: 'Ekip olarak kullanabilir miyiz?', a: 'Evet. Takım planında paylaşılan projeler, yorum mentionları ve SSO desteği bulunuyor. Kurumsal plan için özel VPC dağıtımı sunuyoruz.' },
    { q: 'Fiyatlandırma nasıl?', a: 'Bireysel kullanım için ücretsiz, haftada 10 gözden geçirme. Ücretli planlar aylık $12\'den başlıyor. Erken erişim sırasında tüm planlarda %50 indirim geçerli.' },
  ];

  return (
    <div style={{
      background: c.bg,
      color: c.fg,
      minHeight: '100%',
      fontFamily: '"Inter Tight", "JetBrains Sans", system-ui, sans-serif',
      letterSpacing: '-0.01em',
      fontFeatureSettings: '"ss01", "cv11"',
    }}>
      {/* NAV — editorial restraint, a hair of terminal mono */}
      <nav style={{
        position: 'sticky', top: 0, zIndex: 50,
        padding: '20px 40px',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        background: 'rgba(10,10,10,0.75)',
        backdropFilter: 'blur(16px)',
        borderBottom: `1px solid ${c.line}`,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{
            width: 22, height: 22, borderRadius: 6, background: c.fg,
            display: 'grid', placeItems: 'center', color: c.bg,
            fontWeight: 700, fontSize: 12, letterSpacing: '-0.04em',
          }}>r</div>
          <span style={{ fontWeight: 500, letterSpacing: '-0.02em' }}>revu</span>
          <span style={{
            fontSize: 11, marginLeft: 6, color: c.faint,
            fontFamily: '"JetBrains Mono", ui-monospace, monospace',
            fontVariantNumeric: 'tabular-nums',
          }}>
            v0.3.1
          </span>
        </div>
        <div style={{ display: 'flex', gap: 32, fontSize: 14, color: c.dim }}>
          {['Ürün', 'Nasıl çalışır', 'Fiyat', 'Dokümanlar'].map((x) => (
            <a key={x} href="#" style={{ color: 'inherit', textDecoration: 'none', transition: 'color .2s' }}
              onMouseEnter={(e) => e.currentTarget.style.color = c.fg}
              onMouseLeave={(e) => e.currentTarget.style.color = c.dim}>
              <TextScramble text={x} duration={400} />
            </a>
          ))}
        </div>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <button style={{
            background: 'transparent', border: 'none', color: c.fg,
            fontSize: 14, padding: '8px 14px', cursor: 'pointer', fontFamily: 'inherit',
          }}>Giriş</button>
          <Magnetic strength={0.25}>
            <button style={{
              background: c.fg, color: c.bg, border: 'none',
              fontSize: 14, padding: '9px 16px', borderRadius: 999,
              cursor: 'pointer', fontFamily: 'inherit', fontWeight: 500,
            }}>
              Dene →
            </button>
          </Magnetic>
        </div>
      </nav>

      {/* HERO */}
      <section ref={heroRef} style={{
        position: 'relative',
        padding: '60px 40px 40px',
        minHeight: 'calc(100vh - 64px)',
        display: 'flex', flexDirection: 'column',
        overflow: 'hidden',
      }}>
        {/* faint grid */}
        <div style={{
          position: 'absolute', inset: 0, pointerEvents: 'none',
          backgroundImage: `linear-gradient(${c.line} 1px, transparent 1px), linear-gradient(90deg, ${c.line} 1px, transparent 1px)`,
          backgroundSize: '60px 60px',
          maskImage: 'radial-gradient(ellipse at center, black 20%, transparent 75%)',
          WebkitMaskImage: 'radial-gradient(ellipse at center, black 20%, transparent 75%)',
        }} />
        <CursorGlow color="rgba(125,255,179,0.06)" size={500} targetRef={heroRef} />

        {/* meta row — CLI status strip */}
        <Reveal>
          <div style={{
            display: 'flex', alignItems: 'center', gap: 24, fontSize: 11,
            color: c.faint, letterSpacing: '0.12em', textTransform: 'uppercase',
            fontFamily: '"JetBrains Mono", ui-monospace, monospace',
            fontVariantNumeric: 'tabular-nums',
            paddingBottom: 20, borderBottom: `1px solid ${c.line}`,
          }}>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: c.accent, boxShadow: `0 0 8px ${c.accent}`, animation: 'pulseDot 2s ease-in-out infinite' }} />
              operational
            </span>
            <span>01 / ürün</span>
            <span>mmxxvi</span>
            <span style={{ marginLeft: 'auto' }}>istanbul · berlin · sf</span>
          </div>
        </Reveal>

        {/* headline + terminal split */}
        <div style={{ flex: 1, paddingTop: 60, position: 'relative', zIndex: 1 }}>
          <div style={{
            maxWidth: 1400, margin: '0 auto',
            display: 'grid', gridTemplateColumns: 'minmax(0, 1.1fr) minmax(0, 1fr)',
            gap: 60, alignItems: 'start',
          }}>
            {/* LEFT — editorial headline */}
            <div>
              <Reveal delay={60}>
                <h1 style={{
                  fontSize: 'clamp(52px, 8vw, 136px)',
                  fontWeight: 400,
                  lineHeight: 0.92,
                  letterSpacing: '-0.045em',
                  margin: 0,
                  textWrap: 'balance',
                }}>
                  AI, kodunu <span style={{ fontStyle: 'italic', fontWeight: 300, opacity: 0.65 }}>senin gibi</span>
                  <br />okuyor. Daha sessiz.
                </h1>
              </Reveal>

              <Reveal delay={220}>
                <p style={{
                  marginTop: 40, fontSize: 18, lineHeight: 1.5,
                  color: c.dim, maxWidth: 520,
                  textWrap: 'pretty',
                }}>
                  Her pull request için izole bir Kubernetes pod. İçinde bir
                  LangGraph ajanı: planlar, okur, inceler — pod kapanır.
                  Rev&uuml;, küçük bir ekip için büyük bir meslektaş.
                </p>
              </Reveal>

              <Reveal delay={340}>
                <div style={{ marginTop: 36, display: 'flex', flexDirection: 'column', gap: 18 }}>
                  {/* install line */}
                  <div style={{
                    display: 'flex', alignItems: 'center',
                    padding: '14px 16px', background: c.panel,
                    border: `1px solid ${c.line}`, borderRadius: 8,
                    fontFamily: '"JetBrains Mono", ui-monospace, monospace',
                    fontSize: 13, maxWidth: 420,
                  }}>
                    <span style={{ color: c.accent }}>$</span>
                    <span style={{ marginLeft: 10, color: c.fg }}>npx revu init</span>
                    <span style={{ color: c.accent, marginLeft: 2, animation: 'blink 1s infinite' }}>▋</span>
                    <span style={{ marginLeft: 'auto', color: c.faint, fontSize: 11, cursor: 'pointer' }}>⧉</span>
                  </div>
                  <div style={{ display: 'flex', gap: 10 }}>
                    <Magnetic>
                      <button style={{
                        background: c.fg, color: c.bg, border: 'none',
                        padding: '16px 24px', borderRadius: 999, cursor: 'pointer',
                        fontFamily: 'inherit', fontSize: 15, fontWeight: 500,
                        display: 'inline-flex', alignItems: 'center', gap: 10,
                      }}>
                        <TextScramble text="Ücretsiz başla" duration={500} /> →
                      </button>
                    </Magnetic>
                    <button style={{
                      background: 'transparent', color: c.fg,
                      border: `1px solid ${c.lineStrong}`,
                      padding: '16px 24px', borderRadius: 999, cursor: 'pointer',
                      fontFamily: 'inherit', fontSize: 15, fontWeight: 500,
                    }}>
                      Canlı demo
                    </button>
                  </div>
                  <div style={{
                    fontSize: 12, color: c.faint, letterSpacing: '0.02em',
                    fontFamily: '"JetBrains Mono", monospace',
                  }}>
                    kredi kartı yok · 10 ücretsiz review / hafta
                  </div>
                </div>
              </Reveal>
            </div>

            {/* RIGHT — live terminal window (hero media placeholder) */}
            <Reveal delay={180}>
              <div style={{
                background: c.panel,
                border: `1px solid ${c.line}`,
                borderRadius: 12,
                boxShadow: '0 40px 80px rgba(0,0,0,0.5), 0 0 0 1px rgba(125,255,179,0.05)',
                overflow: 'hidden',
                fontFamily: '"JetBrains Mono", ui-monospace, monospace',
              }}>
                {/* titlebar */}
                <div style={{
                  display: 'flex', alignItems: 'center',
                  padding: '10px 14px', borderBottom: `1px solid ${c.line}`,
                  fontSize: 11, color: c.faint,
                }}>
                  <span style={{ display: 'flex', gap: 6 }}>
                    <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#ff5f57' }} />
                    <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#febc2e' }} />
                    <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#28c840' }} />
                  </span>
                  <span style={{ margin: '0 auto' }}>revu — agent · project-7b3a · 142 files</span>
                  <span>⌘K</span>
                </div>
                {/* body */}
                <div style={{ padding: '18px 18px 14px', minHeight: 360, fontSize: 13, lineHeight: 1.75 }}>
                  {terminalLines.slice(0, Math.min(tickIdx + 1, terminalLines.length)).map((l, i) => (
                    <div key={i} style={{ color: kindColor(l.k), whiteSpace: 'pre-wrap' }}>
                      {l.t}
                    </div>
                  ))}
                  {tickIdx < terminalLines.length && (
                    <div style={{ display: 'inline-block', width: 8, height: 14, background: c.accent, animation: 'blink 1s infinite' }} />
                  )}
                  {tickIdx >= terminalLines.length && (
                    <div style={{ marginTop: 14, color: c.faint, fontSize: 11, fontStyle: 'italic' }}>
                      [ demo · buraya ürünün gerçek gifi gelecek — 16:9 önerilir ]
                    </div>
                  )}
                </div>
                {/* status bar */}
                <div style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  padding: '8px 14px', borderTop: `1px solid ${c.line}`,
                  fontSize: 11, color: c.faint,
                }}>
                  <span><span style={{ color: c.accent }}>●</span> agent: ready</span>
                  <span>tokens: 8.2k/64k</span>
                  <span>lat: 142ms</span>
                </div>
              </div>
            </Reveal>
          </div>
        </div>

        {/* stat strip */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          marginTop: 100,
          maxWidth: 1400,
          width: '100%',
          margin: '100px auto 0',
          borderTop: `1px solid ${c.line}`,
          borderBottom: `1px solid ${c.line}`,
        }}>
          {[
            { v: 42000, s: '+', l: 'Gözden geçirilen PR' },
            { v: 8, s: '·', l: 'Dil (derin)' },
            { v: 94, s: '%', l: 'Kabul oranı' },
            { v: 12, s: 'sn', l: 'İlk yanıt' },
          ].map((s, i) => (
            <div key={i} style={{
              padding: '28px 24px',
              borderLeft: i > 0 ? `1px solid ${c.line}` : 'none',
            }}>
              <div style={{ fontSize: 'clamp(28px, 3vw, 44px)', fontWeight: 300, letterSpacing: '-0.03em' }}>
                <Ticker value={s.v} />
                <span style={{ opacity: 0.4, marginLeft: 2 }}>{s.s}</span>
              </div>
              <div style={{
                fontSize: 11, color: c.faint, textTransform: 'uppercase',
                letterSpacing: '0.12em', marginTop: 8,
                fontFamily: '"JetBrains Mono", monospace',
              }}>
                {s.l}
              </div>
            </div>
          ))}
        </div>

        <style>{`
          @keyframes blink { 0%,49%{opacity:1} 50%,100%{opacity:0} }
          @keyframes pulseDot { 0%,100%{opacity:1} 50%{opacity:.4} }
        `}</style>
      </section>

      {/* NASIL ÇALIŞIR */}
      <section style={{ padding: '140px 40px', borderTop: `1px solid ${c.line}` }}>
        <div style={{ maxWidth: 1400, margin: '0 auto' }}>
          <Reveal>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 40, marginBottom: 80 }}>
              <div style={{
                fontSize: 11, color: c.faint, textTransform: 'uppercase',
                letterSpacing: '0.15em',
                fontFamily: '"JetBrains Mono", monospace',
              }}>
                <span style={{ color: c.accent }}>##</span> 02 / nasıl çalışır
              </div>
              <h2 style={{
                fontSize: 'clamp(36px, 5vw, 76px)',
                fontWeight: 400, letterSpacing: '-0.03em', lineHeight: 1,
                margin: 0, textWrap: 'balance',
              }}>
                Üç komut. <span style={{ opacity: 0.45 }}>Bir dakikadan az.</span>
              </h2>
            </div>
          </Reveal>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 0 }}>
            {steps.map((s, i) => (
              <Reveal key={i} delay={i * 120}>
                <div style={{
                  padding: '40px 32px',
                  borderTop: `1px solid ${c.lineStrong}`,
                  borderRight: i < 2 ? `1px solid ${c.line}` : 'none',
                  paddingLeft: i === 0 ? 0 : 40,
                  paddingRight: i === 2 ? 0 : 40,
                  minHeight: 320,
                  display: 'flex', flexDirection: 'column', gap: 18,
                }}>
                  <div style={{
                    display: 'flex', justifyContent: 'space-between',
                    fontFamily: '"JetBrains Mono", monospace',
                    fontSize: 12, color: c.faint,
                  }}>
                    <span style={{ fontVariantNumeric: 'tabular-nums' }}>{s.n}</span>
                    <span style={{ letterSpacing: '0.18em' }}>{s.k}</span>
                  </div>
                  <div style={{
                    fontFamily: '"JetBrains Mono", monospace',
                    fontSize: 12, color: c.accent,
                    padding: '8px 10px', background: c.panel,
                    border: `1px solid ${c.line}`, borderRadius: 6,
                    alignSelf: 'flex-start',
                  }}>
                    $ {s.cmd}
                  </div>
                  <h3 style={{
                    marginTop: 8, fontSize: 'clamp(24px, 2.4vw, 34px)',
                    fontWeight: 400, letterSpacing: '-0.02em', lineHeight: 1.1,
                  }}>{s.t}</h3>
                  <p style={{
                    marginTop: 'auto', fontSize: 15, lineHeight: 1.55,
                    color: c.dim, maxWidth: 320,
                  }}>{s.d}</p>
                </div>
              </Reveal>
            ))}
          </div>

          {/* marquee of tech */}
          <Reveal>
            <div style={{ marginTop: 120, borderTop: `1px solid ${c.line}`, paddingTop: 32 }}>
              <div style={{
                fontSize: 11, color: c.faint, textTransform: 'uppercase',
                letterSpacing: '0.15em', marginBottom: 24,
                fontFamily: '"JetBrains Mono", monospace',
              }}>
                <span style={{ color: c.accent }}>##</span> altyapı
              </div>
              <Marquee speed={60}>
                {['Kubernetes', 'LangGraph', 'Gemini 2.5', 'FastAPI', 'Qdrant', 'MongoDB', 'React 19', 'Vite', 'Bcrypt · JWT', 'Minikube'].map((t) => (
                  <span key={t} style={{
                    fontSize: 'clamp(24px, 3vw, 42px)',
                    fontWeight: 300, letterSpacing: '-0.02em',
                    display: 'inline-flex', alignItems: 'center', gap: 24,
                  }}>
                    {t}<span style={{ color: c.accent, opacity: 0.6 }}>◆</span>
                  </span>
                ))}
              </Marquee>
            </div>
          </Reveal>
        </div>
      </section>

      {/* SSS */}
      <section style={{ padding: '140px 40px', borderTop: `1px solid ${c.line}` }}>
        <div style={{ maxWidth: 1100, margin: '0 auto', display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 60 }}>
          <Reveal>
            <div style={{ position: 'sticky', top: 100 }}>
              <div style={{
                fontSize: 11, color: c.faint, textTransform: 'uppercase',
                letterSpacing: '0.15em', marginBottom: 16,
                fontFamily: '"JetBrains Mono", monospace',
              }}>
                <span style={{ color: c.accent }}>##</span> 03 / sss
              </div>
              <h2 style={{
                fontSize: 'clamp(32px, 3.8vw, 56px)',
                fontWeight: 400, letterSpacing: '-0.03em',
                lineHeight: 1, margin: 0, textWrap: 'balance',
              }}>
                Sık sorulan sorular.
              </h2>
              <p style={{
                marginTop: 20, fontSize: 14, color: c.dim,
                lineHeight: 1.6, maxWidth: 280,
              }}>
                Burada cevabını bulamadığın bir şey varsa{' '}
                <a href="#" style={{ color: c.fg, textDecorationColor: 'rgba(255,255,255,0.3)' }}>yaz bize</a>.
              </p>
            </div>
          </Reveal>
          <Reveal delay={120}>
            <Accordion items={faqs} accent={c.accent} />
          </Reveal>
        </div>
      </section>

      {/* FOOTER — giant wordmark */}
      <footer style={{ padding: '80px 40px 40px', borderTop: `1px solid ${c.line}` }}>
        <div style={{ maxWidth: 1400, margin: '0 auto' }}>
          <div style={{
            fontSize: 'clamp(80px, 14vw, 220px)',
            fontWeight: 300, letterSpacing: '-0.06em', lineHeight: 0.85,
            margin: 0, opacity: 0.92,
          }}>
            rev<span style={{ fontStyle: 'italic', fontWeight: 200 }}>ü</span>
            <span style={{ color: c.accent, opacity: 0.9 }}>.</span>
          </div>
          <div style={{
            marginTop: 60, display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)', gap: 32,
            paddingTop: 32, borderTop: `1px solid ${c.line}`,
          }}>
            {[
              { h: 'Ürün', items: ['Özellikler', 'Fiyat', 'Değişiklikler', 'Yol haritası'] },
              { h: 'Kaynaklar', items: ['Dokümanlar', 'API', 'Self-host', 'Blog'] },
              { h: 'Şirket', items: ['Hakkımızda', 'Kariyer', 'İletişim', 'Basın'] },
              { h: 'Yasal', items: ['Gizlilik', 'Şartlar', 'Güvenlik', 'SLA'] },
            ].map((col) => (
              <div key={col.h}>
                <div style={{
                  fontSize: 11, color: c.faint, textTransform: 'uppercase',
                  letterSpacing: '0.15em', marginBottom: 16,
                  fontFamily: '"JetBrains Mono", monospace',
                }}>{col.h}</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {col.items.map((i) => (
                    <a key={i} href="#" style={{ color: c.dim, textDecoration: 'none', fontSize: 14 }}
                      onMouseEnter={(e) => e.currentTarget.style.color = c.fg}
                      onMouseLeave={(e) => e.currentTarget.style.color = c.dim}>
                      <TextScramble text={i} duration={350} />
                    </a>
                  ))}
                </div>
              </div>
            ))}
          </div>
          <div style={{
            marginTop: 60, display: 'flex', justifyContent: 'space-between',
            fontSize: 12, color: c.faint,
            fontFamily: '"JetBrains Mono", monospace',
            fontVariantNumeric: 'tabular-nums',
          }}>
            <span>© mmxxvi · revu labs</span>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: c.accent, boxShadow: `0 0 8px ${c.accent}` }} />
              her satır, bir meslektaş
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
};

window.HybridLanding = HybridLanding;
