import { useState } from 'react';
import { User, Mail, Shield, Lock, Save, KeyRound } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Toast';
import { authAPI } from '../services/api';

export default function Profil() {
  const { user, token, updateUser } = useAuth();
  const { showToast } = useToast();

  // ── Profil ──
  const [nom, setNom] = useState(user?.nom || '');
  const [prenoms, setPrenoms] = useState(user?.prenoms || '');
  const [email, setEmail] = useState(user?.email || '');
  const [savingProfile, setSavingProfile] = useState(false);

  // ── Mot de passe ──
  const [ancienMdp, setAncienMdp] = useState('');
  const [nouveauMdp, setNouveauMdp] = useState('');
  const [confirmMdp, setConfirmMdp] = useState('');
  const [savingPwd, setSavingPwd] = useState(false);

  const roleLabel =
    user?.role === 'admin' ? 'Administrateur' : user?.role === 'medecin' ? 'Médecin' : 'Infirmier';

  // Le profil a-t-il été modifié par rapport aux valeurs courantes de l'utilisateur ?
  const profilModifie =
    nom.trim() !== (user?.nom || '') ||
    prenoms.trim() !== (user?.prenoms || '') ||
    email.trim() !== (user?.email || '');

  // Les trois champs mot de passe sont-ils renseignés ?
  const pwdRempli = ancienMdp.length > 0 && nouveauMdp.length > 0 && confirmMdp.length > 0;

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    if (!nom.trim() || !prenoms.trim() || !email.trim()) {
      showToast('Tous les champs du profil sont requis', 'error');
      return;
    }
    setSavingProfile(true);
    try {
      const updated = await authAPI.updateProfile(token, {
        nom: nom.trim(),
        prenoms: prenoms.trim(),
        email: email.trim(),
      });
      updateUser({ nom: updated.nom, prenoms: updated.prenoms, email: updated.email });
      showToast('Profil mis à jour avec succès', 'success');
    } catch (err: any) {
      showToast(err?.message || 'Erreur lors de la mise à jour du profil', 'error');
    } finally {
      setSavingProfile(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    if (nouveauMdp.length < 8) {
      showToast('Le nouveau mot de passe doit faire au moins 8 caractères', 'error');
      return;
    }
    if (nouveauMdp !== confirmMdp) {
      showToast('La confirmation ne correspond pas au nouveau mot de passe', 'error');
      return;
    }
    setSavingPwd(true);
    try {
      await authAPI.changePassword(token, {
        ancien_mot_de_passe: ancienMdp,
        nouveau_mot_de_passe: nouveauMdp,
      });
      showToast('Mot de passe modifié avec succès', 'success');
      setAncienMdp('');
      setNouveauMdp('');
      setConfirmMdp('');
    } catch (err: any) {
      showToast(err?.message || 'Erreur lors du changement de mot de passe', 'error');
    } finally {
      setSavingPwd(false);
    }
  };

  const inputStyle: React.CSSProperties = {
    width: '100%', padding: '10px 12px', borderRadius: '8px',
    border: '1px solid #D1D5DB', fontSize: '14px', marginBottom: '4px',
  };
  const labelStyle: React.CSSProperties = {
    display: 'flex', alignItems: 'center', gap: '6px',
    fontSize: '12px', fontWeight: 600, color: '#6B7280', marginBottom: '6px',
  };

  return (
    <>
      <div className="sp-page-header sp-fade-in">
        <div>
          <h1 className="sp-page-title">Mon Profil</h1>
          <p className="sp-page-subtitle">Gérez vos informations personnelles et votre mot de passe</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 380px), 1fr))', gap: '20px' }}>

        {/* ── Informations du profil ── */}
        <div className="sp-card sp-fade-in">
          <div className="sp-card-header">
            <div className="sp-card-title"><User size={18} /> Informations personnelles</div>
          </div>
          <form onSubmit={handleSaveProfile} style={{ padding: '24px' }}>
            <div style={{ marginBottom: '16px' }}>
              <label style={labelStyle}><User size={13} /> Nom</label>
              <input style={inputStyle} value={nom} onChange={e => setNom(e.target.value)} maxLength={100} />
            </div>
            <div style={{ marginBottom: '16px' }}>
              <label style={labelStyle}><User size={13} /> Prénoms</label>
              <input style={inputStyle} value={prenoms} onChange={e => setPrenoms(e.target.value)} maxLength={150} />
            </div>
            <div style={{ marginBottom: '16px' }}>
              <label style={labelStyle}><Mail size={13} /> Email</label>
              <input style={inputStyle} type="email" value={email} onChange={e => setEmail(e.target.value)} maxLength={200} />
            </div>
            <div style={{ marginBottom: '20px' }}>
              <label style={labelStyle}><Shield size={13} /> Rôle</label>
              <div style={{ ...inputStyle, background: '#F3F4F6', color: '#6B7280', display: 'flex', alignItems: 'center' }}>
                {roleLabel} <span style={{ fontSize: '11px', marginLeft: '8px' }}>(non modifiable)</span>
              </div>
            </div>
            <button type="submit" className="sp-btn sp-btn-primary" disabled={savingProfile || !profilModifie}
              style={{ display: 'flex', alignItems: 'center', gap: '8px', opacity: (savingProfile || !profilModifie) ? 0.5 : 1, cursor: (savingProfile || !profilModifie) ? 'not-allowed' : 'pointer' }}>
              <Save size={15} /> {savingProfile ? 'Enregistrement…' : 'Enregistrer le profil'}
            </button>
          </form>
        </div>

        {/* ── Changement de mot de passe ── */}
        <div className="sp-card sp-fade-in">
          <div className="sp-card-header">
            <div className="sp-card-title"><KeyRound size={18} /> Changer le mot de passe</div>
          </div>
          <form onSubmit={handleChangePassword} style={{ padding: '24px' }}>
            <div style={{ marginBottom: '16px' }}>
              <label style={labelStyle}><Lock size={13} /> Mot de passe actuel</label>
              <input style={inputStyle} type="password" value={ancienMdp} onChange={e => setAncienMdp(e.target.value)} required autoComplete="current-password" />
            </div>
            <div style={{ marginBottom: '16px' }}>
              <label style={labelStyle}><Lock size={13} /> Nouveau mot de passe</label>
              <input style={inputStyle} type="password" value={nouveauMdp} onChange={e => setNouveauMdp(e.target.value)} required autoComplete="new-password" />
              <p style={{ fontSize: '11px', color: '#9CA3AF', margin: '2px 0 0' }}>Au moins 8 caractères.</p>
            </div>
            <div style={{ marginBottom: '20px' }}>
              <label style={labelStyle}><Lock size={13} /> Confirmer le nouveau mot de passe</label>
              <input style={inputStyle} type="password" value={confirmMdp} onChange={e => setConfirmMdp(e.target.value)} required autoComplete="new-password" />
            </div>
            <button type="submit" className="sp-btn sp-btn-primary" disabled={savingPwd || !pwdRempli}
              style={{ display: 'flex', alignItems: 'center', gap: '8px', opacity: (savingPwd || !pwdRempli) ? 0.5 : 1, cursor: (savingPwd || !pwdRempli) ? 'not-allowed' : 'pointer' }}>
              <KeyRound size={15} /> {savingPwd ? 'Modification…' : 'Modifier le mot de passe'}
            </button>
          </form>
        </div>

      </div>
    </>
  );
}
