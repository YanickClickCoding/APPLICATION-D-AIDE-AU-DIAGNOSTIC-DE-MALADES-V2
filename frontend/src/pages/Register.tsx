import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { getUtilisateurs, saveUtilisateurs } from '../db';
import { User, Mail, Lock, Eye, EyeOff, UserPlus, AlertCircle } from 'lucide-react';
import type { Utilisateur } from '../types';

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    nom: '',
    prenoms: '',
    email: '',
    mot_de_passe: '',
    confirm_passe: ''
  });
  const [showPw1, setShowPw1] = useState(false);
  const [showPw2, setShowPw2] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    document.body.classList.add('sp-auth');
    return () => document.body.classList.remove('sp-auth');
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (formData.mot_de_passe !== formData.confirm_passe) {
      setError('Les mots de passe ne correspondent pas.');
      return;
    }

    if (formData.mot_de_passe.length < 8) {
      setError('Le mot de passe doit faire au moins 8 caractères.');
      return;
    }

    const users = getUtilisateurs();
    if (users.some(u => u.email === formData.email)) {
      setError('Cette adresse email est déjà utilisée.');
      return;
    }

    const newUser: Utilisateur = {
      utilisateur_id: Date.now(),
      nom: formData.nom,
      prenoms: formData.prenoms,
      email: formData.email,
      mot_de_passe: formData.mot_de_passe,
      role: 'infirmier',
      created_at: new Date().toISOString()
    };

    saveUtilisateurs([...users, newUser]);
    navigate('/login', { state: { success: 'Compte créé avec succès ! Connectez-vous.' } });
  };

  return (
    <div className="sp-auth-container" style={{ maxWidth: '500px' }}>
      <div className="sp-auth-logo">
        <div className="sp-auth-logo-icon">
          <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
            <path d="M18 4v28M4 18h28" stroke="white" strokeWidth="4" strokeLinecap="round"/>
            <circle cx="18" cy="18" r="7" stroke="white" strokeWidth="2.5" fill="none"/>
          </svg>
        </div>
        <div className="sp-auth-logo-name">SANTÉ PLUS</div>
        <div className="sp-auth-logo-sub">Clinique Privée · Cotonou, Bénin</div>
      </div>

      <div className="sp-auth-card sp-fade-in">
        <h1 className="sp-auth-title">Créer un compte</h1>
        <p className="sp-auth-subtitle">Renseignez vos informations pour accéder au système</p>

        {error && (
          <div className="sp-alert error" style={{ marginBottom: '18px' }}>
            <AlertCircle size={18} />
            <div>{error}</div>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '14px' }}>
            <div className="sp-form-group">
              <label className="sp-form-label">Nom <span className="required">*</span></label>
              <div className="sp-input-icon-wrap">
                <User className="sp-input-icon" />
                <input 
                  type="text" 
                  className="sp-form-input" 
                  placeholder="NOM"
                  value={formData.nom}
                  onChange={e => setFormData({...formData, nom: e.target.value.toUpperCase()})}
                  required 
                />
              </div>
            </div>
            <div className="sp-form-group">
              <label className="sp-form-label">Prénom(s) <span className="required">*</span></label>
              <div className="sp-input-icon-wrap">
                <User className="sp-input-icon" />
                <input 
                  type="text" 
                  className="sp-form-input" 
                  placeholder="Prénom(s)"
                  value={formData.prenoms}
                  onChange={e => setFormData({...formData, prenoms: e.target.value})}
                  required 
                />
              </div>
            </div>
          </div>

          <div className="sp-form-group" style={{ marginBottom: '14px' }}>
            <label className="sp-form-label">Adresse email <span className="required">*</span></label>
            <div className="sp-input-icon-wrap">
              <Mail className="sp-input-icon" />
              <input 
                type="email" 
                className="sp-form-input" 
                placeholder="votre@email.com" 
                value={formData.email}
                onChange={e => setFormData({...formData, email: e.target.value})}
                required 
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '22px' }}>
            <div className="sp-form-group">
              <label className="sp-form-label">Mot de passe <span className="required">*</span></label>
              <div className="sp-input-icon-wrap">
                <Lock className="sp-input-icon" />
                <input 
                  type={showPw1 ? "text" : "password"} 
                  className="sp-form-input" 
                  placeholder="••••••••" 
                  value={formData.mot_de_passe}
                  onChange={e => setFormData({...formData, mot_de_passe: e.target.value})}
                  required 
                  style={{ paddingRight: '40px' }}
                />
                <button type="button" className="sp-pw-toggle" onClick={() => setShowPw1(!showPw1)}>
                  {showPw1 ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
              <small style={{ fontSize: '11px', color: 'var(--sp-gray-400)' }}>Min. 8 caractères</small>
            </div>
            <div className="sp-form-group">
              <label className="sp-form-label">Confirmation <span className="required">*</span></label>
              <div className="sp-input-icon-wrap">
                <Lock className="sp-input-icon" />
                <input 
                  type={showPw2 ? "text" : "password"} 
                  className="sp-form-input" 
                  placeholder="••••••••" 
                  value={formData.confirm_passe}
                  onChange={e => setFormData({...formData, confirm_passe: e.target.value})}
                  required 
                  style={{ paddingRight: '40px' }}
                />
                <button type="button" className="sp-pw-toggle" onClick={() => setShowPw2(!showPw2)}>
                  {showPw2 ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
            </div>
          </div>

          <button type="submit" className="sp-btn sp-btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '12px' }}>
            <UserPlus size={18} />
            Créer mon compte
          </button>
        </form>

        <div className="sp-divider">ou</div>

        <div style={{ textAlign: 'center', fontSize: '13.5px', color: 'var(--sp-gray-500)' }}>
          Déjà un compte ?{' '}
          <Link to="/login" style={{ color: 'var(--sp-primary)', fontWeight: 600, textDecoration: 'none' }}>
            Se connecter
          </Link>
        </div>
      </div>

      <div style={{ textAlign: 'center', marginTop: '20px', fontSize: '11.5px', color: 'rgba(255,255,255,0.4)' }}>
        © {new Date().getFullYear()} SANTÉ PLUS · Tous droits réservés
      </div>
    </div>
  );
};

export default Register;
