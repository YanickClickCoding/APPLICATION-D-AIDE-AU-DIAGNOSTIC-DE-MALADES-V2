import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useToast } from '../components/Toast';
import { authAPI } from '../services/api';
import { Mail, Lock, KeyRound, ArrowLeft, Loader, Info } from 'lucide-react';

export default function MotDePasseOublie() {
  const { showToast } = useToast();
  const navigate = useNavigate();

  const [step, setStep] = useState<'email' | 'reset'>('email');
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [nouveauMdp, setNouveauMdp] = useState('');
  const [confirmMdp, setConfirmMdp] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    document.body.classList.add('sp-auth');
    return () => document.body.classList.remove('sp-auth');
  }, []);

  const handleRequestCode = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loading) return;
    setLoading(true);
    try {
      const res = await authAPI.forgotPassword(email.trim());
      showToast(res.message, 'info');
      setStep('reset');
    } catch (err: any) {
      showToast(err?.message || 'Erreur lors de la demande de code', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loading) return;
    if (nouveauMdp.length < 8) {
      showToast('Le mot de passe doit faire au moins 8 caractères', 'error');
      return;
    }
    if (nouveauMdp !== confirmMdp) {
      showToast('La confirmation ne correspond pas', 'error');
      return;
    }
    setLoading(true);
    try {
      await authAPI.resetPassword({
        email: email.trim(),
        code: code.trim(),
        nouveau_mot_de_passe: nouveauMdp,
      });
      showToast('Mot de passe réinitialisé. Vous pouvez vous connecter.', 'success');
      navigate('/login', { replace: true });
    } catch (err: any) {
      showToast(err?.message || 'Erreur lors de la réinitialisation', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="sp-auth-bg-image" />
      <div className="sp-auth-container">
        <div className="sp-auth-logo">
          <div className="sp-auth-logo-icon">
            <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
              <path d="M18 4v28M4 18h28" stroke="white" strokeWidth="4" strokeLinecap="round" />
              <circle cx="18" cy="18" r="7" stroke="white" strokeWidth="2" fill="none" />
            </svg>
          </div>
          <div className="sp-auth-logo-name">GASA SAD</div>
          <div className="sp-auth-logo-sub">Système d'Aide au Diagnostic</div>
        </div>

        <div className="sp-auth-card sp-fade-in">
          <h1 className="sp-auth-title">Mot de passe oublié</h1>
          <p className="sp-auth-subtitle">
            {step === 'email'
              ? 'Saisissez votre email pour recevoir un code de réinitialisation.'
              : 'Saisissez le code et votre nouveau mot de passe.'}
          </p>

          {step === 'reset' && (
            <div className="sp-alert" style={{ marginBottom: '18px', background: '#EFF6FF', border: '1px solid #BFDBFE', color: '#1E40AF', display: 'flex', alignItems: 'flex-start', gap: '8px', padding: '10px 14px', borderRadius: '8px' }}>
              <Info size={16} style={{ flexShrink: 0, marginTop: '1px' }} />
              <span style={{ fontSize: '13px' }}>
                Le code de confirmation est affiché dans les <strong>logs du serveur backend</strong> (application de développement).
              </span>
            </div>
          )}

          {step === 'email' ? (
            <form onSubmit={handleRequestCode}>
              <div className="sp-form-group" style={{ marginBottom: '24px' }}>
                <label className="sp-form-label">Adresse email</label>
                <div className="sp-input-icon-wrap">
                  <Mail className="sp-input-icon" />
                  <input
                    type="email" className="sp-form-input" placeholder="votre@email.com"
                    value={email} onChange={e => setEmail(e.target.value)} required disabled={loading}
                  />
                </div>
              </div>
              <button type="submit" className="sp-btn sp-btn-primary"
                style={{ width: '100%', justifyContent: 'center', padding: '12px', fontSize: '14.5px' }} disabled={loading}>
                {loading ? (<><Loader size={18} className="animate-spin" /> Envoi…</>) : (<><KeyRound size={18} /> Recevoir un code</>)}
              </button>
            </form>
          ) : (
            <form onSubmit={handleReset}>
              <div className="sp-form-group" style={{ marginBottom: '15px' }}>
                <label className="sp-form-label">Code de réinitialisation</label>
                <div className="sp-input-icon-wrap">
                  <KeyRound className="sp-input-icon" />
                  <input
                    type="text" className="sp-form-input" placeholder="123456" inputMode="numeric"
                    value={code} onChange={e => setCode(e.target.value)} required disabled={loading} maxLength={6}
                  />
                </div>
              </div>
              <div className="sp-form-group" style={{ marginBottom: '15px' }}>
                <label className="sp-form-label">Nouveau mot de passe</label>
                <div className="sp-input-icon-wrap">
                  <Lock className="sp-input-icon" />
                  <input
                    type="password" className="sp-form-input" placeholder="••••••••" autoComplete="new-password"
                    value={nouveauMdp} onChange={e => setNouveauMdp(e.target.value)} required disabled={loading}
                  />
                </div>
              </div>
              <div className="sp-form-group" style={{ marginBottom: '24px' }}>
                <label className="sp-form-label">Confirmer le mot de passe</label>
                <div className="sp-input-icon-wrap">
                  <Lock className="sp-input-icon" />
                  <input
                    type="password" className="sp-form-input" placeholder="••••••••" autoComplete="new-password"
                    value={confirmMdp} onChange={e => setConfirmMdp(e.target.value)} required disabled={loading}
                  />
                </div>
              </div>
              <button type="submit" className="sp-btn sp-btn-primary"
                style={{ width: '100%', justifyContent: 'center', padding: '12px', fontSize: '14.5px' }} disabled={loading}>
                {loading ? (<><Loader size={18} className="animate-spin" /> Réinitialisation…</>) : (<><Lock size={18} /> Réinitialiser le mot de passe</>)}
              </button>
              <button type="button" onClick={() => setStep('email')}
                style={{ width: '100%', marginTop: '10px', background: 'none', border: 'none', color: 'var(--sp-gray-500)', fontSize: '13px', cursor: 'pointer' }}>
                Renvoyer un code
              </button>
            </form>
          )}

          <div style={{ textAlign: 'center', marginTop: '16px', fontSize: '13.5px' }}>
            <Link to="/login" style={{ color: 'var(--sp-primary)', fontWeight: 600, textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
              <ArrowLeft size={14} /> Retour à la connexion
            </Link>
          </div>
        </div>

        <div style={{ textAlign: 'center', marginTop: '16px', fontSize: '11.5px', color: 'rgba(255,255,255,0.3)' }}>
          © {new Date().getFullYear()} GASA SAD · Système d'Aide au Diagnostic
        </div>
      </div>
    </>
  );
}
