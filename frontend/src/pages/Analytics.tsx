import React, { useState, useEffect } from 'react';
import { Calendar, Users, Brain, TrendingUp, BarChart2, Info, AlertCircle, Activity, CheckCircle, XCircle } from 'lucide-react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Filler } from 'chart.js';
import { analyticsAPI } from '../services/api';
import DateRangePicker from '../components/DateRangePicker';

ChartJS.register(Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Filler);

type SeriesData = Awaited<ReturnType<typeof analyticsAPI.getSeries>>;

type MetricKey = 'resume' | 'consultations' | 'patients' | 'diagnostics' | 'approuves' | 'rejetes' | 'taux';

interface MetricDef {
  key: MetricKey;
  label: string;
  icon: React.ComponentType<{ size?: number; style?: React.CSSProperties }>;
  color: string;   // couleur principale (texte/courbe)
  bg: string;      // fond pastel de la pilule
  titreTotal?: string;
  titreSerie?: string;
  serie?: (d: SeriesData) => number[];
  total?: (d: SeriesData) => number;
  pourcent?: boolean;
}

const METRICS: MetricDef[] = [
  { key: 'resume', label: 'Résumé', icon: BarChart2, color: '#374151', bg: '#E5E7EB' },
  {
    key: 'consultations', label: 'Consultations', icon: Calendar, color: '#059669', bg: '#D1FAE5',
    titreTotal: 'Nombre total de consultations', titreSerie: 'Consultations quotidiennes',
    serie: d => d.consultations, total: d => d.totaux.consultations,
  },
  {
    key: 'patients', label: 'Patients', icon: Users, color: '#2563EB', bg: '#DBEAFE',
    titreTotal: 'Nombre total de nouveaux patients', titreSerie: 'Nouveaux patients quotidiens',
    serie: d => d.patients, total: d => d.totaux.patients,
  },
  {
    key: 'diagnostics', label: 'Diagnostics IA', icon: Brain, color: '#0D9488', bg: '#CCFBF1',
    titreTotal: 'Nombre total de diagnostics IA', titreSerie: 'Diagnostics IA quotidiens',
    serie: d => d.diagnostics, total: d => d.totaux.diagnostics,
  },
  {
    key: 'approuves', label: 'IA Approuvés', icon: CheckCircle, color: '#16A34A', bg: '#DCFCE7',
    titreTotal: 'Nombre total de diagnostics IA approuvés', titreSerie: 'Diagnostics IA approuvés quotidiens',
    serie: d => d.diagnostics_approuves, total: d => d.totaux.diagnostics_approuves,
  },
  {
    key: 'rejetes', label: 'IA Rejetés', icon: XCircle, color: '#DC2626', bg: '#FEE2E2',
    titreTotal: 'Nombre total de diagnostics IA rejetés', titreSerie: 'Diagnostics IA rejetés quotidiens',
    serie: d => d.diagnostics_rejetes, total: d => d.totaux.diagnostics_rejetes,
  },
  {
    key: 'taux', label: "Taux d'approbation", icon: TrendingUp, color: '#D97706', bg: '#FEF3C7',
    titreTotal: "Taux d'approbation sur la période", titreSerie: "Taux d'approbation quotidien",
    serie: d => d.taux_approbation, total: d => d.totaux.taux_approbation, pourcent: true,
  },
];

const toISODate = (d: Date) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;

const formatCourt = (iso: string) =>
  new Date(`${iso}T00:00:00`).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' });

// Dégradé vertical sous la courbe, dérivé de la couleur principale
const gradientFill = (hex: string) => (ctx: any) => {
  const { chart } = ctx;
  const { chartArea } = chart;
  if (!chartArea) return `${hex}20`;
  const grad = chart.ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
  grad.addColorStop(0, `${hex}38`);
  grad.addColorStop(1, `${hex}03`);
  return grad;
};

