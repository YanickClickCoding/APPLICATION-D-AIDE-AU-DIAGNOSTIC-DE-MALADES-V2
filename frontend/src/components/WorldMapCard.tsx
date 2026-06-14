import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Globe, RefreshCw, Search, X } from 'lucide-react';
import { geoEqualEarth, geoPath } from 'd3-geo';
import { feature } from 'topojson-client';
import { analyticsAPI } from '../services/api';
import { continentOf, type Continent } from './countryContinent';

/**
 * Carte du monde dynamique pour le tableau de bord.
 * Rendu SVG réaliste fait main avec d3-geo (projection) + topojson-client
 * (décodage des contours) — sans react-simple-maps, incompatible React 19.
 *
 * Localise les maladies dans le monde : un continent s'allume s'il est
 * concerné par la maladie (savoir géographique OMS, côté backend), avec une
 * intensité reflétant le nombre de cas réellement diagnostiqués. Sélecteur de
 * maladie + barres de poids par continent. Branché sur
 * /analytics/diagnostics-par-continent.
 */

interface ContinentStat {
  nom: string;
  pourcentage: number;   // distribution mondiale OMS (ou estimée)
  intensite: number;     // poids OMS relatif (0–1) — renvoyé par l'API
}

// Topojson de la carte du monde (world-atlas, codes ISO numériques en geo.id).
const GEO_URL = 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json';

const COULEURS: Record<string, string> = {
  Afrique:  '#EF4444',
  Europe:   '#3B82F6',
  Amérique: '#F59E0B',
  Asie:     '#8B5CF6',
  Océanie:  '#10B981',
};

const GRIS = '#F3F4F6';        // pays sans cas (gris clair, ressort sur le fond gris de la carte)
const GRIS_STROKE = '#9CA3AF';

// Dimensions du viewBox SVG de la carte.
const W = 800;
const H = 360;

interface PaysGeo {
  id: string;
  d: string;            // tracé SVG projeté
  continent: Continent | null;
}

