import React, { useState, useEffect } from 'react';
import { Calendar, Activity, CheckCircle, UserCheck, Sun, List, PlusCircle, Inbox, UserX, PieChart, Brain, TrendingUp, AlertCircle, RefreshCw } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { analyticsAPI, healthAPI } from '../services/api';
import type { DashboardStats, Consultation } from '../services/api';

ChartJS.register(ArcElement, Tooltip, Legend);

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
            <div className="sp-stat-value" style={{ display: 'flex', alignItems: 'baseline', color: '#0f172a', fontFamily: "'Syne', sans-serif" }}>
                <span style={{ fontSize: '38px', fontWeight: 900, lineHeight: 1 }}>{displayValue}</span>
                {total !== undefined && (
                  <span style={{ fontSize: '24px', fontWeight: 700, color: '#94a3b8', marginLeft: '4px' }}>
                    / {displayTotal}
                  </span>
                )}
            </div>
            <div className="sp-stat-label" style={{ fontWeight: 700, fontSize: '11px', letterSpacing: '0.08em', marginTop: '6px' }}>{label}</div>
        </div>
    </div>
  );
};

const CenteredCounter = ({ value }: { value: number }) => {
  const displayValue = useCounter(value);
  return (
    <div style={{fontSize: '24px', fontWeight: 700, color: '#64748B', fontFamily: "'DM Sans', sans-serif"}}>
        {displayValue}
    </div>
  );
};

