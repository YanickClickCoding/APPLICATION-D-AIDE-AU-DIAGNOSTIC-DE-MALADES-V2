import { AlertTriangle } from 'lucide-react';

interface Props {
  compact?: boolean;
}

export const MedicalDisclaimerBanner = ({ compact = false }: Props) => {
  if (compact) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '8px 14px',
        background: '#FFFBEB',
        border: '1px solid #FCD34D',
        borderRadius: '8px',
        fontSize: '12px',
        color: '#92400E',
      }}>
        <AlertTriangle size={14} style={{ flexShrink: 0, color: '#D97706' }} />
        <span>
          <strong>Aide à la décision uniquement.</strong> Les suggestions IA ne remplacent pas le jugement clinique du médecin.
        </span>
      </div>
    );
  }

  return (
    <div style={{
      display: 'flex',
      alignItems: 'flex-start',
      gap: '12px',
      padding: '14px 18px',
      background: 'linear-gradient(135deg, #FFFBEB, #FEF3C7)',
      border: '1px solid #FCD34D',
      borderLeft: '4px solid #F59E0B',
      borderRadius: '10px',
      fontSize: '13px',
      color: '#78350F',
      lineHeight: '1.5',
    }}>
      <AlertTriangle size={18} style={{ flexShrink: 0, color: '#D97706', marginTop: '1px' }} />
      <div>
        <strong style={{ display: 'block', marginBottom: '4px', color: '#92400E' }}>
          Outil d'aide au diagnostic — Avertissement médical
        </strong>
        Ce système utilise l'intelligence artificielle pour suggérer des diagnostics probables sur la base des symptômes et signes vitaux saisis.
        Ces suggestions sont fournies à titre indicatif uniquement et <strong>ne constituent pas un diagnostic médical définitif</strong>.
        Le diagnostic final reste sous la responsabilité exclusive du médecin, qui doit le valider en fonction de son examen clinique, des antécédents du patient et de tout autre élément clinique pertinent.
      </div>
    </div>
  );
};
