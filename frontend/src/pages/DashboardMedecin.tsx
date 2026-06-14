import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Calendar, Users, Activity, CheckCircle, Clock, Plus, Brain, TrendingUp, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { analyticsAPI, consultationsAPI } from '../services/api';

interface Stats {
  total_patients: number;
  total_consultations: number;
  consultations_en_attente: number;
  consultations_en_cours: number;
  consultations_terminees: number;
  total_diagnostics: number;
  taux_approbation: number;
  confiance_moyenne: number;
}

interface Consultation {
  id: number;
  patient_id?: number;
  nom_patient: string;
  date: string;
  motif: string;
  statut: string;
}

const DashboardMedecin = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<Stats | null>(null);
  const [recentConsultations, setRecentConsultations] = useState<Consultation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [dashData, consultations] = await Promise.all([
        analyticsAPI.getDashboard(),
        analyticsAPI.getRecentConsultations(5),
      ]);
      setStats(dashData.kpis as Stats);
      setRecentConsultations(consultations);
    } catch (err: any) {
      setError(err.message || 'Erreur de connexion au backend');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const statusColors: Record<string, { bg: string; text: string; border: string }> = {
    'en attente': { bg: '#FEF3C7', text: '#92400E', border: '#FCD34D' },
    'en_attente_medecin': { bg: '#EEF2FF', text: '#4F46E5', border: '#C7D2FE' },
    'en cours':   { bg: '#DBEAFE', text: '#1E40AF', border: '#93C5FD' },
    'terminée':   { bg: '#D1FAE5', text: '#065F46', border: '#6EE7B7' },
  };

  const statusLabels: Record<string, string> = {
    'en attente': 'En attente',
    'en_attente_medecin': 'Att. médecin',
    'en cours': 'En cours',
    'terminée': 'Terminée',
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px', flexDirection: 'column', gap: '16px' }}>
        <Activity size={48} style={{ animation: 'spin 1s linear infinite', color: '#4F46E5' }} />
        <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
        <p style={{ color: '#6B7280' }}>Chargement du tableau de bord...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <AlertCircle size={48} style={{ color: '#EF4444', margin: '0 auto 16px' }} />
        <h3 style={{ color: '#1F2937', marginBottom: '8px' }}>Erreur de connexion au backend</h3>
        <p style={{ color: '#6B7280', marginBottom: '16px' }}>{error}</p>
        <button onClick={fetchData} className="sp-btn sp-btn-primary">Réessayer</button>
      </div>
    );
  }

  return (
    <>
      {/* Header */}
      <div className="sp-page-header sp-fade-in">
        <div>
          <h1 className="sp-page-title">
            Bonjour, Dr. {user?.prenoms} {user?.nom}
          </h1>
          <p className="sp-page-subtitle">
            {new Date().toLocaleDateString('fr-FR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <Link to="/consultation/nouvelle" className="sp-btn sp-btn-primary">
            <Plus size={18} /> Nouvelle consultation
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="sp-auto-grid sp-fade-in" style={{ marginBottom: '24px' }}>
        <div className="sp-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '13px', color: '#6B7280', fontWeight: 500 }}>Total patients</span>
            <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: '#EEF2FF', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Users size={18} style={{ color: '#4F46E5' }} />
            </div>
          </div>
          <div className="sp-number sp-number-lg" style={{ color: '#1F2937' }}>{stats?.total_patients ?? 0}</div>
          <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>patients enregistrés</div>
        </div>

        <div className="sp-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '13px', color: '#6B7280', fontWeight: 500 }}>En attente</span>
            <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: '#FFFBEB', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Clock size={18} style={{ color: '#F59E0B' }} />
            </div>
          </div>
          <div className="sp-number sp-number-lg" style={{ color: '#1F2937' }}>{stats?.consultations_en_attente ?? 0}</div>
          <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>consultations à traiter</div>
        </div>

        <div className="sp-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '13px', color: '#6B7280', fontWeight: 500 }}>En cours</span>
            <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: '#EFF6FF', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Activity size={18} style={{ color: '#3B82F6' }} />
            </div>
          </div>
          <div className="sp-number sp-number-lg" style={{ color: '#1F2937' }}>{stats?.consultations_en_cours ?? 0}</div>
          <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>consultations actives</div>
        </div>

        <div className="sp-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '13px', color: '#6B7280', fontWeight: 500 }}>Terminées</span>
            <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: '#F0FDF4', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <CheckCircle size={18} style={{ color: '#10B981' }} />
            </div>
          </div>
          <div className="sp-number sp-number-lg" style={{ color: '#1F2937' }}>{stats?.consultations_terminees ?? 0}</div>
          <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>consultations clôturées</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px' }} className="sp-fade-in">
        {/* Consultations récentes */}
        <div className="sp-card">
          <div className="sp-card-header">
            <div className="sp-card-title">
              <Calendar size={20} />
              Consultations récentes
            </div>
            <Link to="/consultations" className="sp-btn sp-btn-outline" style={{ fontSize: '13px', padding: '6px 14px' }}>
              Voir tout
            </Link>
          </div>
          <div style={{ padding: 0 }}>
            {recentConsultations.length === 0 ? (
              <div style={{ padding: '40px', textAlign: 'center' }}>
                <Calendar size={40} style={{ color: '#D1D5DB', margin: '0 auto 12px' }} />
                <p style={{ color: '#9CA3AF' }}>Aucune consultation récente</p>
              </div>
            ) : (
              recentConsultations.map((c, index) => {
                const colors = statusColors[c.statut] || statusColors['en attente'];
                return (
                  <div
                    key={c.id}
                    style={{
                      padding: '16px 20px',
                      borderBottom: index < recentConsultations.length - 1 ? '1px solid #F3F4F6' : 'none',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '16px',
                    }}
                  >
                    <div style={{
                      width: '40px', height: '40px', borderRadius: '10px',
                      background: 'linear-gradient(135deg, #4F46E5, #7C3AED)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      color: '#fff', fontSize: '14px', fontWeight: 700, flexShrink: 0
                    }}>
                      {c.nom_patient?.charAt(0)?.toUpperCase() ?? '?'}
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontWeight: 600, color: '#1F2937', fontSize: '14px' }}>
                        {c.patient_id ? (
                          <Link to={`/dossier-patient/${c.patient_id}`} style={{ color: '#1F2937', textDecoration: 'none' }}>
                            {c.nom_patient}
                          </Link>
                        ) : c.nom_patient}
                      </div>
                      <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '2px' }}>
                        {c.motif} · {new Date(c.date).toLocaleDateString('fr-FR')}
                      </div>
                    </div>
                    <span style={{
                      padding: '3px 10px',
                      background: colors.bg, color: colors.text,
                      borderRadius: '12px', fontSize: '11px', fontWeight: 600,
                      border: `1px solid ${colors.border}`, flexShrink: 0
                    }}>
                      {statusLabels[c.statut] || c.statut}
                    </span>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Panel IA + Stats */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Système IA */}
          <div className="sp-card" style={{ padding: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
              <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'linear-gradient(135deg, #7C3AED, #4F46E5)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Brain size={18} style={{ color: '#fff' }} />
              </div>
              <div>
                <div style={{ fontWeight: 600, color: '#1F2937', fontSize: '14px' }}>Système IA</div>
                <div style={{ fontSize: '12px', color: '#10B981' }}>● Opérationnel</div>
              </div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '13px', color: '#6B7280' }}>Diagnostics générés</span>
                <span className="sp-number sp-number-sm" style={{ color: '#1F2937' }}>{stats?.total_diagnostics ?? 0}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '13px', color: '#6B7280' }}>Taux d'approbation</span>
                <span className="sp-number sp-number-sm" style={{ color: '#10B981' }}>{stats?.taux_approbation ?? 0}%</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '13px', color: '#6B7280' }}>Confiance moyenne</span>
                <span className="sp-number sp-number-sm" style={{ color: '#4F46E5' }}>{stats?.confiance_moyenne ?? 0}%</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '13px', color: '#6B7280' }}>Maladies détectables</span>
                <span className="sp-number sp-number-sm" style={{ color: '#1F2937' }}>121</span>
              </div>
            </div>
          </div>

          {/* Actions rapides */}
          <div className="sp-card" style={{ padding: '20px' }}>
            <div style={{ fontWeight: 600, color: '#1F2937', marginBottom: '14px', fontSize: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <TrendingUp size={16} />
              Actions rapides
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <Link to="/consultation/nouvelle" className="sp-btn sp-btn-primary" style={{ justifyContent: 'center' }}>
                <Plus size={16} /> Nouvelle consultation
              </Link>
              <Link to="/mes-patients" className="sp-btn sp-btn-outline" style={{ justifyContent: 'center' }}>
                <Users size={16} /> Voir mes patients
              </Link>
              <Link to="/diagnostics" className="sp-btn sp-btn-outline" style={{ justifyContent: 'center' }}>
                <Brain size={16} /> Diagnostics IA
              </Link>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default DashboardMedecin;