const Dashboard = () => {
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
        analyticsAPI.getPersonnelDisponible()
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
    enCours: stats.kpis.consultations_en_cours || 0,
    terminees: stats.kpis.consultations_terminees || 0,
    medecinsDispo: personnel?.medecins.disponibles || 0,
    totalMedecins: personnel?.medecins.total || 0,
    infirmiersDispo: personnel?.infirmiers.disponibles || 0,
    totalInfirmiers: personnel?.infirmiers.total || 0,
    consultationsJour: 0, // Pas encore disponible dans l'API
    totalPatients: stats.kpis.total_patients,
    diagnosticsIA: stats.kpis.total_diagnostics,
    diagnosticsApprouves: 0, // Pas encore disponible dans l'API
    diagnosticsRejetes: 0, // Pas encore disponible dans l'API
    tauxApprobation: stats.kpis.taux_approbation
  };

  const totalStatsCount = statsData.totalConsultations + statsData.enCours + statsData.consultationsJour + statsData.totalPatients + statsData.diagnosticsIA;

  const chartData = {
    labels: ['Total Consultations', 'En cours', 'Aujourd\'hui', 'Total Patients', 'Diagnostics IA', 'IA Approuvés'],
    datasets: [{
      data: totalStatsCount === 0 ? [1, 1] : [
        statsData.totalConsultations, 
        statsData.enCours, 
        statsData.consultationsJour, 
        statsData.totalPatients,
        statsData.diagnosticsIA,
        statsData.diagnosticsApprouves
      ],
      backgroundColor: totalStatsCount === 0 ? ['#4a4a4a', '#4a4a4a'] : ['#0A4B8C', '#3B82F6', '#EC4899', '#8B5CF6', '#6366F1', '#10B981'],
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
          color: '#CBD5E1',
          font: { family: "'DM Sans', sans-serif", size: 10 },
          padding: 10,
          boxWidth: 12
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
              <p className="sp-page-subtitle">Vue d'ensemble de la clinique SANTÉ PLUS · Système IA {modelInfo?.loaded ? '✓' : '✗'}</p>
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
              <Link to="/consultations" className="sp-btn sp-btn-primary">
                  <PlusCircle size={18} /> Nouvelle consultation
              </Link>
          </div>
      </div>

      {/* Stats Grid */}
      <div className="sp-stats-grid sp-fade-in" style={{ marginBottom: '20px' }}>
          <StatCard label="Total Patients" value={statsData.totalPatients} icon={UserCheck} accent="#8B5CF6" bgIcon="#ede9fe" colorIcon="#7C3AED" />
          <StatCard label="Total Consultations" value={statsData.totalConsultations} icon={Calendar} accent="var(--sp-primary)" bgIcon="#dbeafe" colorIcon="var(--sp-primary)" />
          <StatCard label="Aujourd'hui" value={statsData.consultationsJour} icon={Sun} accent="#EC4899" bgIcon="#fce7f3" colorIcon="#DB2777" />
          <StatCard label="En Cours" value={statsData.enCours} icon={Activity} accent="#3B82F6" bgIcon="#eff6ff" colorIcon="#2563EB" />
      </div>

      <div className="sp-stats-grid sp-fade-in" style={{ marginBottom: '20px' }}>
          <StatCard label="Diagnostics IA" value={statsData.diagnosticsIA} icon={Brain} accent="#6366F1" bgIcon="#eef2ff" colorIcon="#6366F1" />
          <StatCard label="IA Approuvés" value={statsData.diagnosticsApprouves} icon={CheckCircle} accent="var(--sp-success)" bgIcon="#d1fae5" colorIcon="var(--sp-success)" />
          <StatCard label="IA Rejetés" value={statsData.diagnosticsRejetes} icon={UserX} accent="var(--sp-danger)" bgIcon="#fee2e2" colorIcon="var(--sp-danger)" />
          <StatCard label="Taux d'approbation" value={statsData.tauxApprobation} icon={TrendingUp} accent="#F59E0B" bgIcon="#fef3c7" colorIcon="#D97706" />
      </div>

      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr 1fr 1fr', gap:'20px'}} className="sp-fade-in">
          {/* Personnel disponible */}
          <div className="sp-card">
              <div className="sp-card-header">
                  <div className="sp-card-title">
                      <UserCheck size={20} />
                      Personnel Médical
                  </div>
              </div>
              <div style={{padding: '20px'}}>
                  <div style={{marginBottom: '20px'}}>
                      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px'}}>
                          <span style={{fontSize: '13px', color: '#6B7280', fontWeight: 600}}>Médecins</span>
                          <span style={{fontSize: '20px', fontWeight: 700, color: '#4F46E5'}}>
                              {personnel?.medecins.disponibles || 0}/{personnel?.medecins.total || 0}
                          </span>
                      </div>
                      <div style={{height: '6px', background: '#E5E7EB', borderRadius: '3px', overflow: 'hidden'}}>
                          <div style={{
                              height: '100%',
                              width: `${personnel?.medecins.total > 0 ? (personnel.medecins.disponibles / personnel.medecins.total * 100) : 0}%`,
                              background: 'linear-gradient(90deg, #4F46E5, #7C3AED)',
                              transition: 'width 0.3s ease'
                          }}></div>
                      </div>
                  </div>
                  <div>
                      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px'}}>
                          <span style={{fontSize: '13px', color: '#6B7280', fontWeight: 600}}>Infirmiers</span>
                          <span style={{fontSize: '20px', fontWeight: 700, color: '#10B981'}}>
                              {personnel?.infirmiers.disponibles || 0}/{personnel?.infirmiers.total || 0}
                          </span>
                      </div>
                      <div style={{height: '6px', background: '#E5E7EB', borderRadius: '3px', overflow: 'hidden'}}>
                          <div style={{
                              height: '100%',
                              width: `${personnel?.infirmiers.total > 0 ? (personnel.infirmiers.disponibles / personnel.infirmiers.total * 100) : 0}%`,
                              background: 'linear-gradient(90deg, #10B981, #059669)',
                              transition: 'width 0.3s ease'
                          }}></div>
                      </div>
                  </div>
              </div>
          </div>

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
                    const sc: Record<string, string> = { 'en attente': 'attente', 'en cours': 'cours', 'terminée': 'terminee' };
                    const cls = sc[row.statut] || 'attente';
                    const statutLabel: Record<string, string> = { 'en attente': 'En attente', 'en cours': 'En cours', 'terminée': 'Terminée' };
                    
                    return (
                      <div key={row.id} style={{display:'flex', alignItems:'center', gap:'14px', padding:'13px 20px', borderBottom:'1px solid var(--sp-gray-100)'}}>
                          <div style={{width:'38px', height:'38px', borderRadius:'10px', background:'linear-gradient(135deg,var(--sp-primary),var(--sp-accent))', display:'flex', alignItems:'center', justifyContent:'center', flexShrink:0}}>
                              <Activity size={16} style={{color:'#fff'}} />
                          </div>
                          <div style={{flex:1, minWidth:0}}>
                              <div style={{fontWeight:600, fontSize:'13.5px', color:'var(--sp-gray-800)', whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis'}}>
                                  {row.nom_patient}
                              </div>
                              <div style={{fontSize:'11.5px', color:'var(--sp-gray-400)'}}>
                                  {new Date(row.date).toLocaleString('fr-FR')}
                              </div>
                          </div>
                          <span className={`sp-badge ${cls}`} style={{ fontSize: '10px' }}>{statutLabel[row.statut]}</span>
                      </div>
                    );
                  })}
                  {recentConsultations.length === 0 && (
                  <div className="sp-empty" style={{padding:'30px'}}>
                      <Inbox size={32} style={{ color: 'var(--sp-gray-300)', marginBottom: '8px' }} />
                      <div className="sp-empty-title">Aucune consultation</div>
                  </div>
                  )}
              </div>
          </div>

          {/* Statut du système IA */}
          <div className="sp-card">
              <div className="sp-card-header">
                  <div className="sp-card-title">
                      <Brain size={20} />
                      Système IA
                  </div>
                  <span className={`sp-badge ${modelInfo?.loaded ? 'available' : 'attente'}`} style={{fontSize: '10px'}}>
                      {modelInfo?.loaded ? 'Actif' : 'Inactif'}
                  </span>
              </div>
              <div style={{padding: '20px'}}>
                  <div style={{marginBottom: '16px'}}>
                      <div style={{fontSize: '12px', color: '#6B7280', marginBottom: '4px'}}>Modèle chargé</div>
                      <div style={{fontSize: '16px', fontWeight: 600, color: modelInfo?.loaded ? '#10B981' : '#EF4444'}}>
                          {modelInfo?.loaded ? 'Oui' : 'Non'}
                      </div>
                  </div>
                  <div style={{marginBottom: '16px'}}>
                      <div style={{fontSize: '12px', color: '#6B7280', marginBottom: '4px'}}>Précision du modèle</div>
                      <div style={{fontSize: '16px', fontWeight: 600, color: '#4F46E5'}}>
                          {stats.model_accuracy ? `${(stats.model_accuracy * 100).toFixed(1)}%` : '94.6%'}
                      </div>
                  </div>
                  <div>
                      <div style={{fontSize: '12px', color: '#6B7280', marginBottom: '4px'}}>Maladies détectables</div>
                      <div style={{fontSize: '16px', fontWeight: 600, color: '#8B5CF6'}}>
                          121
                      </div>
                  </div>
              </div>
          </div>

          {/* Graphique des données */}
          <div className="sp-card" style={{backgroundColor: '#242424', border: 'none'}}>
              <div className="sp-card-header" style={{borderBottom: '1px solid #333'}}>
                  <div className="sp-card-title" style={{color: '#fff'}}>
                      <PieChart size={20} style={{color: '#60a5fa'}} />
                      Vue d'ensemble
                  </div>
              </div>
              <div style={{padding: '20px', display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
                  <div style={{width: '100%', height: '280px', position: 'relative'}}>
                      <Doughnut data={chartData} options={chartOptions} />
                      <div style={{position: 'absolute', top: 0, left: 0, right: 0, bottom: '40px', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', pointerEvents: 'none'}}>
                          <CenteredCounter value={statsData.totalConsultations} />
                          <div style={{fontSize: '14px', color: '#64748B', fontFamily: "'DM Sans', sans-serif"}}>
                              Consultations
                          </div>
                      </div>
                  </div>
              </div>
          </div>

      </div>
    </>
  );
};

export default Dashboard;
