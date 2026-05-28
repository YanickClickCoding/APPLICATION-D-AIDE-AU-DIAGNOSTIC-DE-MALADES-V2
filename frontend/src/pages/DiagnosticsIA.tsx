import React, { useState, useEffect, useCallback } from 'react';
import {
  Brain, CheckCircle, XCircle, TrendingUp, Activity,
  AlertCircle, Percent, RefreshCw, ImageOff
} from 'lucide-react';
import { analyticsAPI } from '../services/api';
import { MedicalDisclaimerBanner } from '../components/MedicalDisclaimerBanner';

const API = 'http://localhost:8000/api';

interface DiagStats {
  total_diagnostics: number;
  taux_approbation: number;
  confiance_moyenne: number;
}
interface ModelPerf {
  par_confiance: { high: number; medium: number; low: number };
  taux_rejet: number;
  total_diagnostics: number;
}

// ── Composant image matplotlib ────────────────────────────────────────────────
const ChartImage = ({ src, alt, loading }: { src: string | null; alt: string; loading: boolean }) => {
  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '280px', flexDirection: 'column', gap: '12px' }}>
        <RefreshCw size={28} style={{ animation: 'spin 1s linear infinite', color: '#7C3AED' }} />
        <span style={{ color: '#9CA3AF', fontSize: '13px' }}>Génération du graphique...</span>
      </div>
    );
  }
  if (!src) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '220px', flexDirection: 'column', gap: '10px' }}>
        <ImageOff size={32} style={{ color: '#D1D5DB' }} />
        <span style={{ color: '#9CA3AF', fontSize: '13px' }}>Graphique indisponible</span>
      </div>
    );
  }
  return (
    <img
      src={`data:image/png;base64,${src}`}
      alt={alt}
      style={{ width: '100%', borderRadius: '8px', display: 'block' }}
    />
  );
};

