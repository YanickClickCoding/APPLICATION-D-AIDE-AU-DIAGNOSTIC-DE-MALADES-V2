import React, { useState, useEffect } from 'react';
import { getConsultations, getMedecins } from '../db';
import { Calendar, Clock, Activity, CheckCircle, UserCheck, Sun, List, PlusCircle, Inbox, UserX, PieChart } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

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
      // Ease out expo
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
  const consultations = getConsultations();
  const medecins = getMedecins();
  
  const statsData = {
    totalConsultations: consultations.length,
    enAttente: consultations.filter(c => c && c.statut === 'en attente').length,
    enCours: consultations.filter(c => c && c.statut === 'en cours').length,
    terminees: consultations.filter(c => c && c.statut === 'terminée').length,
    medecinsDispo: medecins.filter(m => m && m.disponible).length,
    totalMedecins: medecins.length,
    consultationsJour: consultations.filter(c => c && c.date_heure && new Date(c.date_heure).toDateString() === new Date().toDateString()).length
  };

  const getMedecinName = (id: number | null) => {
    if (!id) return null;
    const m = medecins.find(med => med && med.medecin_id === id);
    return m ? `Dr. ${m.prenoms} ${m.nom}` : null;
  };

  const recent = [...consultations]
    .filter(c => !!c)
    .sort((a, b) => new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime())
    .slice(0, 6);
  const medecinsDispo = medecins.filter(m => m && m.disponible).slice(0, 6);

  const totalStatsCount = statsData.totalConsultations + statsData.enAttente + statsData.enCours + statsData.terminees + statsData.medecinsDispo + statsData.consultationsJour;

  const chartData = {
    labels: ['Total Consultations', 'En attente', 'En cours', 'Terminées', 'Médecins disponibles', 'Aujourd\'hui'],
    datasets: [{
      data: totalStatsCount === 0 ? [1, 1] : [statsData.totalConsultations, statsData.enAttente, statsData.enCours, statsData.terminees, statsData.medecinsDispo, statsData.consultationsJour],
      backgroundColor: totalStatsCount === 0 ? ['#4a4a4a', '#4a4a4a'] : ['#0A4B8C', '#F59E0B', '#3B82F6', '#10B981', '#8B5CF6', '#EC4899'],
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
      <div className="sp-page-header sp-fade-in">
          <div>
              <h1 className="sp-page-title">Tableau de bord</h1>
              <p className="sp-page-subtitle">Vue d'ensemble de la clinique SANTÉ PLUS</p>
          </div>
          <div style={{display:'flex',gap:'10px',alignItems:'center'}}>
              <Link to="/consultations" className="sp-btn sp-btn-primary">
                  <PlusCircle size={18} /> Nouvelle consultation
              </Link>
          </div>
      </div>

      {/* Stats Grid */}
      <div className="sp-stats-grid sp-fade-in" style={{ marginBottom: '24px' }}>
          <StatCard label="Total Consultations" value={statsData.totalConsultations} icon={Calendar} accent="var(--sp-primary)" bgIcon="#dbeafe" colorIcon="var(--sp-primary)" />
          <StatCard label="En attente" value={statsData.enAttente} icon={Clock} accent="#F59E0B" bgIcon="#fef3c7" colorIcon="#D97706" />
          <StatCard label="En cours" value={statsData.enCours} icon={Activity} accent="#3B82F6" bgIcon="#eff6ff" colorIcon="#2563EB" />
          <StatCard label="Terminées" value={statsData.terminees} icon={CheckCircle} accent="var(--sp-success)" bgIcon="#d1fae5" colorIcon="var(--sp-success)" />
          <StatCard label="MÉDECINS DISPONIBLES" value={statsData.medecinsDispo} total={statsData.totalMedecins} icon={UserCheck} accent="#8B5CF6" bgIcon="#ede9fe" colorIcon="#7C3AED" />
          <StatCard label="Aujourd'hui" value={statsData.consultationsJour} icon={Sun} accent="#EC4899" bgIcon="#fce7f3" colorIcon="#DB2777" />
      </div>

      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:'20px'}} className="sp-fade-in">
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
                  {recent.map(row => {
                    const mName = getMedecinName(row.medecin_id);
                    const sc: Record<string, string> = { 'en attente': 'attente', 'en cours': 'cours', 'terminée': 'terminee' };
                    const cls = sc[row.statut] || 'attente';
                    
                    return (
                      <div key={row.consultation_id} style={{display:'flex', alignItems:'center', gap:'14px', padding:'13px 20px', borderBottom:'1px solid var(--sp-gray-100)'}}>
                          <div style={{width:'38px', height:'38px', borderRadius:'10px', background:'linear-gradient(135deg,var(--sp-primary),var(--sp-accent))', display:'flex', alignItems:'center', justifyContent:'center', flexShrink:0}}>
                              <Activity size={16} style={{color:'#fff'}} />
                          </div>
                          <div style={{flex:1, minWidth:0}}>
                              <div style={{fontWeight:600, fontSize:'13.5px', color:'var(--sp-gray-800)', whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis'}}>
                                  {row.nom_patient}
                              </div>
                              <div style={{fontSize:'11.5px', color:'var(--sp-gray-400)'}}>
                                  {new Date(row.date_heure).toLocaleString('fr-FR')} {mName && `· ${mName}`}
                              </div>
                          </div>
                          <span className={`sp-badge ${cls}`} style={{ fontSize: '10px' }}>{row.statut}</span>
                      </div>
                    );
                  })}
                  {recent.length === 0 && (
                  <div className="sp-empty" style={{padding:'30px'}}>
                      <Inbox size={32} style={{ color: 'var(--sp-gray-300)', marginBottom: '8px' }} />
                      <div className="sp-empty-title">Aucune consultation</div>
                  </div>
                  )}
              </div>
          </div>

          {/* Médecins disponibles */}
          <div className="sp-card">
              <div className="sp-card-header">
                  <div className="sp-card-title">
                      <UserCheck size={20} />
                      Médecins disponibles
                  </div>
                  <Link to="/medecins" className="sp-btn sp-btn-outline sp-btn-sm">Gérer</Link>
              </div>
              <div>
                  {medecinsDispo.map(med => (
                  <div key={med.medecin_id} style={{display:'flex', alignItems:'center', gap:'14px', padding:'13px 20px', borderBottom:'1px solid var(--sp-gray-100)'}}>
                      <div style={{width:'38px', height:'38px', borderRadius:'50%', background:'linear-gradient(135deg,#059669,#10b981)', display:'flex', alignItems:'center', justifyContent:'center', flexShrink:0, fontFamily:"'Syne',sans-serif", fontWeight:700, fontSize:'13px', color:'#fff'}}>
                          {((med.prenoms || '?').substring(0, 1) + (med.nom || '?').substring(0, 1)).toUpperCase()}
                      </div>
                      <div style={{flex:1, minWidth:0}}>
                          <div style={{fontWeight:600, fontSize:'13.5px', color:'var(--sp-gray-800)'}}>
                              Dr. {med.prenoms} {med.nom}
                          </div>
                          <div style={{fontSize:'11.5px', color:'var(--sp-gray-400)'}}>
                              {med.specialite}
                          </div>
                      </div>
                      <span className="sp-badge available" style={{display:'flex', alignItems:'center', gap:'4px', fontSize: '10px'}}>
                          Dispo
                      </span>
                  </div>
                  ))}
                  {medecinsDispo.length === 0 && (
                  <div className="sp-empty" style={{padding:'30px'}}>
                      <UserX size={32} style={{ color: 'var(--sp-gray-300)', marginBottom: '8px' }} />
                      <div className="sp-empty-title">Aucun médecin disponible</div>
                  </div>
                  )}
              </div>
          </div>

          {/* Toutes les données (Graphique) */}
          <div className="sp-card" style={{backgroundColor: '#242424', border: 'none'}}>
              <div className="sp-card-header" style={{borderBottom: '1px solid #333'}}>
                  <div className="sp-card-title" style={{color: '#fff'}}>
                      <PieChart size={20} style={{color: '#60a5fa'}} />
                      Toutes les données
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
