import React, { useState, useEffect } from 'react';
import { UserCheck, Users, Phone, Mail, Stethoscope, Activity, Search } from 'lucide-react';
import { analyticsAPI } from '../services/api';

const PersonnelMedical = () => {
  const [personnel, setPersonnel] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'medecins' | 'infirmiers'>('medecins');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchPersonnel = async () => {
      try {
        setLoading(true);
        const data = await analyticsAPI.getPersonnelDisponible();
        setPersonnel(data);
      } catch (error) {
        console.error('Erreur lors du chargement du personnel:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPersonnel();
    // Rafraîchir toutes les 60 secondes
    const interval = setInterval(fetchPersonnel, 60000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <Activity size={48} style={{ animation: 'spin 1s linear infinite', color: '#4F46E5' }} />
      </div>
    );
  }

  const medecins = personnel?.medecins?.liste || [];
  const infirmiers = personnel?.infirmiers?.liste || [];

  const filteredMedecins = medecins.filter((m: any) =>
    m.nom.toLowerCase().includes(searchTerm.toLowerCase()) ||
    m.prenoms.toLowerCase().includes(searchTerm.toLowerCase()) ||
    m.specialite.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredInfirmiers = infirmiers.filter((i: any) =>
    i.nom.toLowerCase().includes(searchTerm.toLowerCase()) ||
    i.prenoms.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <>
      <div className="sp-page-header sp-fade-in">
        <div>
          <h1 className="sp-page-title">Personnel Médical</h1>
          <p className="sp-page-subtitle">
            Gestion du personnel médical · {personnel?.medecins.total || 0} médecins · {personnel?.infirmiers.total || 0} infirmiers
          </p>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="sp-stats-grid sp-fade-in" style={{ marginBottom: '24px', gridTemplateColumns: 'repeat(4, 1fr)' }}>
        <div className="sp-stat-card" style={{'--card-accent': '#4F46E5'} as React.CSSProperties}>
          <div className="sp-stat-icon" style={{background: '#eef2ff', borderRadius: '14px', width: '54px', height: '54px'}}>
            <Stethoscope style={{color: '#4F46E5', width:'24px', height:'24px'}} />
          </div>
          <div>
            <div className="sp-stat-value" style={{ fontSize: '38px', fontWeight: 900, color: '#0f172a' }}>
              {personnel?.medecins.disponibles || 0}
            </div>
            <div className="sp-stat-label">Médecins Disponibles</div>
          </div>
        </div>

        <div className="sp-stat-card" style={{'--card-accent': '#10B981'} as React.CSSProperties}>
          <div className="sp-stat-icon" style={{background: '#d1fae5', borderRadius: '14px', width: '54px', height: '54px'}}>
            <UserCheck style={{color: '#10B981', width:'24px', height:'24px'}} />
          </div>
          <div>
            <div className="sp-stat-value" style={{ fontSize: '38px', fontWeight: 900, color: '#0f172a' }}>
              {personnel?.infirmiers.disponibles || 0}
            </div>
            <div className="sp-stat-label">Infirmiers Disponibles</div>
          </div>
        </div>

        <div className="sp-stat-card" style={{'--card-accent': '#8B5CF6'} as React.CSSProperties}>
          <div className="sp-stat-icon" style={{background: '#ede9fe', borderRadius: '14px', width: '54px', height: '54px'}}>
            <Users style={{color: '#8B5CF6', width:'24px', height:'24px'}} />
          </div>
          <div>
            <div className="sp-stat-value" style={{ fontSize: '38px', fontWeight: 900, color: '#0f172a' }}>
              {personnel?.medecins.total || 0}
            </div>
            <div className="sp-stat-label">Total Médecins</div>
          </div>
        </div>

        <div className="sp-stat-card" style={{'--card-accent': '#06B6D4'} as React.CSSProperties}>
          <div className="sp-stat-icon" style={{background: '#cffafe', borderRadius: '14px', width: '54px', height: '54px'}}>
            <Users style={{color: '#06B6D4', width:'24px', height:'24px'}} />
          </div>
          <div>
            <div className="sp-stat-value" style={{ fontSize: '38px', fontWeight: 900, color: '#0f172a' }}>
              {personnel?.infirmiers.total || 0}
            </div>
            <div className="sp-stat-label">Total Infirmiers</div>
          </div>
        </div>
      </div>

      {/* Tabs and Search */}
      <div className="sp-card sp-fade-in" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '20px' }}>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={() => setActiveTab('medecins')}
              className={`sp-btn ${activeTab === 'medecins' ? 'sp-btn-primary' : 'sp-btn-outline'}`}
            >
              <Stethoscope size={18} />
              Médecins ({medecins.length})
            </button>
            <button
              onClick={() => setActiveTab('infirmiers')}
              className={`sp-btn ${activeTab === 'infirmiers' ? 'sp-btn-primary' : 'sp-btn-outline'}`}
            >
              <UserCheck size={18} />
              Infirmiers ({infirmiers.length})
            </button>
          </div>

          <div style={{ position: 'relative', width: '300px' }}>
            <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#9CA3AF' }} />
            <input
              type="text"
              placeholder="Rechercher..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 12px 10px 40px',
                border: '1px solid #E5E7EB',
                borderRadius: '8px',
                fontSize: '14px'
              }}
            />
          </div>
        </div>
      </div>

      {/* Liste du Personnel */}
      <div className="sp-card sp-fade-in">
        <div className="sp-card-header">
          <div className="sp-card-title">
            {activeTab === 'medecins' ? <Stethoscope size={20} /> : <UserCheck size={20} />}
            {activeTab === 'medecins' ? 'Liste des Médecins' : 'Liste des Infirmiers'}
          </div>
        </div>

        <div style={{ padding: '0' }}>
          {activeTab === 'medecins' ? (
            <div style={{ display: 'grid', gap: '1px', background: '#E5E7EB' }}>
              {filteredMedecins.map((medecin: any) => (
                <div
                  key={medecin.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '20px',
                    padding: '20px',
                    background: '#fff',
                    transition: 'background 0.2s'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = '#F9FAFB'}
                  onMouseLeave={(e) => e.currentTarget.style.background = '#fff'}
                >
                  <div style={{
                    width: '56px',
                    height: '56px',
                    borderRadius: '12px',
                    background: 'linear-gradient(135deg, #4F46E5, #7C3AED)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#fff',
                    fontSize: '20px',
                    fontWeight: 700,
                    flexShrink: 0
                  }}>
                    {medecin.nom.substring(0, 1)}{medecin.prenoms.substring(0, 1)}
                  </div>

                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: '16px', color: '#1F2937', marginBottom: '4px' }}>
                      Dr. {medecin.prenoms} {medecin.nom}
                    </div>
                    <div style={{ fontSize: '14px', color: '#6B7280' }}>
                      <span style={{ 
                        display: 'inline-block',
                        padding: '2px 8px',
                        background: '#EEF2FF',
                        color: '#4F46E5',
                        borderRadius: '4px',
                        fontSize: '12px',
                        fontWeight: 600
                      }}>
                        {medecin.specialite}
                      </span>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#6B7280', fontSize: '14px' }}>
                    <Phone size={16} />
                    {medecin.telephone}
                  </div>

                  <span className="sp-badge available" style={{ fontSize: '11px' }}>
                    Disponible
                  </span>
                </div>
              ))}

              {filteredMedecins.length === 0 && (
                <div style={{ padding: '40px', textAlign: 'center', background: '#fff' }}>
                  <p style={{ color: '#9CA3AF' }}>Aucun médecin trouvé</p>
                </div>
              )}
            </div>
          ) : (
            <div style={{ display: 'grid', gap: '1px', background: '#E5E7EB' }}>
              {filteredInfirmiers.map((infirmier: any) => (
                <div
                  key={infirmier.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '20px',
                    padding: '20px',
                    background: '#fff',
                    transition: 'background 0.2s'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = '#F9FAFB'}
                  onMouseLeave={(e) => e.currentTarget.style.background = '#fff'}
                >
                  <div style={{
                    width: '56px',
                    height: '56px',
                    borderRadius: '12px',
                    background: 'linear-gradient(135deg, #10B981, #059669)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#fff',
                    fontSize: '20px',
                    fontWeight: 700,
                    flexShrink: 0
                  }}>
                    {infirmier.nom.substring(0, 1)}{infirmier.prenoms.substring(0, 1)}
                  </div>

                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: '16px', color: '#1F2937', marginBottom: '4px' }}>
                      {infirmier.prenoms} {infirmier.nom}
                    </div>
                    {infirmier.email && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#6B7280', fontSize: '13px' }}>
                        <Mail size={14} />
                        {infirmier.email}
                      </div>
                    )}
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#6B7280', fontSize: '14px' }}>
                    <Phone size={16} />
                    {infirmier.telephone}
                  </div>

                  <span className="sp-badge available" style={{ fontSize: '11px' }}>
                    Disponible
                  </span>
                </div>
              ))}

              {filteredInfirmiers.length === 0 && (
                <div style={{ padding: '40px', textAlign: 'center', background: '#fff' }}>
                  <p style={{ color: '#9CA3AF' }}>Aucun infirmier trouvé</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default PersonnelMedical;
