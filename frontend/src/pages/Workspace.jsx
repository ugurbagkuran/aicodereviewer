import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ChevronLeft, Send, Play, FileCode, Bot, TerminalSquare } from 'lucide-react';

export default function Workspace() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [message, setMessage] = useState('');
  const [chatLog, setChatLog] = useState([
    { role: 'ai', content: 'Merhaba! Ben AI Kod İnceleme asistanınızım. Size nasıl yardımcı olabilirim?' }
  ]);

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!message.trim()) return;
    
    setChatLog([...chatLog, { role: 'user', content: message }]);
    setMessage('');
    
    // AI yanıt simülasyonu (İleride WebSocket ile Backend'den gelecek)
    setTimeout(() => {
      setChatLog(prev => [...prev, { role: 'ai', content: 'Şu an yapım aşamasındayım, backend WebSocket ile bağlanınca size gerçek cevaplar vereceğim!' }]);
    }, 1000);
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
      
      {/* Navbar */}
      <header style={{ 
        height: '60px', 
        borderBottom: '1px solid var(--border-color)', 
        display: 'flex', 
        alignItems: 'center', 
        padding: '0 20px',
        backgroundColor: 'var(--bg-sidebar)',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <button 
            onClick={() => navigate('/dashboard')} 
            style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', display: 'flex', alignItems: 'center' }}
          >
            <ChevronLeft size={20} /> Geri
          </button>
          <div style={{ width: '1px', height: '24px', backgroundColor: 'var(--border-color)' }}></div>
          <h2 style={{ fontSize: '1rem', fontWeight: '500', margin: 0 }}>Proje: {projectId || 'Yeni Proje'}</h2>
        </div>
        <div>
          <button className="btn btn-primary" style={{ padding: '6px 12px', fontSize: '0.85rem' }}>
            <Play size={14} /> Çalıştır (Preview)
          </button>
        </div>
      </header>

      {/* Main Layout */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        
        {/* Sol Menü - Dosya Seçici */}
        <div style={{ 
          width: '250px', 
          borderRight: '1px solid var(--border-color)', 
          backgroundColor: 'var(--bg-sidebar)',
          padding: '15px',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <h3 style={{ fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '15px', letterSpacing: '1px' }}>
            Dosyalar
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
            <div style={{ padding: '8px', backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: '4px', display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.9rem', cursor: 'pointer' }}>
              <FileCode size={16} color="var(--primary)" /> main.py
            </div>
            <div style={{ padding: '8px', borderRadius: '4px', display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.9rem', cursor: 'pointer', color: 'var(--text-muted)' }}>
              <FileCode size={16} /> requirements.txt
            </div>
          </div>
        </div>

        {/* Orta Kısım - Kod Görüntüleyici */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', backgroundColor: '#090e17' }}>
          {/* Tab */}
          <div style={{ display: 'flex', borderBottom: '1px solid var(--border-color)', backgroundColor: 'var(--bg-sidebar)' }}>
             <div style={{ padding: '10px 20px', borderTop: '2px solid var(--primary)', backgroundColor: '#090e17', fontSize: '0.9rem' }}>
               main.py
             </div>
          </div>
          {/* Editor Area */}
          <div style={{ flex: 1, padding: '20px', overflowY: 'auto', fontFamily: 'var(--font-mono)', fontSize: '0.9rem', color: '#e2e8f0', lineHeight: '1.6' }}>
            <pre style={{ margin: 0 }}>
              <code style={{ color: '#c678dd' }}>def</code> <code style={{ color: '#61afef' }}>hello_world</code>():<br/>
              &nbsp;&nbsp;&nbsp;&nbsp;<code style={{ color: '#c678dd' }}>print</code>(<code style={{ color: '#98c379' }}>"Merhaba AI Code Reviewer!"</code>)<br/>
              <br/>
              <code style={{ color: '#7f848e', fontStyle: 'italic' }}># Yapay zeka ile bu kodu düzenleyebilirsiniz.</code>
            </pre>
          </div>
          
          {/* Terminal / Logs */}
          <div style={{ height: '200px', borderTop: '1px solid var(--border-color)', backgroundColor: 'var(--bg-sidebar)', padding: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: 'var(--text-muted)', fontSize: '0.8rem', marginBottom: '10px', textTransform: 'uppercase' }}>
              <TerminalSquare size={14} /> Terminal & Loglar
            </div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: '#98c379' }}>
              [INFO] Kapsayıcı başlatılıyor...<br/>
              [INFO] Sistem hazır.
            </div>
          </div>
        </div>

        {/* Sağ Menü - AI Agent Chat */}
        <div style={{ 
          width: '350px', 
          borderLeft: '1px solid var(--border-color)', 
          backgroundColor: 'var(--bg-sidebar)',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <div style={{ padding: '15px', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '10px' }}>
             <Bot size={20} color="var(--accent)" />
             <h3 style={{ fontSize: '1rem', margin: 0 }}>AI Asistan</h3>
          </div>
          
          {/* Sohbet Geçmişi */}
          <div style={{ flex: 1, padding: '15px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '15px' }}>
            {chatLog.map((msg, i) => (
              <div key={i} style={{ 
                alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                backgroundColor: msg.role === 'user' ? 'var(--primary)' : 'rgba(255,255,255,0.05)',
                padding: '10px 15px',
                borderRadius: '8px',
                maxWidth: '85%',
                fontSize: '0.9rem',
                border: msg.role === 'ai' ? '1px solid var(--border-color)' : 'none',
                lineHeight: '1.4'
              }}>
                {msg.content}
              </div>
            ))}
          </div>

          {/* Mesaj Gönderme Kutusu */}
          <div style={{ padding: '15px', borderTop: '1px solid var(--border-color)' }}>
            <form onSubmit={handleSendMessage} style={{ display: 'flex', gap: '10px' }}>
              <input 
                type="text" 
                className="input-field" 
                placeholder="Bir soru sorun veya kod isteyin..." 
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                style={{ padding: '10px', fontSize: '0.9rem', backgroundColor: '#0f172a' }}
              />
              <button type="submit" className="btn btn-primary" style={{ padding: '10px', borderRadius: '8px' }}>
                <Send size={18} />
              </button>
            </form>
          </div>

        </div>

      </div>

    </div>
  );
}