const Analytics = () => {
  // Période par défaut : les 30 derniers jours (aujourd'hui inclus)
  const defaultDebut = (() => { const d = new Date(); d.setDate(d.getDate() - 29); return toISODate(d); })();
  const defaultFin = toISODate(new Date());

  const [dateDebut, setDateDebut] = useState(defaultDebut);
  const [dateFin, setDateFin] = useState(defaultFin);
  const [metric, setMetric] = useState<MetricKey>('resume');
  const [data, setData] = useState<SeriesData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    analyticsAPI.getSeries({ dateDebut: dateDebut || undefined, dateFin: dateFin || undefined })
      .then(d => { if (!cancelled) { setData(d); setError(null); } })
      .catch(err => {
        console.error('Erreur lors du chargement des séries:', err);
        if (!cancelled) setError('Impossible de charger les données analytiques');
      })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [dateDebut, dateFin]);

  if (loading && !data) {
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

  if (error || !data) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <AlertCircle size={48} style={{ color: '#EF4444', margin: '0 auto' }} />
        <h3 style={{ marginTop: '16px', color: '#1F2937' }}>Erreur de connexion au backend</h3>
        <p style={{ color: '#6B7280', marginTop: '8px' }}>{error || 'Données non disponibles'}</p>
        <button
          onClick={() => window.location.reload()}
          style={{ marginTop: '16px', padding: '8px 16px', background: '#4F46E5', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}
        >
          Réessayer
        </button>
      </div>
    );
  }

  const labels = data.dates.map(formatCourt);
  const metricDef = METRICS.find(m => m.key === metric)!;

  const baseOptions = (pourcent: boolean): any => ({
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 1600, easing: 'easeInOutQuart' },
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: metric === 'resume'
        ? { display: true, position: 'top', labels: { usePointStyle: true, boxWidth: 8, font: { size: 11 }, color: '#374151' } }
        : { display: false },
      tooltip: {
        backgroundColor: '#1F2937',
        titleColor: '#E5E7EB',
        bodyColor: '#fff',
        padding: 10,
        cornerRadius: 8,
        callbacks: pourcent
          ? { label: (item: any) => ` ${item.dataset.label}: ${item.raw} %` }
          : undefined,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ...(pourcent ? { max: 100 } : {}),
        ticks: { color: '#6B7280', font: { size: 11 }, callback: pourcent ? (v: any) => `${v}%` : undefined },
        grid: { color: '#F3F4F6' },
        border: { display: false },
      },
      x: {
        ticks: { color: '#6B7280', font: { size: 11 }, maxTicksLimit: 16, maxRotation: 0 },
        grid: { display: false },
        border: { display: false },
      },
    },
  });

  const singleDataset = (def: MetricDef) => ({
    labels,
    datasets: [{
      label: def.label,
      data: def.serie!(data),
      borderColor: def.color,
      backgroundColor: gradientFill(def.color),
      borderWidth: 2,
      pointRadius: 0,
      pointHoverRadius: 5,
      pointHoverBackgroundColor: def.color,
      tension: 0.45,
      fill: true,
    }],
  });

  const resumeDatasets = {
    labels,
    datasets: METRICS.filter(m => m.serie && !m.pourcent).map(m => ({
      label: m.label,
      data: m.serie!(data),
      borderColor: m.color,
      backgroundColor: gradientFill(m.color),
      borderWidth: 2,
      pointRadius: 0,
      pointHoverRadius: 5,
      pointHoverBackgroundColor: m.color,
      tension: 0.45,
      fill: true,
    })),
  };

  return (
    <>
      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>

      <div className="sp-page-header sp-fade-in-up">
        <div>
          <h1 className="sp-page-title">Analytique</h1>
          <p className="sp-page-subtitle">Évolution quotidienne des données du système sur la période</p>
        </div>
      </div>

      {/* Barre de période avec calendrier déroulant double-mois */}
      <div className="sp-fade-in-up" style={{ animationDelay: '0.08s' }}>
        <DateRangePicker
          dateDebut={dateDebut}
          dateFin={dateFin}
          loading={loading}
          onChange={(debut, fin) => { setDateDebut(debut); setDateFin(fin); }}
        />
      </div>

      {/* Pilules de métriques */}
      <div className="sp-fade-in-up" style={{ animationDelay: '0.16s', display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '20px' }}>
        {METRICS.map(({ key, label, icon: Icon, color, bg }) => {
          const actif = metric === key;
          return (
            <button
              key={key}
              onClick={() => setMetric(key)}
              style={{
                display: 'flex', alignItems: 'center', gap: '8px',
                padding: '9px 16px', borderRadius: '999px',
                fontSize: '13px', fontWeight: 700, cursor: 'pointer',
                background: bg,
                color,
                border: `2px solid ${actif ? color : 'transparent'}`,
                transition: 'all 0.15s',
              }}
            >
              <Icon size={15} />
              {label}
            </button>
          );
        })}
      </div>

      {/* Carte de total (métrique sélectionnée) */}
      {metric !== 'resume' && (
        <div className="sp-fade-in-up" style={{ animationDelay: '0.24s', background: '#F6F6F7', borderRadius: '14px', padding: '24px 26px', marginBottom: '26px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', boxShadow: 'var(--sp-shadow)' }}>
          <div>
            <div style={{ fontSize: '40px', fontWeight: 800, color: '#111827', lineHeight: 1.1 }}>
              {metricDef.pourcent ? `${metricDef.total!(data)} %` : metricDef.total!(data)}
            </div>
            <div style={{ fontSize: '14px', color: '#374151', marginTop: '10px', fontWeight: 500 }}>{metricDef.titreTotal}</div>
          </div>
          <Info size={18} style={{ color: '#6B7280' }} />
        </div>
      )}

      {/* Courbe quotidienne */}
      <div className="sp-fade-in-up" style={{ animationDelay: '0.32s' }}>
        <h3 style={{ fontSize: '16px', fontWeight: 800, color: '#111827', margin: '0 0 12px' }}>
          {metric === 'resume' ? 'Activité quotidienne' : metricDef.titreSerie}
        </h3>
        <div className="sp-card" style={{ padding: '18px 16px' }}>
          <div style={{ height: '380px' }}>
            <Line
              data={metric === 'resume' ? resumeDatasets : singleDataset(metricDef)}
              options={baseOptions(metric !== 'resume' && !!metricDef.pourcent)}
            />
          </div>
        </div>
      </div>
    </>
  );
};

export default Analytics;
