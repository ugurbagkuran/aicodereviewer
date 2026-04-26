import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { APP, Logo, Dot } from '../tokens.jsx';
import { Magnetic, TextScramble } from '../shared.jsx';
import { login, register } from '../api/auth.js';

const inputStyle = {
  width: '100%', padding: '12px 14px',
  background: '#0d0d0d', border: `1px solid ${APP.line}`,
  color: APP.fg, borderRadius: 10, fontFamily: APP.sans,
  fontSize: 14, outline: 'none',
  transition: 'border-color .2s, background .2s',
};

const Field = ({ label, mono, extra, children }) => (
  <label style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
      <span style={{ fontSize: 12, color: APP.dim, fontFamily: APP.sans }}>
        {label}
        <span style={{ marginLeft: 8, fontFamily: APP.mono, color: APP.faint, fontSize: 11 }}>{mono}</span>
      </span>
      {extra}
    </div>
    {children}
  </label>
);

export default function Login() {
  const navigate = useNavigate();
  const [mode, setMode] = useState('login');
  const [email, setEmail] = useState('');
  const [pw, setPw] = useState('');
  const [pw2, setPw2] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [ok, setOk] = useState(false);
  const [error, setError] = useState('');
  const [info, setInfo] = useState('');

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    setInfo('');
    if (mode === 'register' && pw !== pw2) {
      setError('Şifreler eşleşmiyor.');
      return;
    }
    setLoading(true);
    try {
      if (mode === 'login') {
        await login(email, pw);
      } else {
        await register(name, email, pw);
        await login(email, pw);
      }
      setOk(true);
      setTimeout(() => navigate('/dashboard'), 900);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: 'grid', gridTemplateColumns: '1.1fr 1fr',
      minHeight: '100vh', width: '100%',
      background: APP.bg, color: APP.fg, fontFamily: APP.sans,
    }}>
      {/* LEFT — slogan */}
      <div style={{
        position: 'relative', padding: '32px 48px',
        display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
        borderRight: `1px solid ${APP.line}`,
        overflow: 'hidden',
      }}>
        <div style={{
          position: 'absolute', inset: 0, pointerEvents: 'none',
          backgroundImage: `linear-gradient(${APP.line} 1px, transparent 1px), linear-gradient(90deg, ${APP.line} 1px, transparent 1px)`,
          backgroundSize: '60px 60px',
          maskImage: 'radial-gradient(ellipse at 20% 40%, black 10%, transparent 70%)',
          WebkitMaskImage: 'radial-gradient(ellipse at 20% 40%, black 10%, transparent 70%)',
        }} />
        <div style={{ position: 'relative', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Logo />
          <span style={{ fontSize: 11, color: APP.faint, fontFamily: APP.mono, letterSpacing: '0.15em', textTransform: 'uppercase' }}>
            <Dot /> operational
          </span>
        </div>

        <div style={{ position: 'relative' }}>
          <div style={{
            fontSize: 11, color: APP.faint, letterSpacing: '0.15em',
            textTransform: 'uppercase', fontFamily: APP.mono, marginBottom: 20,
          }}>
            <span style={{ color: APP.accent }}>##</span> giriş
          </div>
          <h1 style={{
            fontSize: 'clamp(40px, 5vw, 72px)', fontWeight: 400,
            letterSpacing: '-0.045em', lineHeight: 0.95, margin: 0,
          }}>
            Ajanın seni<br />
            <span style={{ fontStyle: 'italic', fontWeight: 300, opacity: 0.7 }}>bekliyor</span>.
          </h1>
          <p style={{
            marginTop: 28, fontSize: 15, color: APP.dim,
            lineHeight: 1.55, maxWidth: 440,
          }}>
            İzole bir pod, kendi namespace'i, kendi belleği. Bir review
            başlatmak için sadece bir tık yeter — iz bırakmaz.
          </p>

          <div style={{
            marginTop: 36, padding: '12px 14px',
            background: APP.panelSoft, border: `1px solid ${APP.line}`, borderRadius: 8,
            fontFamily: APP.mono, fontSize: 12, color: APP.faint,
            maxWidth: 420,
          }}>
            <div style={{ color: APP.accent }}>$ revu whoami</div>
            <div>→ no session. please authenticate.</div>
            <div>→ awaiting input<span style={{ animation: 'blink 1s infinite' }}>▋</span></div>
          </div>
        </div>

        <div style={{
          position: 'relative', display: 'flex', justifyContent: 'space-between',
          fontSize: 11, color: APP.faint, fontFamily: APP.mono,
          letterSpacing: '0.12em', textTransform: 'uppercase',
        }}>
          <span>© mmxxvi revu labs</span>
          <span>istanbul · berlin · sf</span>
        </div>
      </div>

      {/* RIGHT — form */}
      <div style={{
        padding: '64px 48px', display: 'flex', flexDirection: 'column',
        justifyContent: 'center', background: APP.bg,
      }}>
        <div style={{ maxWidth: 380, width: '100%', margin: '0 auto' }}>
          {/* tabs */}
          <div style={{
            display: 'flex', gap: 4, padding: 4,
            background: APP.panelSoft, border: `1px solid ${APP.line}`,
            borderRadius: 10, marginBottom: 32,
          }}>
            {[['login', 'Giriş yap'], ['register', 'Hesap oluştur']].map(([k, v]) => (
              <button key={k} onClick={() => { setMode(k); setOk(false); }}
                style={{
                  flex: 1, padding: '10px 12px',
                  background: mode === k ? APP.bg : 'transparent',
                  color: mode === k ? APP.fg : APP.dim,
                  border: 'none', borderRadius: 7, cursor: 'pointer',
                  fontFamily: APP.sans, fontSize: 14, fontWeight: 500,
                  transition: 'all .2s',
                }}>
                {v}
              </button>
            ))}
          </div>

          {ok ? (
            <div style={{
              padding: 24, border: `1px solid ${APP.accentDim}`,
              background: 'rgba(125,255,179,0.04)', borderRadius: 12,
              fontFamily: APP.mono, fontSize: 13,
            }}>
              <div style={{ color: APP.accent, marginBottom: 8 }}>
                [ ok ] {mode === 'login' ? 'authenticated' : 'account created'}
              </div>
              <div style={{ color: APP.dim, lineHeight: 1.6 }}>
                → redirecting to ~/dashboard<span style={{ animation: 'blink 1s infinite' }}>▋</span>
              </div>
            </div>
          ) : (
            <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {mode === 'register' && (
                <Field label="Kullanıcı adı" mono="username">
                  <input value={name} onChange={(e) => setName(e.target.value)}
                    placeholder="ada_lovelace" style={inputStyle} autoComplete="username" />
                </Field>
              )}
              <Field label="E‑posta" mono="email">
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                  placeholder="sen@domain.com" style={inputStyle} autoComplete="email" />
              </Field>
              <Field
                label="Şifre" mono="password"
                extra={mode === 'login' ? (
                  <button type="button" onClick={() => setInfo('Sifre sifirlama akisi henuz aktif degil.')} style={{ fontSize: 12, color: APP.dim, textDecoration: 'none', background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}>
                    <TextScramble text="Unuttum?" duration={350} />
                  </button>
                ) : null}
              >
                <input type="password" value={pw} onChange={(e) => setPw(e.target.value)}
                  placeholder="••••••••" style={inputStyle} />
              </Field>
              {mode === 'register' && (
                <Field label="Şifre tekrar" mono="password_confirm">
                  <input type="password" value={pw2} onChange={(e) => setPw2(e.target.value)}
                    placeholder="••••••••" style={inputStyle} />
                </Field>
              )}

              {error && (
                <div style={{
                  padding: '10px 14px',
                  background: 'rgba(255,100,100,0.06)',
                  border: '1px solid rgba(255,100,100,0.25)',
                  borderRadius: 8,
                  fontFamily: APP.mono, fontSize: 12, color: '#ff7a6e',
                }}>
                  [err] {error}
                </div>
              )}
              {!error && info && (
                <div style={{
                  padding: '10px 14px',
                  background: 'rgba(125,255,179,0.06)',
                  border: '1px solid rgba(125,255,179,0.25)',
                  borderRadius: 8,
                  fontFamily: APP.mono, fontSize: 12, color: APP.accent,
                }}>
                  [info] {info}
                </div>
              )}

              <Magnetic strength={0.15}>
                <button type="submit" disabled={loading} style={{
                  width: '100%', marginTop: 8,
                  background: APP.fg, color: APP.bg, border: 'none',
                  padding: '14px 20px', borderRadius: 10,
                  fontFamily: APP.sans, fontSize: 15, fontWeight: 500,
                  cursor: loading ? 'wait' : 'pointer',
                  opacity: loading ? 0.7 : 1,
                  display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 10,
                }}>
                  {loading ? (
                    <>
                      <span style={{ animation: 'spin 1s linear infinite', display: 'inline-block' }}>◜</span>
                      <span style={{ fontFamily: APP.mono, fontSize: 13 }}>authenticating…</span>
                    </>
                  ) : (
                    <>
                      <TextScramble text={mode === 'login' ? 'Giriş yap' : 'Hesap oluştur'} duration={400} />
                      <span>→</span>
                    </>
                  )}
                </button>
              </Magnetic>

              <div style={{ display: 'flex', alignItems: 'center', gap: 12, margin: '8px 0', color: APP.faint, fontSize: 11, fontFamily: APP.mono }}>
                <div style={{ flex: 1, height: 1, background: APP.line }} />
                VEYA
                <div style={{ flex: 1, height: 1, background: APP.line }} />
              </div>

              <button type="button" onClick={() => setInfo('GitHub ile giris yakinda aktif olacak.')} style={{
                padding: '13px 20px', background: APP.panelSoft,
                border: `1px solid ${APP.line}`, color: APP.fg,
                borderRadius: 10, cursor: 'pointer', fontFamily: APP.sans,
                fontSize: 14, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10,
              }}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 0a12 12 0 00-3.8 23.4c.6.1.8-.3.8-.6v-2c-3.3.7-4-1.6-4-1.6-.5-1.4-1.3-1.8-1.3-1.8-1.1-.7.1-.7.1-.7 1.2 0 1.8 1.2 1.8 1.2 1.1 1.8 2.8 1.3 3.5 1 .1-.8.4-1.3.8-1.6-2.7-.3-5.5-1.3-5.5-6 0-1.3.5-2.4 1.2-3.2-.1-.3-.5-1.5.1-3.2 0 0 1-.3 3.3 1.2a11 11 0 016 0c2.3-1.5 3.3-1.2 3.3-1.2.6 1.7.2 2.9.1 3.2.8.8 1.2 1.9 1.2 3.2 0 4.7-2.8 5.7-5.5 6 .4.4.8 1.1.8 2.3v3.3c0 .3.2.7.8.6A12 12 0 0012 0z" />
                </svg>
                GitHub ile devam et
              </button>

              <div style={{
                marginTop: 16, fontSize: 12, color: APP.faint,
                textAlign: 'center', fontFamily: APP.mono, lineHeight: 1.6,
              }}>
                devam ederek <a href="#" style={{ color: APP.dim }}>şartlar</a> ve{' '}
                <a href="#" style={{ color: APP.dim }}>gizlilik</a> politikasını kabul etmiş olursun
              </div>
            </form>
          )}
        </div>
      </div>

      <style>{`
        @keyframes blink { 0%,49%{opacity:1} 50%,100%{opacity:0} }
        @keyframes spin { to { transform: rotate(360deg) } }
        input::placeholder { color: rgba(237,237,237,0.25); }
        input:focus { border-color: rgba(255,255,255,0.2) !important; }
      `}</style>
    </div>
  );
}