const WorldMapCard = () => {
  const [maladie, setMaladie] = useState<string>('');
  const [continents, setContinents] = useState<ContinentStat[]>([]);
  const [maladies, setMaladies] = useState<string[]>([]);
  const [total, setTotal] = useState(0);
  const [source, setSource] = useState('');
  const [loading, setLoading] = useState(true);

  // Recherche de maladie (champ + liste filtrée déroulante).
  const [recherche, setRecherche] = useState('');
  const [rechercheOuverte, setRechercheOuverte] = useState(false);
  const rechercheRef = useRef<HTMLDivElement>(null);

  // Continent survolé (depuis les barres) : seul lui reste visible sur la carte.
  const [continentSurvole, setContinentSurvole] = useState<string | null>(null);

  // Géométrie de la carte (chargée une seule fois depuis le CDN).
  const [pays, setPays] = useState<PaysGeo[]>([]);
  const [geoError, setGeoError] = useState(false);

  // Chargement + projection de la carte du monde (une seule fois).
  useEffect(() => {
    let annule = false;
    fetch(GEO_URL)
      .then(r => r.json())
      .then((topo: any) => {
        if (annule) return;
        const fc: any = feature(topo, topo.objects.countries);
        const projection = geoEqualEarth().fitSize([W, H], fc);
        const path = geoPath(projection);
        const liste: PaysGeo[] = fc.features.map((f: any) => ({
          id: String(f.id),
          d: path(f) || '',
          continent: continentOf(f.id),
        }));
        setPays(liste);
      })
      .catch(() => { if (!annule) setGeoError(true); });
    return () => { annule = true; };
  }, []);

  const charger = useCallback((m: string) => {
    setLoading(true);
    analyticsAPI.getDiagnosticsParContinent(m || undefined)
      .then(d => {
        setContinents(d.continents);
        setTotal(d.total);
        setSource(d.source);
        setMaladies(prev => (prev.length ? prev : d.maladies));
      })
      .catch(() => { setContinents([]); setTotal(0); })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { charger(maladie); }, [maladie, charger]);

  // Ferme la liste de recherche au clic en dehors.
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (rechercheRef.current && !rechercheRef.current.contains(e.target as Node)) {
        setRechercheOuverte(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  // Maladies filtrées par le texte de recherche (insensible à la casse/accents).
  const sansAccent = (s: string) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  const maladiesFiltrees = maladies.filter(m => sansAccent(m).includes(sansAccent(recherche)));

  const choisirMaladie = (m: string) => {
    setMaladie(m);
    setRecherche('');
    setRechercheOuverte(false);
  };

  const statParNom = (nom: string) => continents.find(c => c.nom === nom);

  // Aucune donnée OMS pour la maladie : la carte n'affiche aucun pourcentage.
  const aucuneDonnee = source === 'aucune' || continents.length === 0;

  // Couleur d'un pays : couleur PLEINE et vive du continent dès qu'il est
  // concerné par la maladie (pourcentage > 0), gris sinon.
  // Quand un continent est survolé (depuis les barres), seul lui reste visible :
  // les autres sont fortement atténués en gris.
  const styleFor = (continent: Continent | null): { fill: string; opacity: number } => {
    const estAutre = continentSurvole !== null && continent !== continentSurvole;
    if (estAutre) return { fill: GRIS, opacity: 0.15 };
    if (!continent) return { fill: GRIS, opacity: 1 };
    const stat = statParNom(continent);
    if (!stat || stat.pourcentage === 0) return { fill: GRIS, opacity: 1 };
    return { fill: COULEURS[continent] ?? GRIS, opacity: 1 };
  };

  return (
    <div className="sp-card" style={{ backgroundColor: '#E5E7EB', border: 'none', display: 'flex', flexDirection: 'column' }}>
      <div className="sp-card-header" style={{ borderBottom: '1px solid #D1D5DB' }}>
        <div className="sp-card-title" style={{ color: '#1F2937' }}>
          <Globe size={20} style={{ color: '#2563EB' }} />
          Répartition par continent
        </div>

        {/* Recherche de maladie */}
        <div ref={rechercheRef} style={{ position: 'relative', width: '210px' }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: '6px',
            background: '#fff', border: '1px solid #D1D5DB', borderRadius: '8px',
            padding: '6px 10px',
          }}>
            <Search size={14} style={{ color: '#6B7280', flexShrink: 0 }} />
            <input
              type="text"
              value={recherche}
              placeholder={maladie || 'Rechercher une maladie…'}
              onFocus={() => setRechercheOuverte(true)}
              onChange={e => { setRecherche(e.target.value); setRechercheOuverte(true); }}
              style={{
                border: 'none', outline: 'none', background: 'transparent',
                fontSize: '12px', fontWeight: 600, color: '#1F2937', width: '100%',
              }}
            />
            {maladie && (
              <button
                onClick={() => choisirMaladie('')}
                title="Réinitialiser"
                style={{ border: 'none', background: 'transparent', cursor: 'pointer', display: 'flex', padding: 0, color: '#9CA3AF' }}
              >
                <X size={14} />
              </button>
            )}
          </div>

          {/* Liste déroulante filtrée */}
          {rechercheOuverte && (
            <div style={{
              position: 'absolute', top: 'calc(100% + 4px)', left: 0, right: 0, zIndex: 20,
              background: '#fff', border: '1px solid #D1D5DB', borderRadius: '8px',
              boxShadow: '0 8px 24px rgba(0,0,0,0.15)', maxHeight: '320px', overflowY: 'auto',
            }}>
              {/* Compteur : confirme le nombre de maladies disponibles/filtrées */}
              <div style={{
                position: 'sticky', top: 0, background: '#F9FAFB', zIndex: 1,
                padding: '6px 12px', fontSize: '10px', fontWeight: 700, color: '#9CA3AF',
                textTransform: 'uppercase', letterSpacing: '0.04em', borderBottom: '1px solid #E5E7EB',
              }}>
                {recherche
                  ? `${maladiesFiltrees.length} résultat${maladiesFiltrees.length > 1 ? 's' : ''}`
                  : `${maladies.length} maladies`}
              </div>
              <div
                onClick={() => choisirMaladie('')}
                style={{ padding: '8px 12px', fontSize: '12px', fontWeight: 600, color: '#6B7280', cursor: 'pointer', borderBottom: '1px solid #F3F4F6' }}
                onMouseEnter={e => { e.currentTarget.style.background = '#F3F4F6'; }}
                onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; }}
              >
                Toutes les maladies
              </div>
              {maladiesFiltrees.length === 0 ? (
                <div style={{ padding: '10px 12px', fontSize: '12px', color: '#9CA3AF' }}>Aucun résultat</div>
              ) : (
                maladiesFiltrees.map(m => (
                  <div
                    key={m}
                    onClick={() => choisirMaladie(m)}
                    style={{
                      padding: '8px 12px', fontSize: '12px', cursor: 'pointer',
                      color: m === maladie ? '#2563EB' : '#1F2937',
                      fontWeight: m === maladie ? 700 : 500,
                    }}
                    onMouseEnter={e => { e.currentTarget.style.background = '#F3F4F6'; }}
                    onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; }}
                  >
                    {m}
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>

      <div style={{ padding: '12px 16px 18px', flex: 1, display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {loading && pays.length === 0 ? (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '240px', color: '#9CA3AF', gap: '10px' }}>
            <RefreshCw size={22} style={{ animation: 'spin 1s linear infinite', color: '#60a5fa' }} />
            <span style={{ fontSize: '13px' }}>Chargement de la carte…</span>
          </div>
        ) : (
          <>
            {/* Carte du monde réaliste (SVG d3-geo) */}
            {geoError ? (
              <div style={{ height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748B', fontSize: '13px' }}>
                Carte indisponible (connexion requise)
              </div>
            ) : (
              <svg viewBox={`0 0 ${W} ${H}`} style={{ width: '100%', height: 'auto' }}>
                <rect x={0} y={0} width={W} height={H} fill="transparent" />
                {pays.map(p => {
                  const { fill, opacity } = styleFor(p.continent);
                  return (
                    <path
                      key={p.id}
                      d={p.d}
                      fill={fill}
                      fillOpacity={opacity}
                      stroke={GRIS_STROKE}
                      strokeWidth={0.3}
                      style={{ transition: 'fill 0.4s, fill-opacity 0.4s' }}
                    >
                      <title>{p.continent ?? 'N/A'}</title>
                    </path>
                  );
                })}
              </svg>
            )}

            {aucuneDonnee ? (
              /* Aucune donnée OMS : message clair, pas de barres ni de % inventés */
              <div style={{
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                padding: '14px', borderRadius: '8px', background: '#EEF0F2',
                color: '#6B7280', fontSize: '12.5px', fontWeight: 600, textAlign: 'center',
              }}>
                Aucune donnée OMS pour cette maladie
              </div>
            ) : (
              /* Barres de poids par continent — survol = isole le continent sur la carte */
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px' }}>
                {continents.map(c => (
                  <div
                    key={c.nom}
                    onMouseEnter={() => setContinentSurvole(c.nom)}
                    onMouseLeave={() => setContinentSurvole(null)}
                    style={{
                      cursor: 'pointer', borderRadius: '6px', padding: '2px 4px', margin: '-2px -4px',
                      background: continentSurvole === c.nom ? 'rgba(0,0,0,0.05)' : 'transparent',
                      transition: 'background 0.2s',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '3px' }}>
                      <span style={{ fontSize: '12px', color: '#374151', fontWeight: 600 }}>{c.nom}</span>
                      <span style={{ fontSize: '12px', fontWeight: 700, color: c.pourcentage ? COULEURS[c.nom] : '#9CA3AF' }}>
                        {c.pourcentage}%
                      </span>
                    </div>
                    <div style={{ height: '5px', background: '#D1D5DB', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{
                        height: '100%', width: `${c.pourcentage}%`,
                        background: c.pourcentage ? COULEURS[c.nom] : '#9CA3AF',
                        borderRadius: '3px', transition: 'width 0.6s ease',
                      }} />
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Source des % à gauche, nos cas réels diagnostiqués à droite. */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '11px', color: '#6B7280' }}>
              <span>
                % :&nbsp;
                <span style={{ fontWeight: 700, color: source.startsWith('OMS') ? '#2563EB' : '#9CA3AF' }}>
                  {source === 'OMS (live)' ? 'OMS · données d\'actualité'
                    : source === 'OMS' ? 'données OMS'
                    : 'aucune donnée OMS'}
                </span>
              </span>
              <span style={{ fontWeight: 600, color: '#374151' }}>
                {total} cas diagnostiqué{total > 1 ? 's' : ''} · {maladie || 'toutes maladies'}
              </span>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default WorldMapCard;
