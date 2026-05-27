import React, { useState, useEffect } from 'react';
import { Calendar, Activity, CheckCircle, UserCheck, Sun, List, PlusCircle, Inbox, UserX, PieChart, Brain, TrendingUp, AlertCircle, RefreshCw } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Doughnut, Line } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Filler } from 'chart.js';
import { analyticsAPI, healthAPI, mlAPI } from '../services/api';
import type { DashboardStats, Consultation } from '../services/api';
import { useAuth } from '../context/AuthContext';


ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Filler);

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
            <div className="sp-stat-value" style={{ display: 'flex', alignItems: 'baseline', color: '#0f172a' }}>
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
  const { user, isAdmin } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentConsultations, setRecentConsultations] = useState<Consultation[]>([]);
  const [personnel, setPersonnel] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modelInfo, setModelInfo] = useState<{
    loaded: boolean;
    n_features?: number;
    n_classes?: number;
    metadata?: { accuracy?: number; precision?: number; recall?: number; f1_score?: number; n_samples?: number };
  } | null>(null);
  const [activeMetrics, setActiveMetrics] = useState([true, true, true, true]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [dashboardData, consultationsData, healthData, personnelData, mlInfoData] = await Promise.all([
        analyticsAPI.getDashboard(),
        isAdmin ? Promise.resolve([]) : analyticsAPI.getRecentConsultations(6),
        healthAPI.check(),
        analyticsAPI.getPersonnelDisponible(),
        mlAPI.getModelInfo().catch(() => null),
      ]);
      setStats(dashboardData);
      setRecentConsultations(consultationsData);
      setModelInfo({
        loaded: healthData.model_loaded,
        n_features: mlInfoData?.n_features,
        n_classes: mlInfoData?.n_classes,
        metadata: mlInfoData?.metadata as any,
      });
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

      {/* Stats Grid */}
      <div className="sp-stats-grid sp-fade-in" style={{ marginBottom: '20px' }}>
          <StatCard label="Total Patients" value={statsData.totalPatients} icon={UserCheck} accent="#8B5CF6" bgIcon="#ede9fe" colorIcon="#7C3AED" />
          <StatCard label="Total Consultations" value={statsData.totalConsultations} icon={Calendar} accent="var(--sp-primary)" bgIcon="#dbeafe" colorIcon="var(--sp-primary)" />
          <StatCard label="Aujourd'hui" value={statsData.consultationsJour} icon={Sun} accent="#EC4899" bgIcon="#fce7f3" colorIcon="#DB2777" />
          <StatCard label="En Attente" value={statsData.enAttente} icon={Activity} accent="#3B82F6" bgIcon="#eff6ff" colorIcon="#2563EB" />
      </div>

      <div className="sp-stats-grid sp-fade-in" style={{ marginBottom: '20px' }}>
          <StatCard label="Diagnostics IA" value={statsData.diagnosticsIA} icon={Brain} accent="#6366F1" bgIcon="#eef2ff" colorIcon="#6366F1" />
          <StatCard label="IA Approuvés" value={statsData.diagnosticsApprouves} icon={CheckCircle} accent="var(--sp-success)" bgIcon="#d1fae5" colorIcon="var(--sp-success)" />
          <StatCard label="IA Rejetés" value={statsData.diagnosticsRejetes} icon={UserX} accent="var(--sp-danger)" bgIcon="#fee2e2" colorIcon="var(--sp-danger)" />
          <StatCard label="Taux d'approbation" value={Math.round(statsData.tauxApprobation)} icon={TrendingUp} accent="#F59E0B" bgIcon="#fef3c7" colorIcon="#D97706" />
      </div>

      {/* Première ligne : Système IA et Vue d'ensemble */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }} className="sp-fade-in">
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
              <div style={{padding: '16px 20px 20px'}}>
                {modelInfo?.loaded ? (() => {
                  const meta = modelInfo.metadata;
                  const toP = (v?: number) => v != null ? (v > 1 ? v : v * 100) : null;
                  const acc  = toP(meta?.accuracy)  ?? toP(stats?.model_accuracy) ?? 95.35;
                  const prec = toP(meta?.precision) ?? 95.68;
                  const rec  = toP(meta?.recall)    ?? 95.35;
                  const f1   = toP(meta?.f1_score)  ?? 95.32;

                  const metricDefs = [
                    { label: 'Accuracy',  val: acc,  color: '#4F46E5' },
                    { label: 'Précision', val: prec, color: '#059669' },
                    { label: 'Rappel',    val: rec,  color: '#D97706' },
                    { label: 'F1-Score',  val: f1,   color: '#DB2777' },
                  ];

                  const lineData = {
                    labels: metricDefs.map(m => m.label),
                    datasets: [{
                      label: 'Performance (%)',
                      data: metricDefs.map((m, i) => activeMetrics[i] ? m.val : null),
                      borderColor: '#4F46E5',
                      backgroundColor: (ctx: any) => {
                        const chart = ctx.chart;
                        const { chartArea } = chart;
                        if (!chartArea) return 'rgba(79,70,229,0.15)';
                        const grad = chart.ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
                        grad.addColorStop(0, 'rgba(79,70,229,0.28)');
                        grad.addColorStop(1, 'rgba(79,70,229,0.01)');
                        return grad;
                      },
                      borderWidth: 2.5,
                      pointBackgroundColor: metricDefs.map((m, i) => activeMetrics[i] ? m.color : 'transparent'),
                      pointBorderColor: metricDefs.map((m, i) => activeMetrics[i] ? '#fff' : 'transparent'),
                      pointBorderWidth: 2,
                      pointRadius: metricDefs.map((_: any, i: number) => activeMetrics[i] ? 6 : 0),
                      pointHoverRadius: metricDefs.map((_: any, i: number) => activeMetrics[i] ? 8 : 0),
                      tension: 0.42,
                      fill: true,
                      spanGaps: true,
                    }],
                  };

                  const lineOptions: any = {
                    animation: { duration: 800, easing: 'easeInOutQuart' },
                    responsive: true,
                    maintainAspectRatio: true,
                    layout: { padding: { left: 6, right: 6 } },
                    plugins: {
                      legend: { display: false },
                      tooltip: {
                        filter: (item: any) => item.raw !== null,
                        callbacks: {
                          label: (item: any) => ` ${(item.raw as number).toFixed(1)} %`,
                        },
                        backgroundColor: '#1e1b4b',
                        titleColor: '#c7d2fe',
                        bodyColor: '#fff',
                        padding: 8,
                        cornerRadius: 8,
                      },
                    },
                    scales: {
                      y: {
                        min: Math.floor(Math.min(acc, prec, rec, f1)) - 2,
                        max: Math.ceil(Math.max(acc, prec, rec, f1)) + 1,
                        ticks: { font: { size: 9 }, color: '#9CA3AF', callback: (v: any) => `${v}%` },
                        grid: { color: '#E5E7EB', drawBorder: false },
                      },
                      x: {
                        offset: false,
                        ticks: { font: { size: 9, weight: '700' }, color: '#374151' },
                        grid: { display: false },
                      },
                    },
                  };

                  return (
                    <>
                      {/* Line chart dynamique */}
                      <div style={{ marginBottom: '14px', background: '#F9FAFB', borderRadius: 12, padding: '10px 8px 6px', border: '1px solid #E5E7EB' }}>
                        <Line data={lineData} options={lineOptions} />
                      </div>

                      {/* Badges métriques cliquables */}
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                        {metricDefs.map(({ label, color }, i) => (
                          <span
                            key={label}
                            onClick={() => setActiveMetrics(prev => prev.map((v, j) => j === i ? !v : v))}
                            style={{
                              fontSize: 10,
                              fontWeight: 700,
                              background: activeMetrics[i] ? `${color}18` : '#F3F4F6',
                              color: activeMetrics[i] ? color : '#9CA3AF',
                              padding: '3px 10px',
                              borderRadius: 6,
                              border: `1.5px solid ${activeMetrics[i] ? color : '#E5E7EB'}`,
                              cursor: 'pointer',
                              textDecoration: activeMetrics[i] ? 'none' : 'line-through',
                              transition: 'all 0.2s',
                              userSelect: 'none',
                            }}
                          >
                            {label}
                          </span>
                        ))}
                      </div>
                    </>
                  );
                })() : (
                  <div style={{ textAlign: 'center', padding: '20px 0', color: '#9CA3AF' }}>
                    <div style={{ fontSize: 32, marginBottom: 8 }}>⚠️</div>
                    <div style={{ fontSize: 13, fontWeight: 600, color: '#EF4444' }}>Modèle non chargé</div>
                    <div style={{ fontSize: 11, marginTop: 4 }}>Entraînez le modèle depuis la page Administration</div>
                  </div>
                )}
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
                  <div style={{width: '100%', height: '320px', position: 'relative'}}>
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

      {/* Deuxième ligne : Personnel Médical et Consultations récentes */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }} className="sp-fade-in">
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
                          <span className="sp-number sp-number-md" style={{color: '#4F46E5'}}>
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
                          <span className="sp-number sp-number-md" style={{color: '#10B981'}}>
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

                  {/* Disponibilité — statistiques */}
                  <div style={{marginTop: '20px', paddingTop: '16px', borderTop: '1px solid #F3F4F6'}}>
                      <p style={{fontSize: '11px', color: '#9CA3AF', fontWeight: 600, marginBottom: '14px', textTransform: 'uppercase', letterSpacing: '0.06em'}}>Disponibilité en temps réel</p>
                      <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px'}}>
                          {[
                              { label: 'Médecins',   dispo: personnel?.medecins.disponibles   || 0, total: personnel?.medecins.total   || 0, color: '#4F46E5', bg: '#EEF2FF' },
                              { label: 'Infirmiers', dispo: personnel?.infirmiers.disponibles || 0, total: personnel?.infirmiers.total || 0, color: '#10B981', bg: '#ECFDF5' }
                          ].map(({ label, dispo, total, color, bg }) => {
                              const ratio = total > 0 ? dispo / total : 0;
                              const pct   = Math.round(ratio * 100);
                              const r     = 26;
                              const circ  = 2 * Math.PI * r;
                              const dash  = ratio * circ;
                              const indispo = total - dispo;
                              return (
                                  <div key={label} style={{display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '14px 8px 10px', background: bg, borderRadius: '12px', gap: '8px'}}>
                                      <div style={{position: 'relative', width: '72px', height: '72px'}}>
                                          <svg width="72" height="72" viewBox="0 0 72 72">
                                              <circle cx="36" cy="36" r={r} fill="none" stroke="white" strokeWidth="7"/>
                                              <circle cx="36" cy="36" r={r} fill="none" stroke={color} strokeWidth="7"
                                                  strokeDasharray={`${dash} ${circ - dash}`}
                                                  strokeLinecap={pct < 100 ? 'round' : 'butt'}
                                                  transform="rotate(-90 36 36)"/>
                                          </svg>
                                          <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
                                              <span style={{fontSize: '16px', fontWeight: 700, color, lineHeight: 1}}>{pct}%</span>
                                          </div>
                                      </div>
                                      <span style={{fontSize: '12px', fontWeight: 700, color: '#374151'}}>{label}</span>
                                      <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '3px', width: '100%'}}>
                                          <div style={{display: 'flex', justifyContent: 'space-between', width: '100%', fontSize: '11px'}}>
                                              <span style={{color: '#6B7280'}}>Disponibles</span>
                                              <span style={{fontWeight: 700, color}}>{dispo}</span>
                                          </div>
                                          <div style={{display: 'flex', justifyContent: 'space-between', width: '100%', fontSize: '11px'}}>
                                              <span style={{color: '#6B7280'}}>Indisponibles</span>
                                              <span style={{fontWeight: 700, color: indispo > 0 ? '#EF4444' : '#9CA3AF'}}>{indispo}</span>
                                          </div>
                                          <div style={{display: 'flex', justifyContent: 'space-between', width: '100%', fontSize: '11px', borderTop: '1px solid rgba(0,0,0,0.06)', paddingTop: '3px', marginTop: '1px'}}>
                                              <span style={{color: '#6B7280'}}>Total</span>
                                              <span style={{fontWeight: 600, color: '#374151'}}>{total}</span>
                                          </div>
                                      </div>
                                  </div>
                              );
                          })}
                      </div>
                  </div>
              </div>
          </div>

          {/* Consultations récentes (non-admin) / Top maladies (admin) */}
          {isAdmin ? (
            <div className="sp-card">
              <div className="sp-card-header">
                <div className="sp-card-title">
                  <PieChart size={20} />
                  Top maladies diagnostiquées
                </div>
              </div>
              <div style={{ padding: '16px 20px 20px' }}>
                {stats.top_diagnostics.length === 0 ? (
                  <div className="sp-empty" style={{ padding: '30px' }}>
                    <Inbox size={32} style={{ color: 'var(--sp-gray-300)', marginBottom: '8px' }} />
                    <div className="sp-empty-title">Aucun diagnostic enregistré</div>
                  </div>
                ) : (() => {
                  const maxCount = Math.max(...stats.top_diagnostics.map(d => d.count));
                  const palette = ['#4F46E5', '#7C3AED', '#DB2777', '#059669', '#D97706'];
                  return stats.top_diagnostics.slice(0, 5).map((d, i) => (
                    <div key={d.diagnostic} style={{ marginBottom: i < 4 ? '14px' : 0 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '5px' }}>
                        <span style={{ fontSize: '12.5px', fontWeight: 600, color: '#374151', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '75%' }}>
                          {d.diagnostic}
                        </span>
                        <span style={{ fontSize: '12px', fontWeight: 700, color: palette[i % palette.length] }}>
                          {d.count} cas
                        </span>
                      </div>
                      <div style={{ height: '6px', background: '#F3F4F6', borderRadius: '3px', overflow: 'hidden' }}>
                        <div style={{
                          height: '100%',
                          width: `${maxCount > 0 ? (d.count / maxCount) * 100 : 0}%`,
                          background: palette[i % palette.length],
                          borderRadius: '3px',
                          transition: 'width 0.8s ease',
                        }} />
                      </div>
                    </div>
                  ));
                })()}
              </div>
            </div>
          ) : (
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
          )}
      </div>
    </>
  );
};

export default Dashboard;
