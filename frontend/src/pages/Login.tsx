import React, { useState, useEffect } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getUtilisateurs } from '../db';
import { Mail, Lock, Eye, EyeOff, LogIn, AlertCircle, CheckCircle } from 'lucide-react';

const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [success] = useState(location.state?.success || '');

  useEffect(() => {
    document.body.classList.add('sp-auth');
    return () => document.body.classList.remove('sp-auth');
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    const users = getUtilisateurs();
    const user = users.find(u => u.email === email && u.mot_de_passe === password);
    
    if (user) {
      login(user);
      navigate('/');
    } else {
      setError('Email ou mot de passe incorrect.');
    }
  };

  return (
    <div className="sp-auth-container">
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
        <h1 className="sp-auth-title">Bon retour 👋</h1>
        <p className="sp-auth-subtitle">Connectez-vous pour accéder à votre espace</p>

        {error && (
          <div className="sp-alert error" style={{ marginBottom: '18px' }}>
            <AlertCircle size={18} />
            <div>{error}</div>
          </div>
        )}

        {success && (
          <div className="sp-alert success" style={{ marginBottom: '18px' }}>
            <CheckCircle size={18} />
            <span>{success}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="sp-form-group" style={{ marginBottom: '15px' }}>
            <label className="sp-form-label">Adresse email</label>
            <div className="sp-input-icon-wrap">
              <Mail className="sp-input-icon" />
              <input 
                type="email" 
                className="sp-form-input" 
                placeholder="votre@email.com" 
                value={email}
                onChange={e => setEmail(e.target.value)}
                required 
              />
            </div>
          </div>

          <div className="sp-form-group" style={{ marginBottom: '24px' }}>
            <label className="sp-form-label">Mot de passe</label>
            <div className="sp-input-icon-wrap">
              <Lock className="sp-input-icon" />
              <input 
                type={showPassword ? "text" : "password"} 
                className="sp-form-input" 
                placeholder="••••••••" 
                value={password}
                onChange={e => setPassword(e.target.value)}
                required 
                style={{ paddingRight: '40px' }}
              />
              <button 
                type="button" 
                className="sp-pw-toggle" 
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
              </button>
            </div>
          </div>

          <button type="submit" className="sp-btn sp-btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '12px', fontSize: '14.5px' }}>
            <LogIn size={18} />
            Se connecter
          </button>
        </form>

        <div className="sp-divider">ou</div>

        <div style={{ textAlign: 'center', fontSize: '13.5px', color: 'var(--sp-gray-500)' }}>
          Pas encore de compte ?{' '}
          <Link to="/register" style={{ color: 'var(--sp-primary)', fontWeight: 600, textDecoration: 'none' }}>
            S'inscrire
          </Link>
        </div>
      </div>

      <div style={{ textAlign: 'center', marginTop: '16px', fontSize: '11.5px', color: 'rgba(255,255,255,0.3)' }}>
        © {new Date().getFullYear()} SANTÉ PLUS · Système de gestion des consultations
      </div>
    </div>
  );
};

export default Login;
