import React, { useState, useEffect } from 'react';
import { Calendar, Activity, UserCheck, Sun, List, PlusCircle, Inbox, PieChart, Brain, AlertCircle, RefreshCw } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale } from 'chart.js';
import { analyticsAPI, healthAPI } from '../services/api';
import type { DashboardStats, Consultation } from '../services/api';
import { useAuth } from '../context/AuthContext';
import WorldMapCard from '../components/WorldMapCard';


ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale);

// Custom hook for counter animation
const useCounter = (target: number, duration: number = 1500) => {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let frame = 0;
    const frameRate = 1000 / 60;
    const totalFrames = Math.round(duration / frameRate);
    
    const animate = () => {
      frame++;
      const progress = frame / totalFrames;
      const currentCount = Math.round(target * (progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress)));
      setCount(currentCount);
      
      if (frame < totalFrames) {
        requestAnimationFrame(animate);
      } else {
        setCount(target);
      }
    };
    
    requestAnimationFrame(animate);
  }, [target, duration]);

  return count;
};

const StatCard = ({ label, value, total, icon: Icon, accent, bgIcon, colorIcon }: { label: string, value: number, total?: number, icon: any, accent: string, bgIcon: string, colorIcon: string }) => {
  const displayValue = useCounter(value);
  const displayTotal = total !== undefined ? useCounter(total) : null;
  
  return (
    <div className="sp-stat-card" style={{'--card-accent': accent} as React.CSSProperties}>
        <div className="sp-stat-icon" style={{background: bgIcon, borderRadius: '14px', width: '54px', height: '54px'}}>
            <Icon style={{color: colorIcon, width:'24px', height:'24px'}} />
        </div>
        <div>
            <div className="sp-stat-value" style={{ display: 'flex', alignItems: 'baseline', color: '#292929' }}>
                <span className="sp-number sp-number-xl">{displayValue}</span>
                {total !== undefined && (
                  <span className="sp-number sp-number-lg" style={{ color: '#94a3b8', marginLeft: '4px' }}>
                    / {displayTotal}
                  </span>
                )}
            </div>
            <div className="sp-stat-label" style={{ fontWeight: 700, fontSize: '10px', letterSpacing: '0.08em', marginTop: '1px' }}>{label}</div>
        </div>
    </div>
  );
};

