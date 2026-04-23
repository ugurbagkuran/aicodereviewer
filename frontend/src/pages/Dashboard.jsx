import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, GitBranch, Folder, LogOut, ArrowRight, Activity } from 'lucide-react';

export default function Dashboard() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [showNewProjectMenu, setShowNewProjectMenu] = useState(false);

  // Şimdilik sahte verilerle tasarımı yapıyoruz. İleride backend'den bağlanacak.
  useEffect(() => {
    setProjects([
      { id: '1', name: 'React E-Ticaret', status: 'active', lastUpdate: '2 saat önce' },
      { id: '2', name: 'FastAPI Backend API', status: 'idle', lastUpdate: '1 gün önce' },
      { id: '3', name: 'Python Veri Analizi', status: 'active', lastUpdate: '3 gün önce' }
    ]);
  }, []);

  return (
    <div className="animate-fade-in" style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto' }}>
      
      {/* Üst Kısım (Header) */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px' }}>
        <div>
          <h1 style={{ fontSize: '2rem' }}>Projeleriniz</h1>
          <p style={{ color: 'var(--text-muted)' }}>Çalışma alanlarınızı ve kod depolarınızı yönetin</p>
        </div>
        
        <div style={{ display: 'flex', gap: '15px' }}>
          <button 
            className="btn btn-primary"
            onClick={() => setShowNewProjectMenu(!showNewProjectMenu)}
          >
            <Plus size={18} /> Yeni Proje
          </button>
          
          <button 
            className="btn btn-outline"
            onClick={() => navigate('/login')}
          >
            <LogOut size={18} /> Çıkış Yap
          </button>
        </div>
      </header>

      {/* Yeni Proje Menüsü */}
      {showNewProjectMenu && (
        <div className="glass-panel animate-fade-in" style={{ padding: '20px', marginBottom: '40px', display: 'flex', gap: '20px' }}>
          <div style={{ flex: 1, padding: '20px', border: '1px solid var(--border-color)', borderRadius: '8px', cursor: 'pointer' }} className="btn-outline">
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '10px' }}><Folder size={20} /> Boş Proje Oluştur</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '10px' }}>Sıfırdan bir ortam başlatın ve kodlamaya hemen başlayın.</p>
          </div>
          <div style={{ flex: 1, padding: '20px', border: '1px solid var(--border-color)', borderRadius: '8px', cursor: 'pointer' }} className="btn-outline">
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '10px' }}><GitBranch size={20} /> GitHub'dan İçe Aktar</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '10px' }}>Var olan bir GitHub deposunu bağlayın ve analiz edin.</p>
          </div>
        </div>
      )}

      {/* Projeler Grid Listesi */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
        {projects.map((project) => (
          <div key={project.id} className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '15px' }}>
              <h3 style={{ fontSize: '1.2rem', margin: 0 }}>{project.name}</h3>
              <span style={{ 
                padding: '4px 8px', 
                borderRadius: '4px', 
                fontSize: '0.75rem', 
                fontWeight: '600',
                backgroundColor: project.status === 'active' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(148, 163, 184, 0.1)',
                color: project.status === 'active' ? '#10b981' : '#94a3b8',
                display: 'flex',
                alignItems: 'center',
                gap: '5px'
              }}>
                <Activity size={12} /> {project.status === 'active' ? 'Aktif' : 'Uyku Modu'}
              </span>
            </div>
            
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '30px', flex: 1 }}>
              Son güncelleme: {project.lastUpdate}
            </p>
            
            <button 
              className="btn btn-outline" 
              style={{ width: '100%', justifyContent: 'space-between' }}
              onClick={() => navigate(`/workspace/${project.id}`)}
            >
              Çalışma Alanını Aç <ArrowRight size={16} />
            </button>
          </div>
        ))}
      </div>

    </div>
  );
}