// ── Page principale ───────────────────────────────────────────────────────────
const DiagnosticsIA = () => {
  const [stats, setStats]   = useState<DiagStats | null>(null);
  const [perf, setPerf]     = useState<ModelPerf | null>(null);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState<string | null>(null);

  // Charts base64
  const [imgTop,       setImgTop]       = useState<string | null>(null);
  const [imgStatuts,   setImgStatuts]   = useState<string | null>(null);
  const [imgConfiance, setImgConfiance] = useState<string | null>(null);

  const [loadTop,       setLoadTop]       = useState(true);
  const [loadStatuts,   setLoadStatuts]   = useState(true);
  const [loadConfiance, setLoadConfiance] = useState(true);

  const fetchChart = useCallback(async (
    path: string,
    setter: (v: string | null) => void,
    loadSetter: (v: boolean) => void
  ) => {
    loadSetter(true);
    try {
      const res = await fetch(`${API}${path}`);
      if (!res.ok) throw new Error();
      const data = await res.json();
      setter(data.image ?? null);
    } catch {
      setter(null);
    } finally {
      loadSetter(false);
    }
  }, []);

  const fetchAll = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [dashData, perfData] = await Promise.all([
        analyticsAPI.getDashboard(),
        analyticsAPI.getModelPerformance(),
      ]);
      setStats({
        total_diagnostics: dashData.kpis.total_diagnostics,
        taux_approbation:  dashData.kpis.taux_approbation,
        confiance_moyenne: dashData.kpis.confiance_moyenne,
      });
      setPerf(perfData as ModelPerf);
    } catch (err: any) {
      setError(err.message || 'Erreur de chargement');
    } finally {
      setLoading(false);
    }

    // Graphiques en parallèle
    fetchChart('/analytics/charts/top-diagnostics?limit=10', setImgTop,       setLoadTop);
    fetchChart('/analytics/charts/statuts',                   setImgStatuts,   setLoadStatuts);
    fetchChart('/analytics/charts/confiance',                 setImgConfiance, setLoadConfiance);
  }, [fetchChart]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px', flexDirection: 'column', gap: '16px' }}>
        <style>{`@keyframes spin { from { transform:rotate(0deg) } to { transform:rotate(360deg) } }`}</style>
        <Brain size={48} style={{ animation: 'spin 1s linear infinite', color: '#7C3AED' }} />
        <p style={{ color: '#6B7280' }}>Chargement des diagnostics IA...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <AlertCircle size={48} style={{ color: '#EF4444', margin: '0 auto 16px' }} />
        <h3 style={{ color: '#1F2937', marginBottom: '8px' }}>Erreur de chargement</h3>
        <p style={{ color: '#6B7280', marginBottom: '16px' }}>{error}</p>
        <button onClick={fetchAll} className="sp-btn sp-btn-primary">Réessayer</button>
      </div>
    );
  }

  return (
    <>
      <style>{`@keyframes spin { from { transform:rotate(0deg) } to { transform:rotate(360deg) } }`}</style>

      {/* ── Header ── */}
      <div className="sp-page-header sp-fade-in">
        <div>
          <h1 className="sp-page-title">Diagnostics IA</h1>
          <p className="sp-page-subtitle">Analyse et performance du modèle Random Forest — 121 maladies</p>
        </div>
        <button onClick={fetchAll} className="sp-btn sp-btn-outline">
          <Activity size={16} /> Actualiser
        </button>
      </div>

      <MedicalDisclaimerBanner />
      

      {/* ── KPI Cards ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '24px' }} className="sp-fade-in">
        {[
          {
            label: 'Total diagnostics', value: stats?.total_diagnostics ?? 0,
            sub: 'générés par l\'IA', icon: Brain, bg: '#EDE9FE', color: '#7C3AED',
          },
          {
            label: "Taux d'approbation", value: `${stats?.taux_approbation ?? 0}%`,
            sub: 'confirmés par médecins', icon: CheckCircle, bg: '#D1FAE5', color: '#10B981',
          },
          {
            label: 'Taux de rejet', value: `${perf?.taux_rejet?.toFixed(1) ?? 0}%`,
            sub: 'rejetés par médecins', icon: XCircle, bg: '#FEE2E2', color: '#EF4444',
          },
          {
            label: 'Confiance moyenne', value: `${stats?.confiance_moyenne ?? 0}%`,
            sub: 'niveau de certitude IA', icon: Percent, bg: '#EFF6FF', color: '#3B82F6',
          },
        ].map(({ label, value, sub, icon: Icon, bg, color }) => (
          <div key={label} className="sp-card" style={{ padding: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <span style={{ fontSize: '13px', color: '#6B7280', fontWeight: 500 }}>{label}</span>
              <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: bg, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Icon size={18} style={{ color }} />
              </div>
            </div>
            <div style={{ fontSize: '28px', fontWeight: 700, color: '#1F2937' }}>{value}</div>
            <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>{sub}</div>
          </div>
        ))}
      </div>

      {/* ── Ligne 1 : Top diagnostics + Donut statuts ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '3fr 2fr', gap: '20px', marginBottom: '20px' }} className="sp-fade-in">

        {/* Top 10 maladies — graphique matplotlib */}
        <div className="sp-card">
          <div className="sp-card-header">
            <div className="sp-card-title">
              <TrendingUp size={20} />
              Top 10 maladies diagnostiquées
            </div>
          </div>
          <div style={{ padding: '16px 20px 20px' }}>
            <ChartImage src={imgTop} alt="Top 10 maladies" loading={loadTop} />
          </div>
        </div>

        {/* Répartition statuts — donut matplotlib */}
        <div className="sp-card">
          <div className="sp-card-header">
            <div className="sp-card-title">
              <CheckCircle size={20} />
              Répartition des diagnostics
            </div>
          </div>
          <div style={{ padding: '16px 20px 20px' }}>
            <ChartImage src={imgStatuts} alt="Répartition statuts" loading={loadStatuts} />
          </div>
        </div>
      </div>

      {/* ── Ligne 2 : Confiance + Infos modèle ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '3fr 2fr', gap: '20px' }} className="sp-fade-in">

        {/* Distribution certitude — graphique matplotlib */}
        <div className="sp-card">
          <div className="sp-card-header">
            <div className="sp-card-title">
              <Percent size={20} />
              Distribution de la certitude IA
            </div>
          </div>
          <div style={{ padding: '16px 20px 20px' }}>
            <ChartImage src={imgConfiance} alt="Distribution certitude" loading={loadConfiance} />
          </div>
        </div>

        {/* Infos modèle */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Performance par sévérité */}
          <div className="sp-card" style={{ padding: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <Activity size={18} style={{ color: '#4F46E5' }} />
              <span style={{ fontWeight: 600, color: '#1F2937', fontSize: '14px' }}>Performance par sévérité</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {[
                { label: 'Cas critiques confirmés', val: perf?.par_confiance?.high ?? 0, bg: '#FEE2E2', fg: '#EF4444', w: '70%' },
                { label: 'Cas graves confirmés',    val: perf?.par_confiance?.medium ?? 0, bg: '#FEF3C7', fg: '#F59E0B', w: '50%' },
                { label: 'Cas modérés confirmés',   val: perf?.par_confiance?.low ?? 0, bg: '#D1FAE5', fg: '#10B981', w: '80%' },
              ].map(({ label, val, bg, fg, w }) => (
                <div key={label}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <span style={{ fontSize: '13px', color: '#6B7280' }}>{label}</span>
                    <span style={{ fontSize: '13px', fontWeight: 600, color: fg }}>{val}</span>
                  </div>
                  <div style={{ height: '6px', background: bg, borderRadius: '3px' }}>
                    <div style={{ height: '100%', width: val ? w : '0%', background: fg, borderRadius: '3px', transition: 'width 0.6s ease' }} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Infos modèle */}
          <div className="sp-card" style={{ padding: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <div style={{ width: '32px', height: '32px', borderRadius: '8px', background: 'linear-gradient(135deg, #7C3AED, #4F46E5)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Brain size={16} style={{ color: '#fff' }} />
              </div>
              <span style={{ fontWeight: 600, color: '#1F2937', fontSize: '14px' }}>Modèle Random Forest</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {[
                { label: 'Algorithme',             value: 'Random Forest' },
                { label: 'Maladies détectables',   value: '121' },
                { label: 'Features analysées',     value: '400' },
                { label: 'Précision entraînement', value: '94.6%' },
                { label: 'Graphiques',             value: '● Matplotlib', color: '#4F46E5' },
                { label: 'Statut',                 value: '● Opérationnel', color: '#10B981' },
              ].map(item => (
                <div key={item.label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '12px', color: '#6B7280' }}>{item.label}</span>
                  <span style={{ fontSize: '12px', fontWeight: 600, color: item.color ?? '#1F2937' }}>{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default DiagnosticsIA;
