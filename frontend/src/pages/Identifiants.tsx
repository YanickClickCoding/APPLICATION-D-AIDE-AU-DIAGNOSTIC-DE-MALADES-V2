import React from 'react';
import { Shield, User, Stethoscope, Copy, CheckCircle } from 'lucide-react';

const Identifiants = () => {
  const [copiedField, setCopiedField] = React.useState<string | null>(null);

  const copyToClipboard = (text: string, field: string) => {
    navigator.clipboard.writeText(text);
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 2000);
  };

  const CredentialCard = ({ 
    title, 
    icon: Icon, 
    color, 
    bgColor, 
    credentials 
  }: { 
    title: string; 
    icon: any; 
    color: string; 
    bgColor: string; 
    credentials: Array<{ label: string; value: string; field: string }> 
  }) => (
    <div className="sp-card" style={{ marginBottom: '20px' }}>
      <div className="sp-card-header" style={{ background: bgColor, borderBottom: `2px solid ${color}` }}>
        <div className="sp-card-title" style={{ color: color }}>
          <Icon size={20} />
          {title}
        </div>
      </div>
      <div style={{ padding: '20px' }}>
        {credentials.map((cred, idx) => (
          <div key={idx} style={{ 
            marginBottom: idx < credentials.length - 1 ? '16px' : '0',
            padding: '12px',
            background: '#F9FAFB',
            borderRadius: '8px',
            border: '1px solid #E5E7EB'
          }}>
            <div style={{ 
              fontSize: '11px', 
              fontWeight: 600, 
              color: '#6B7280', 
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              marginBottom: '6px' 
            }}>
              {cred.label}
            </div>
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'space-between',
              gap: '12px'
            }}>
              <code style={{ 
                fontSize: '14px', 
                fontWeight: 600, 
                color: '#1F2937',
                fontFamily: "'Courier New', monospace",
                flex: 1
              }}>
                {cred.value}
              </code>
              <button
                onClick={() => copyToClipboard(cred.value, cred.field)}
                style={{
                  padding: '6px 10px',
                  background: copiedField === cred.field ? '#10B981' : '#4F46E5',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '12px',
                  fontWeight: 600,
                  transition: 'all 0.2s'
                }}
              >
                {copiedField === cred.field ? (
                  <>
                    <CheckCircle size={14} />
                    Copié
                  </>
                ) : (
                  <>
                    <Copy size={14} />
                    Copier
                  </>
                )}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <>
      <div className="sp-page-header sp-fade-in">
        <div>
          <h1 className="sp-page-title">Identifiants de Connexion</h1>
          <p className="sp-page-subtitle">Comptes de test pour le système GASA SAD</p>
        </div>
      </div>

      <div style={{ 
        padding: '20px', 
        background: '#FEF3C7', 
        border: '2px solid #F59E0B', 
        borderRadius: '12px',
        marginBottom: '24px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
          <Shield size={20} style={{ color: '#D97706' }} />
          <strong style={{ color: '#92400E', fontSize: '14px' }}>⚠️ ENVIRONNEMENT DE DÉVELOPPEMENT</strong>
        </div>
        <p style={{ color: '#78350F', fontSize: '13px', margin: 0 }}>
          Ces identifiants sont uniquement pour le développement et les tests. 
          En production, changez tous les mots de passe et activez l'authentification à deux facteurs (2FA).
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '20px' }}>
        
        {/* Administrateur */}
        <CredentialCard
          title="👨‍💼 Administrateur"
          icon={Shield}
          color="#DC2626"
          bgColor="#FEE2E2"
          credentials={[
            { label: 'Email', value: 'admin@santeplus.bj', field: 'admin-email' },
            { label: 'Mot de passe', value: 'admin123', field: 'admin-password' },
            { label: 'Rôle', value: 'admin', field: 'admin-role' }
          ]}
        />

      </div>

      {/* Médecins */}
      <div style={{ marginTop: '24px', marginBottom: '12px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#1F2937', marginBottom: '4px' }}>
          👨‍⚕️ Médecins (5 comptes)
        </h2>
        <p style={{ fontSize: '13px', color: '#6B7280' }}>
          Les médecins peuvent maintenant se connecter au système avec leurs identifiants.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '20px', marginBottom: '24px' }}>
        
        {/* Médecin 1 */}
        <CredentialCard
          title="Dr. AHOUANSOU Gérard Koffi - Médecine Générale"
          icon={Stethoscope}
          color="#4F46E5"
          bgColor="#EEF2FF"
          credentials={[
            { label: 'Email', value: 'gerard.ahouansou@sante.com', field: 'med1-email' },
            { label: 'Mot de passe', value: 'admin123', field: 'med1-password' },
            { label: 'Rôle', value: 'medecin', field: 'med1-role' }
          ]}
        />

        {/* Médecin 2 */}
        <CredentialCard
          title="Dr. DOSSOU Marie-Claire Afi - Pédiatrie"
          icon={Stethoscope}
          color="#4F46E5"
          bgColor="#EEF2FF"
          credentials={[
            { label: 'Email', value: 'marie.dossou@sante.com', field: 'med2-email' },
            { label: 'Mot de passe', value: 'admin123', field: 'med2-password' },
            { label: 'Rôle', value: 'medecin', field: 'med2-role' }
          ]}
        />

        {/* Médecin 3 */}
        <CredentialCard
          title="Dr. LEFEBVRE Jean-Baptiste - Cardiologie"
          icon={Stethoscope}
          color="#4F46E5"
          bgColor="#EEF2FF"
          credentials={[
            { label: 'Email', value: 'jean.lefebvre@sante.com', field: 'med3-email' },
            { label: 'Mot de passe', value: 'admin123', field: 'med3-password' },
            { label: 'Rôle', value: 'medecin', field: 'med3-role' }
          ]}
        />

        {/* Médecin 4 */}
        <CredentialCard
          title="Dr. BERNARD Sophie Marie - Pédiatrie"
          icon={Stethoscope}
          color="#4F46E5"
          bgColor="#EEF2FF"
          credentials={[
            { label: 'Email', value: 'sophie.bernard@sante.com', field: 'med4-email' },
            { label: 'Mot de passe', value: 'admin123', field: 'med4-password' },
            { label: 'Rôle', value: 'medecin', field: 'med4-role' }
          ]}
        />

        {/* Médecin 5 */}
        <CredentialCard
          title="Dr. PETIT Thomas André - Dermatologie"
          icon={Stethoscope}
          color="#4F46E5"
          bgColor="#EEF2FF"
          credentials={[
            { label: 'Email', value: 'thomas.petit@sante.com', field: 'med5-email' },
            { label: 'Mot de passe', value: 'admin123', field: 'med5-password' },
            { label: 'Rôle', value: 'medecin', field: 'med5-role' }
          ]}
        />

      </div>

      {/* Infirmiers */}
      <div style={{ marginTop: '24px', marginBottom: '12px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#1F2937', marginBottom: '4px' }}>
          👨‍⚕️ Infirmiers (4 comptes)
        </h2>
        <p style={{ fontSize: '13px', color: '#6B7280' }}>
          Les infirmiers peuvent maintenant se connecter au système avec leurs identifiants.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '20px' }}>
        
        {/* Infirmier 1 */}
        <CredentialCard
          title="KOUASSI Aya - Infirmier(ère)"
          icon={User}
          color="#10B981"
          bgColor="#D1FAE5"
          credentials={[
            { label: 'Email', value: 'aya.kouassi@sante.com', field: 'inf1-email' },
            { label: 'Mot de passe', value: 'admin123', field: 'inf1-password' },
            { label: 'Rôle', value: 'infirmier', field: 'inf1-role' }
          ]}
        />

        {/* Infirmier 2 */}
        <CredentialCard
          title="MENSAH Kofi - Infirmier(ère)"
          icon={User}
          color="#10B981"
          bgColor="#D1FAE5"
          credentials={[
            { label: 'Email', value: 'kofi.mensah@sante.com', field: 'inf2-email' },
            { label: 'Mot de passe', value: 'admin123', field: 'inf2-password' },
            { label: 'Rôle', value: 'infirmier', field: 'inf2-role' }
          ]}
        />

        {/* Infirmier 3 */}
        <CredentialCard
          title="DIALLO Fatoumata - Infirmier(ère)"
          icon={User}
          color="#10B981"
          bgColor="#D1FAE5"
          credentials={[
            { label: 'Email', value: 'fatoumata.diallo@sante.com', field: 'inf3-email' },
            { label: 'Mot de passe', value: 'admin123', field: 'inf3-password' },
            { label: 'Rôle', value: 'infirmier', field: 'inf3-role' }
          ]}
        />

        {/* Infirmier 4 */}
        <CredentialCard
          title="TRAORE Moussa - Infirmier(ère)"
          icon={User}
          color="#10B981"
          bgColor="#D1FAE5"
          credentials={[
            { label: 'Email', value: 'moussa.traore@sante.com', field: 'inf4-email' },
            { label: 'Mot de passe', value: 'admin123', field: 'inf4-password' },
            { label: 'Rôle', value: 'infirmier', field: 'inf4-role' }
          ]}
        />

      </div>

      {/* Instructions SQL */}
      <div className="sp-card" style={{ marginTop: '20px' }}>
        <div className="sp-card-header">
          <div className="sp-card-title">
            📝 Instructions SQL
          </div>
        </div>
        <div style={{ padding: '20px' }}>
          <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#1F2937', marginBottom: '12px' }}>
            Pour ajouter les rôles et utilisateurs à la base de données :
          </h3>
          <div style={{ 
            background: '#1F2937', 
            padding: '16px', 
            borderRadius: '8px',
            fontFamily: "'Courier New', monospace",
            fontSize: '13px',
            color: '#E5E7EB',
            overflowX: 'auto',
            marginBottom: '12px'
          }}>
            <div>mysql -u root -p sante_plus_ia &lt; backend/add_user_roles.sql</div>
          </div>
          <p style={{ color: '#6B7280', fontSize: '12px', marginBottom: '12px' }}>
            Ou copiez le contenu du fichier <code>backend/add_user_roles.sql</code> et exécutez-le dans votre client MySQL.
          </p>
          <div style={{ 
            padding: '12px', 
            background: '#FEF3C7', 
            border: '1px solid #F59E0B', 
            borderRadius: '8px',
            marginTop: '16px'
          }}>
            <strong style={{ color: '#92400E', fontSize: '13px' }}>⚠️ Note importante :</strong>
            <p style={{ color: '#78350F', fontSize: '12px', margin: '4px 0 0 0' }}>
              Ce script supprime les opérateurs et ajoute uniquement les rôles admin, médecin et infirmier.
            </p>
          </div>
        </div>
      </div>

    </>
  );
};

export default Identifiants;