const CenteredCounter = ({ value }: { value: number }) => {
  const displayValue = useCounter(value);
  return (
    <div className="sp-number sp-number-lg" style={{color: '#64748B'}}>
        {displayValue}
    </div>
  );
};

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentConsultations, setRecentConsultations] = useState<Consultation[]>([]);
  const [personnel, setPersonnel] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modelInfo, setModelInfo] = useState<{ loaded: boolean } | null>(null);
  const fetchData = async () => {
    try {
      setLoading(true);
      const [dashboardData, consultationsData, healthData, personnelData] = await Promise.all([
        analyticsAPI.getDashboard(),
        analyticsAPI.getRecentConsultations(6),
        healthAPI.check(),
        analyticsAPI.getPersonnelDisponible(),
      ]);
      setStats(dashboardData);
      setRecentConsultations(consultationsData);
      setModelInfo({ loaded: healthData.model_loaded });
      setPersonnel(personnelData);
      setError(null);
    } catch (err) {
      console.error('Erreur lors du chargement des données:', err);
      setError('Impossible de charger les données du dashboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Pas de rafraîchissement automatique - l'utilisateur peut utiliser le bouton de rafraîchissement manuel
  }, []);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <div style={{ textAlign: 'center' }}>
          <Activity size={48} style={{ animation: 'spin 1s linear infinite', color: '#4F46E5' }} />
          <p style={{ marginTop: '16px', color: '#6B7280' }}>Chargement des données...</p>
          <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
        </div>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <AlertCircle size={48} style={{ color: '#EF4444', margin: '0 auto' }} />
        <h3 style={{ marginTop: '16px', color: '#1F2937' }}>Erreur de connexion au backend</h3>
        <p style={{ color: '#6B7280', marginTop: '8px' }}>{error || 'Données non disponibles'}</p>
        <p style={{ color: '#9CA3AF', marginTop: '4px', fontSize: '14px' }}>
          Assurez-vous que le serveur backend est démarré sur http://localhost:8000
        </p>
        <button 
          onClick={() => window.location.reload()} 
          style={{ 
            marginTop: '16px', 
            padding: '8px 16px', 
            background: '#4F46E5', 
            color: 'white', 
            border: 'none', 
            borderRadius: '6px', 
            cursor: 'pointer' 
          }}
        >
          Réessayer
        </button>
      </div>
    );
  }

  const statsData = {
    totalConsultations: stats.kpis.total_consultations,
    enAttente: stats.kpis.consultations_en_attente || 0,
    enAttenteMedecin: stats.kpis.consultations_en_attente_medecin || 0,
    enCours: stats.kpis.consultations_en_cours || 0,
    terminees: stats.kpis.consultations_terminees || 0,
    medecinsDispo: personnel?.medecins.disponibles || 0,
    totalMedecins: personnel?.medecins.total || 0,
    infirmiersDispo: personnel?.infirmiers.disponibles || 0,
    totalInfirmiers: personnel?.infirmiers.total || 0,
    consultationsJour: stats.kpis.consultations_aujourd_hui || 0,
    totalPatients: stats.kpis.total_patients,
    diagnosticsIA: stats.kpis.total_diagnostics,
    diagnosticsApprouves: stats.kpis.diagnostics_approuves || 0,
    diagnosticsRejetes: stats.kpis.diagnostics_rejetes || 0,
    tauxApprobation: stats.kpis.taux_approbation
  };

  const totalStatsCount = statsData.totalConsultations + statsData.enAttente + statsData.enAttenteMedecin + statsData.enCours + statsData.consultationsJour + statsData.totalPatients + statsData.diagnosticsIA;

  const chartData = {
    labels: ['Total Consultations', 'En attente', 'Attente médecin', 'En cours', 'Aujourd\'hui', 'Total Patients', 'Diagnostics IA', 'IA Approuvés'],
    datasets: [{
      data: totalStatsCount === 0 ? [1, 1] : [
        statsData.totalConsultations, 
        statsData.enAttente,
        statsData.enAttenteMedecin,
        statsData.enCours, 
        statsData.consultationsJour, 
        statsData.totalPatients,
        statsData.diagnosticsIA,
        statsData.diagnosticsApprouves
      ],
      backgroundColor: totalStatsCount === 0 ? ['#4a4a4a', '#4a4a4a'] : ['#0A4B8C', '#F59E0B', '#FFFFFF', '#3B82F6', '#EC4899', '#8B5CF6', '#6366F1', '#10B981'],
      borderWidth: totalStatsCount === 0 ? 12 : 4,
      borderColor: '#242424',
      borderRadius: 10
    }]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '75%',
    animation: {
      duration: 2500,
      easing: 'easeInOutQuart' as const,
      animateRotate: true
    },
    plugins: {
      legend: {
        display: totalStatsCount > 0,
        position: 'bottom' as const,
        labels: {
          color: '#94a3b8',
          font: { family: "'DM Sans', sans-serif", size: 10 },
          padding: 10,
          boxWidth: 12
        },
        onHover: (event: any) => {
          if (event.native && event.native.target) {
            event.native.target.style.cursor = 'pointer';
          }
        },
        onLeave: (event: any) => {
          if (event.native && event.native.target) {
            event.native.target.style.cursor = 'default';
          }
        }
      },
      tooltip: { enabled: totalStatsCount > 0 }
    }
  };

  return (
    <>
      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
      <div className="sp-page-header sp-fade-in">
          <div>
              <h1 className="sp-page-title">Tableau de bord</h1>
              <p className="sp-page-subtitle">Vue d'ensemble du système GASA SAD · Système IA {modelInfo?.loaded ? '✓' : '✗'}</p>
          </div>
          <div style={{display:'flex',gap:'10px',alignItems:'center'}}>
              <button 
                onClick={fetchData} 
                className="sp-btn sp-btn-outline"
                disabled={loading}
                title="Rafraîchir les données"
              >
                  <RefreshCw size={18} style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} /> 
                  Rafraîchir
              </button>
              {(user?.role === 'medecin' || user?.role === 'infirmier') && (
                <Link to="/consultation/nouvelle" className="sp-btn sp-btn-primary">
                    <PlusCircle size={18} /> Nouvelle consultation
                </Link>
              )}
          </div>
      </div>

      {/* Stats Grid — toutes les cartes sur une seule ligne */}
      <div className="sp-stats-grid sp-fade-in" style={{ marginBottom: '20px', gridTemplateColumns: 'repeat(5, 1fr)' }}>
          <StatCard label="Total Patients" value={statsData.totalPatients} icon={UserCheck} accent="#8B5CF6" bgIcon="#ede9fe" colorIcon="#7C3AED" />
          <StatCard label="Total Consultations" value={statsData.totalConsultations} icon={Calendar} accent="var(--sp-primary)" bgIcon="#dbeafe" colorIcon="var(--sp-primary)" />
          <StatCard label="Aujourd'hui" value={statsData.consultationsJour} icon={Sun} accent="#EC4899" bgIcon="#fce7f3" colorIcon="#DB2777" />
          <StatCard label="En Attente" value={statsData.enAttente} icon={Activity} accent="#3B82F6" bgIcon="#eff6ff" colorIcon="#2563EB" />
          <StatCard label="Diagnostics IA" value={statsData.diagnosticsIA} icon={Brain} accent="#6366F1" bgIcon="#eef2ff" colorIcon="#6366F1" />
      </div>

      {/* Première ligne : Carte du monde (répartition par continent) + Vue d'ensemble */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px', alignItems: 'stretch' }} className="sp-fade-in">
          {/* Carte du monde — répartition des diagnostics par continent */}
          <WorldMapCard />

          {/* Graphique des données */}
          <div className="sp-card" style={{backgroundColor: '#242424', border: 'none'}}>
              <div className="sp-card-header" style={{borderBottom: '1px solid #333'}}>
                  <div className="sp-card-title" style={{color: '#fff'}}>
                      <PieChart size={20} style={{color: '#60a5fa'}} />
                      Vue d'ensemble
                  </div>
              </div>
              <div style={{padding: '20px', display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
                  <div style={{width: '100%', height: '360px', position: 'relative'}}>
                      <Doughnut data={chartData} options={chartOptions} />

                      <div style={{position: 'absolute', top: '40%', left: '50%', transform: 'translate(-50%, -50%)', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', pointerEvents: 'none'}}>
                          <CenteredCounter value={statsData.totalConsultations} />
                          <div style={{fontSize: '14px', color: '#64748B', fontFamily: "'DM Sans', sans-serif", marginTop: '4px'}}>
                              Consultations
                          </div>
                      </div>
                  </div>
              </div>
          </div>
      </div>

      {/* Deuxième ligne : Consultations récentes */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '20px' }} className="sp-fade-in">
          {/* Consultations récentes */}
          <div className="sp-card">
              <div className="sp-card-header">
                <div className="sp-card-title">
                  <List size={20} />
                  Consultations récentes
                </div>
                <Link to="/consultations" className="sp-btn sp-btn-outline sp-btn-sm">Voir tout</Link>
              </div>
              <div>
                {recentConsultations.map(row => {
                  const sc: Record<string, string> = { 'en attente': 'attente', 'en cours': 'cours', 'terminée': 'terminee', 'en_attente_medecin': 'attente' };
                  const cls = sc[row.statut] || 'attente';
                  const statutLabel: Record<string, string> = { 'en attente': 'En attente', 'en cours': 'En cours', 'terminée': 'Terminée', 'en_attente_medecin': 'Att. médecin' };
                  const parts = row.nom_patient.trim().split(/\s+/);
                  const initials = parts.length >= 2
                    ? `${parts[0].charAt(0)}${parts[1].charAt(0)}`.toUpperCase()
                    : row.nom_patient.substring(0, 2).toUpperCase();
                  return (
                    <div key={row.id} style={{ display: 'flex', alignItems: 'center', gap: '14px', padding: '13px 20px', borderBottom: '1px solid var(--sp-gray-100)' }}>
                      <div style={{ width: '38px', height: '38px', borderRadius: '10px', background: 'linear-gradient(135deg,var(--sp-primary),var(--sp-accent))', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: '13px', color: '#fff' }}>
                        {initials}
                      </div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontWeight: 600, fontSize: '13.5px', color: 'var(--sp-gray-800)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          {row.nom_patient}
                        </div>
                        <div style={{ fontSize: '11.5px', color: 'var(--sp-gray-400)' }}>
                          {new Date(row.date).toLocaleString('fr-FR')}
                        </div>
                      </div>
                      <span className={`sp-badge ${cls}`} style={{ fontSize: '10px' }}>{statutLabel[row.statut]}</span>
                    </div>
                  );
                })}
                {recentConsultations.length === 0 && (
                  <div className="sp-empty" style={{ padding: '30px' }}>
                    <Inbox size={32} style={{ color: 'var(--sp-gray-300)', marginBottom: '8px' }} />
                    <div className="sp-empty-title">Aucune consultation</div>
                  </div>
                )}
              </div>
          </div>
      </div>
    </>
  );
};

export default Dashboard;
