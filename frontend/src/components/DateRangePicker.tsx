import React, { useState, useRef, useEffect } from 'react';
import { Calendar, ChevronLeft, ChevronRight, Filter } from 'lucide-react';

interface DateRangePickerProps {
  dateDebut: string; // ISO YYYY-MM-DD, '' = pas de borne
  dateFin: string;
  onChange: (debut: string, fin: string) => void;
  loading?: boolean;
}

const JOURS_SEMAINE = ['Lu', 'Ma', 'Me', 'Je', 'Ve', 'Sa', 'Di'];

const toISO = (annee: number, mois: number, jour: number) =>
  `${annee}-${String(mois + 1).padStart(2, '0')}-${String(jour).padStart(2, '0')}`;

const formatLong = (iso: string) =>
  new Date(`${iso}T00:00:00`).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' });

const capitalize = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

const titreMois = (annee: number, mois: number) =>
  capitalize(new Date(annee, mois).toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' }));

/** Grille d'un mois : jours de la plage en foncé, bornes en noir arrondi */
const MonthGrid = ({
  annee, mois, debut, fin, onPick, onHover,
}: {
  annee: number;
  mois: number;
  debut: string;
  fin: string;
  onPick: (iso: string) => void;
  onHover: (iso: string | null) => void;
}) => {
  const nbJours = new Date(annee, mois + 1, 0).getDate();
  const decalage = (new Date(annee, mois, 1).getDay() + 6) % 7; // semaine commençant lundi
  const cells: (number | null)[] = [
    ...Array(decalage).fill(null),
    ...Array.from({ length: nbJours }, (_, i) => i + 1),
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 34px)', rowGap: '2px', justifyContent: 'center' }}>
      {JOURS_SEMAINE.map(j => (
        <div key={j} style={{ width: 34, height: 28, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px', fontWeight: 600, color: '#9CA3AF' }}>
          {j}
        </div>
      ))}
      {cells.map((jour, i) => {
        if (jour === null) return <div key={`v-${i}`} />;
        const iso = toISO(annee, mois, jour);
        const estDebut = debut !== '' && iso === debut;
        const estFin = fin !== '' && iso === fin;
        const dansPlage = debut !== '' && fin !== '' && iso > debut && iso < fin;
        const style: React.CSSProperties = {
          width: 34,
          height: 34,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '13px',
          cursor: 'pointer',
          userSelect: 'none',
          fontWeight: estDebut || estFin ? 700 : 500,
          ...(estDebut || estFin
            ? { background: '#1F2430', color: '#fff', borderRadius: '10px' }
            : dansPlage
              ? { background: '#4B5563', color: '#fff', borderRadius: '4px' }
              : { color: '#374151', borderRadius: '8px' }),
        };
        return (
          <div
            key={iso}
            style={style}
            onClick={() => onPick(iso)}
            onMouseEnter={() => onHover(iso)}
            onMouseLeave={() => onHover(null)}
          >
            {jour}
          </div>
        );
      })}
    </div>
  );
};

/**
 * Barre de période cliquable + calendrier déroulant double-mois avec sélection de plage.
 * Premier clic = début, second clic = fin (inversion automatique si antérieure).
 */
const DateRangePicker = ({ dateDebut, dateFin, onChange, loading = false }: DateRangePickerProps) => {
  const [open, setOpen] = useState(false);
  const [draftStart, setDraftStart] = useState<string | null>(null);
  const [hover, setHover] = useState<string | null>(null);
  // Premier mois affiché (le second est le suivant)
  const [vue, setVue] = useState(() => {
    const base = dateDebut ? new Date(`${dateDebut}T00:00:00`) : new Date();
    return { annee: base.getFullYear(), mois: base.getMonth() };
  });
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
        setDraftStart(null);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const ouvrir = () => {
    if (!open) {
      const base = dateDebut ? new Date(`${dateDebut}T00:00:00`) : new Date();
      setVue({ annee: base.getFullYear(), mois: base.getMonth() });
      setDraftStart(null);
    }
    setOpen(o => !o);
  };

  const naviguer = (delta: number) => {
    setVue(v => {
      const d = new Date(v.annee, v.mois + delta);
      return { annee: d.getFullYear(), mois: d.getMonth() };
    });
  };

  const pick = (iso: string) => {
    if (draftStart === null) {
      setDraftStart(iso);
    } else {
      const [a, b] = iso < draftStart ? [iso, draftStart] : [draftStart, iso];
      onChange(a, b);
      setDraftStart(null);
      setOpen(false);
    }
  };

  // Plage affichée dans les grilles : aperçu du brouillon (avec survol) sinon plage validée
  let affDebut = dateDebut;
  let affFin = dateFin;
  if (draftStart !== null) {
    if (hover !== null && hover !== draftStart) {
      [affDebut, affFin] = hover < draftStart ? [hover, draftStart] : [draftStart, hover];
    } else {
      affDebut = draftStart;
      affFin = draftStart;
    }
  }

  const moisSuivant = new Date(vue.annee, vue.mois + 1);
  const libelle = dateDebut && dateFin
    ? `${formatLong(dateDebut)} – ${formatLong(dateFin)}`
    : 'Toute la période';

  return (
    <div ref={ref} style={{ position: 'relative', marginBottom: '16px' }} className="sp-fade-in">
      {/* Barre cliquable */}
      <div
        className="sp-card"
        onClick={ouvrir}
        style={{ padding: '12px 18px', display: 'flex', alignItems: 'center', gap: '14px', cursor: 'pointer' }}
      >
        <span style={{ width: 32, height: 32, borderRadius: '8px', background: '#F3F4F6', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
          <Calendar size={16} style={{ color: '#374151' }} />
        </span>
        <span style={{ fontWeight: 700, fontSize: '14px', color: '#1F2937' }}>{libelle}</span>
        <span style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '10px' }}>
          {loading && (
            <span style={{ width: 14, height: 14, border: '2px solid #E5E7EB', borderTopColor: '#4F46E5', borderRadius: '50%', animation: 'spin 0.8s linear infinite', display: 'inline-block' }} />
          )}
          <span style={{ position: 'relative', width: 36, height: 36, borderRadius: '10px', border: '1px solid #E5E7EB', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Filter size={15} style={{ color: '#374151' }} />
            {(dateDebut || dateFin) && (
              <span style={{ position: 'absolute', top: '-3px', right: '-3px', width: 9, height: 9, borderRadius: '50%', background: '#FBBF24' }} />
            )}
          </span>
        </span>
      </div>

      {/* Calendrier déroulant double-mois */}
      {open && (
        <div style={{ position: 'absolute', top: 'calc(100% + 8px)', left: 0, zIndex: 1000, background: '#fff', borderRadius: '14px', boxShadow: '0 12px 36px rgba(0,0,0,0.14)', border: '1px solid #E5E7EB', padding: '16px 18px' }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}>
            <button
              onClick={() => naviguer(-1)}
              style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '4px', display: 'flex', color: '#374151' }}
              title="Mois précédent"
            >
              <ChevronLeft size={18} />
            </button>
            <span style={{ flex: 1, textAlign: 'center', fontWeight: 700, fontSize: '14px', color: '#111827' }}>
              {titreMois(vue.annee, vue.mois)}
            </span>
            <span style={{ flex: 1, textAlign: 'center', fontWeight: 700, fontSize: '14px', color: '#111827' }}>
              {titreMois(moisSuivant.getFullYear(), moisSuivant.getMonth())}
            </span>
            <button
              onClick={() => naviguer(1)}
              style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '4px', display: 'flex', color: '#374151' }}
              title="Mois suivant"
            >
              <ChevronRight size={18} />
            </button>
          </div>
          <div style={{ display: 'flex', gap: '22px' }}>
            <MonthGrid
              annee={vue.annee} mois={vue.mois}
              debut={affDebut} fin={affFin}
              onPick={pick} onHover={setHover}
            />
            <MonthGrid
              annee={moisSuivant.getFullYear()} mois={moisSuivant.getMonth()}
              debut={affDebut} fin={affFin}
              onPick={pick} onHover={setHover}
            />
          </div>
          <div style={{ marginTop: '10px', fontSize: '11px', color: '#9CA3AF', textAlign: 'center' }}>
            {draftStart
              ? 'Cliquez sur la date de fin de la période'
              : 'Cliquez sur la date de début de la période'}
          </div>
        </div>
      )}
    </div>
  );
};

export default DateRangePicker;
