import React, { useEffect, lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { triggerNavigationGuard } from './utils/navigationGuard';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider } from './components/Toast';
import { ConfirmProvider } from './components/ConfirmDialog';
import { initDB } from './db';
import { Users, Calendar, LogOut, UserCheck, Clock, Settings, Brain, User, Bell, UserPlus, Database, BarChart2, TrendingUp } from 'lucide-react';
import { adminAPI } from './services/api';

// Pages — chargement différé pour réduire le bundle initial (~60%)
const Login             = lazy(() => import('./pages/Login'));
const Dashboard         = lazy(() => import('./pages/DashboardNew'));
const Consultations     = lazy(() => import('./pages/Consultations'));
const ConsultationWorkflow = lazy(() => import('./pages/ConsultationWorkflow'));
const ConsultationDetails  = lazy(() => import('./pages/ConsultationDetails'));
const PersonnelMedical  = lazy(() => import('./pages/PersonnelMedical'));
const Utilisateurs      = lazy(() => import('./pages/Utilisateurs'));
const Register          = lazy(() => import('./pages/Register'));
const AdminSystem       = lazy(() => import('./pages/AdminSystem'));
const AdminDataset      = lazy(() => import('./pages/AdminDataset'));
const AdminML           = lazy(() => import('./pages/AdminML'));
const DossierPatient    = lazy(() => import('./pages/DossierPatient'));
const MesPatients       = lazy(() => import('./pages/MesPatients'));
const DiagnosticsIA     = lazy(() => import('./pages/DiagnosticsIA'));
const Analytics         = lazy(() => import('./pages/Analytics'));
const Profil            = lazy(() => import('./pages/Profil'));
const MotDePasseOublie  = lazy(() => import('./pages/MotDePasseOublie'));

const PageLoader = () => (
  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '60vh' }}>
    <div style={{ textAlign: 'center', color: '#6B7280' }}>
      <div style={{ width: 40, height: 40, border: '3px solid #E5E7EB', borderTop: '3px solid #4F46E5', borderRadius: '50%', animation: 'spin 0.8s linear infinite', margin: '0 auto 12px' }} />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      Chargement…
    </div>
  </div>
);

const PrivateRoute = ({
  children,
  adminOnly = false,
  medicalOnly = false,
  noInfirmier = false,
  noAdmin = false,
}: {
  children: React.ReactNode;
  adminOnly?: boolean;
  medicalOnly?: boolean;
  noInfirmier?: boolean;
  /** Si true, l'admin est redirigé vers son espace — il n'a pas accès aux données cliniques */
  noAdmin?: boolean;
}) => {
  const { isAuthenticated, isAdmin, user } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (adminOnly && !isAdmin) return <Navigate to="/" replace />;
  // L'admin n'a aucun accès aux pages cliniques (consultations, diagnostics, patients)
  if (noAdmin && isAdmin) return <Navigate to="/admin/systeme" replace />;
  if (medicalOnly && !isAdmin && user?.role !== 'medecin' && user?.role !== 'infirmier') return <Navigate to="/consultations" replace />;
  if (noInfirmier && user?.role !== 'medecin') return <Navigate to="/" replace />;
  return <>{children}</>;
};

const Sidebar = ({ isOpen, onClose }: { isOpen: boolean, onClose: () => void }) => {
  const location = useLocation();
  const { user, isAdmin, logout } = useAuth();
  const nav = useNavigate();
  const [showConfirm, setShowConfirm] = React.useState(false);

  const navTo = (e: React.MouseEvent, to: string) => {
    e.preventDefault();
    if (triggerNavigationGuard(to)) { nav(to); onClose(); }
  };
  
  useEffect(() => {
    // @ts-ignore
    if (window.feather) {
      // @ts-ignore
      window.feather.replace();
    }
  }, [location.pathname]); // Seulement quand la route change
  
  return (
    <div className={`sp-sidebar ${isOpen ? 'open' : ''}`} id="sidebar">
      <div className="sp-logo-area">
          <div className="sp-logo-icon">
              <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                  <rect width="32" height="32" rx="10" fill="white" fillOpacity="0.15"/>
                  <path d="M16 6v20M6 16h20" stroke="white" strokeWidth="3.5" strokeLinecap="round"/>
                  <circle cx="16" cy="16" r="5" stroke="white" strokeWidth="2" fill="none"/>
              </svg>
          </div>
          <div>
              <div className="sp-logo-name">GASA SAD</div>
              <div className="sp-logo-sub">Système d'Aide au Diagnostic</div>
          </div>
      </div>

      <div className="sp-nav-section">
          <div className="sp-nav-label">Navigation</div>
          <nav>
              {/* Tableau de bord */}
              <a href="/" className={`sp-nav-item ${location.pathname === '/' ? 'active' : ''}`} onClick={e => navTo(e, '/')}>
                  <i data-feather="grid"></i>
                  <span>Tableau de bord</span>
              </a>

              {/* Analytique — séries quotidiennes, accessible à tous les rôles */}
              <a href="/analytique" className={`sp-nav-item ${location.pathname === '/analytique' ? 'active' : ''}`} onClick={e => navTo(e, '/analytique')}>
                  <TrendingUp size={18} />
                  <span>Analytique</span>
              </a>

              {/* Navigation clinique — médecin et infirmier UNIQUEMENT, admin exclu */}
              {!isAdmin && (
                <>
                  <a href="/consultations" className={`sp-nav-item ${location.pathname === '/consultations' ? 'active' : ''}`} onClick={e => navTo(e, '/consultations')}>
                      <Calendar size={18} />
                      <span>Consultations</span>
                  </a>
                  {user?.role === 'medecin' && (
                    <>
                      <a href="/mes-patients" className={`sp-nav-item ${location.pathname === '/mes-patients' ? 'active' : ''}`} onClick={e => navTo(e, '/mes-patients')}>
                          <User size={18} />
                          <span>Mes Patients</span>
                      </a>
                      <a href="/diagnostics" className={`sp-nav-item ${location.pathname === '/diagnostics' ? 'active' : ''}`} onClick={e => navTo(e, '/diagnostics')}>
                          <Brain size={18} />
                          <span>Diagnostics IA</span>
                      </a>
                    </>
                  )}
                </>
              )}

              {/* Navigation administrative — admin UNIQUEMENT */}
              {isAdmin && (
                <>
                  <a href="/personnel" className={`sp-nav-item ${location.pathname === '/personnel' ? 'active' : ''}`} onClick={e => navTo(e, '/personnel')}>
                      <UserCheck size={18} />
                      <span>Personnel Médical</span>
                  </a>
                  <a href="/utilisateurs" className={`sp-nav-item ${location.pathname === '/utilisateurs' ? 'active' : ''}`} onClick={e => navTo(e, '/utilisateurs')}>
                      <Users size={18} />
                      <span>Utilisateurs</span>
                  </a>
                  <a href="/admin/systeme" className={`sp-nav-item ${location.pathname === '/admin/systeme' ? 'active' : ''}`} onClick={e => navTo(e, '/admin/systeme')}>
                      <Settings size={18} />
                      <span>Système</span>
                  </a>
                  <a href="/admin/dataset" className={`sp-nav-item ${location.pathname === '/admin/dataset' ? 'active' : ''}`} onClick={e => navTo(e, '/admin/dataset')}>
                      <Database size={18} />
                      <span>Dataset & Maladies</span>
                  </a>
                  <a href="/admin/ml" className={`sp-nav-item ${location.pathname === '/admin/ml' ? 'active' : ''}`} onClick={e => navTo(e, '/admin/ml')}>
                      <BarChart2 size={18} />
                      <span>Modèle IA</span>
                  </a>
                </>
              )}
          </nav>
      </div>

      <div className="sp-sidebar-footer">
          <div className="sp-user-card" onClick={(e) => navTo(e as React.MouseEvent, '/profil')}
               style={{ cursor: 'pointer' }} title="Voir mon profil">
              <div className="sp-user-avatar">
                  {user?.nom ? user.nom.substring(0, 1).toUpperCase() : '?'}
                  {user?.prenoms ? user.prenoms.substring(0, 1).toUpperCase() : '?'}
              </div>
              <div className="sp-user-info">
                  <div className="sp-user-name">{user?.prenoms} {user?.nom}</div>
                  <div className="sp-user-role">
                    {user?.role === 'admin' ? 'Administrateur' : user?.role === 'medecin' ? 'Médecin' : 'Infirmier'}
                  </div>
              </div>
          </div>
          <button onClick={() => setShowConfirm(true)} className="sp-logout-btn" style={{ width: '100%', border: 'none', cursor: 'pointer', textAlign: 'left', display: 'flex', alignItems: 'center' }}>
              <LogOut size={18} />
              <span>Déconnexion</span>
          </button>

          {showConfirm && (
            <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999 }}>
              <div className="sp-card" style={{ width: '320px', padding: '24px', textAlign: 'center', boxShadow: '0 10px 25px rgba(0,0,0,0.2)' }}>
                <div style={{ background: '#FEE2E2', color: '#EF4444', width: '48px', height: '48px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
                  <LogOut size={24} />
                </div>
                <h3 style={{ margin: '0 0 8px', fontSize: '18px', fontWeight: 700, color: '#1F2937' }}>Déconnexion</h3>
                <p style={{ margin: '0 0 24px', fontSize: '14px', color: '#6B7280' }}>Êtes-vous sûr de vouloir vous déconnecter ?</p>
                <div style={{ display: 'flex', gap: '12px' }}>
                  <button className="sp-btn sp-btn-outline" style={{ flex: 1 }} onClick={() => setShowConfirm(false)}>Annuler</button>
                  <button className="sp-btn" style={{ flex: 1, background: '#EF4444', color: '#fff' }} onClick={() => { logout(); onClose(); }}>Déconnexion</button>
                </div>
              </div>
            </div>
          )}
      </div>
    </div>
  );
};

// Horloge temps réel — composant isolé pour que le tick de 1s ne re-rende pas tout le Layout
const LiveClock = () => {
  const [now, setNow] = React.useState(() => new Date());

  React.useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <span>
      {now.toLocaleDateString('fr-FR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })} à {now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
    </span>
  );
};

interface PendingConsult { consultation_id: number; nom_patient: string; motif: string; date_heure: string; }

const Layout = ({ children }: { children: React.ReactNode }) => {
  const { isAdmin, user, token } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [pendingList, setPendingList] = React.useState<PendingConsult[]>([]);
  const [pendingAccountsCount, setPendingAccountsCount] = React.useState(0);
  const [dropdownOpen, setDropdownOpen] = React.useState(false);
  const [adminDropdownOpen, setAdminDropdownOpen] = React.useState(false);
  const [sidebarOpen, setSidebarOpen] = React.useState(false);
  const [topbarFixed, setTopbarFixed] = React.useState(false);
  const bellRef = React.useRef<HTMLDivElement>(null);
  const adminBellRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    let lastY = window.scrollY;
    const onScroll = () => {
      const y = window.scrollY;
      // Visible uniquement quand on remonte, une fois la barre d'origine hors de vue
      if (y <= 120) {
        setTopbarFixed(false);
      } else if (y < lastY - 2) {
        setTopbarFixed(true);
      } else if (y > lastY + 2) {
        setTopbarFixed(false);
      }
      lastY = y;
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  React.useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (bellRef.current && !bellRef.current.contains(e.target as Node)) {
        setDropdownOpen(false);
      }
      if (adminBellRef.current && !adminBellRef.current.contains(e.target as Node)) {
        setAdminDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  // Verrouiller le scroll de la page quand un dropdown de notifications est ouvert.
  // La liste interne (overflowY:auto) reste scrollable ; seul le défilement de
  // l'arrière-plan (page) est bloqué. On compense la largeur de la scrollbar pour
  // éviter le décalage horizontal du contenu lors du verrouillage.
  React.useEffect(() => {
    const anyOpen = dropdownOpen || adminDropdownOpen;
    if (!anyOpen) return;
    const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
    const prevOverflow = document.body.style.overflow;
    const prevPaddingRight = document.body.style.paddingRight;
    document.body.style.overflow = 'hidden';
    if (scrollbarWidth > 0) document.body.style.paddingRight = `${scrollbarWidth}px`;
    return () => {
      document.body.style.overflow = prevOverflow;
      document.body.style.paddingRight = prevPaddingRight;
    };
  }, [dropdownOpen, adminDropdownOpen]);

  const pendingCount = pendingList.length;

  React.useEffect(() => {
    if (user?.role !== 'medecin' || !user.medecin_id || !token) return;
    const fetchPending = () =>
      fetch(`http://localhost:8000/api/consultations/en-attente?medecin_id=${user.medecin_id}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
        .then(r => r.ok ? r.json() : [])
        .then(d => setPendingList(Array.isArray(d) ? d.filter((c: any) => c.medecin_id === user.medecin_id) : []))
        .catch(() => {});
    fetchPending();
    const id = setInterval(fetchPending, 60_000);
    return () => clearInterval(id);
  }, [user, token]);

  React.useEffect(() => {
    if (!isAdmin || !token) return;
    const fetchPendingAccounts = () =>
      adminAPI.getPendingUsers(token)
        .then(users => setPendingAccountsCount(users.length))
        .catch(() => {});
    fetchPendingAccounts();
    const id = setInterval(fetchPendingAccounts, 60_000);
    return () => clearInterval(id);
  }, [isAdmin, token]);


  const getPageTitle = () => {
    const path = window.location.pathname;
    if (path === '/') return 'Tableau de bord';
    if (path === '/analytique') return 'Analytique';
    if (path === '/consultations') return 'Consultations';
    if (path === '/mes-patients') return 'Mes Patients';
    if (path === '/diagnostics') return 'Diagnostics IA';
    if (path === '/personnel') return 'Personnel Médical';
    if (path === '/utilisateurs') return 'Utilisateurs';
    if (path === '/admin/systeme') return 'Administration Système';
    if (path === '/admin/dataset') return 'Dataset & Maladies';
    if (path === '/admin/ml') return 'Modèle IA & Entraînement';
    if (path.startsWith('/dossier-patient')) return 'Dossier Patient';
    return 'Accueil';
  };
  
  return (
    <>
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      {/* Overlay pour fermer le menu sur mobile + flou arrière-plan */}
      {sidebarOpen && <div className="sp-sidebar-overlay" onClick={() => setSidebarOpen(false)} />}
      
      <div className={`sp-main ${sidebarOpen ? 'sidebar-open' : ''}`}>
          {/* Top Bar */}
          {topbarFixed && <div style={{ height: 'calc(var(--sp-topbar-h) + 16px)', flexShrink: 0 }} />}
          <div className={`sp-topbar${topbarFixed ? ' sp-topbar-fixed' : ''}`}>
              <div className="sp-topbar-left">
                  <button 
                    className="sp-menu-toggle" 
                    onClick={() => setSidebarOpen(!sidebarOpen)}
                  >
                    <i data-feather="menu"></i>
                  </button>
                  <div className="sp-breadcrumb">
                      <span className="sp-breadcrumb-home">Accueil</span>
                      <span className="sp-breadcrumb-sep">›</span>
                      <span className="sp-breadcrumb-current">{getPageTitle()}</span>
                  </div>
              </div>
              <div className="sp-topbar-right">
                  <div className="sp-date-display">
                      <Clock size={16} />
                      <LiveClock />
                  </div>
                  {user?.role === 'medecin' && (
                    <div ref={bellRef} style={{ position: 'relative' }}>
                      <button
                        onClick={() => setDropdownOpen(o => !o)}
                        style={{ background: 'none', border: 'none', cursor: 'pointer', position: 'relative', display: 'flex', alignItems: 'center', color: pendingCount > 0 ? '#4F46E5' : '#9CA3AF', padding: '4px' }}
                        title={pendingCount > 0 ? `${pendingCount} consultation(s) en attente` : 'Aucune notification'}
                      >
                        <Bell size={20} />
                        {pendingCount > 0 && (
                          <span style={{ position: 'absolute', top: '-4px', right: '-4px', background: '#EF4444', color: '#fff', borderRadius: '50%', fontSize: '10px', fontWeight: 700, width: '16px', height: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            {pendingCount}
                          </span>
                        )}
                      </button>

                      {dropdownOpen && (
                        <div style={{ position: 'absolute', top: 'calc(100% + 10px)', right: 0, width: '320px', background: '#fff', borderRadius: '12px', boxShadow: '0 8px 32px rgba(0,0,0,0.15)', border: '1px solid #E5E7EB', zIndex: 1000, overflow: 'hidden' }}>
                          <div style={{ padding: '14px 16px', borderBottom: '1px solid #F3F4F6', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span style={{ fontWeight: 700, fontSize: '14px', color: '#1F2937' }}>Notifications</span>
                            {pendingCount > 0 && (
                              <span style={{ background: '#EEF2FF', color: '#4F46E5', borderRadius: '12px', fontSize: '11px', fontWeight: 700, padding: '2px 8px' }}>{pendingCount} en attente</span>
                            )}
                          </div>

                          {pendingList.length === 0 ? (
                            <div style={{ padding: '24px 16px', textAlign: 'center', color: '#9CA3AF', fontSize: '13px' }}>
                              <Bell size={28} style={{ margin: '0 auto 8px', display: 'block', opacity: 0.3 }} />
                              Aucune consultation en attente
                            </div>
                          ) : (
                            <div style={{ maxHeight: '320px', overflowY: 'auto', overscrollBehavior: 'contain' }}>
                              {pendingList.map(c => (
                                <div
                                  key={c.consultation_id}
                                  onClick={() => { setDropdownOpen(false); navigate(`/consultation/nouvelle?reprendre=${c.consultation_id}`); }}
                                  style={{ padding: '12px 16px', borderBottom: '1px solid #F9FAFB', cursor: 'pointer', transition: 'background 0.15s' }}
                                  onMouseEnter={e => (e.currentTarget.style.background = '#F5F3FF')}
                                  onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
                                >
                                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '8px' }}>
                                    <div style={{ flex: 1, minWidth: 0 }}>
                                      <div style={{ fontWeight: 600, fontSize: '13px', color: '#1F2937', marginBottom: '2px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                        {c.nom_patient}
                                      </div>
                                      <div style={{ fontSize: '12px', color: '#6B7280', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                        {c.motif || '—'}
                                      </div>
                                    </div>
                                    <div style={{ fontSize: '11px', color: '#9CA3AF', flexShrink: 0 }}>
                                      {c.date_heure ? new Date(c.date_heure).toLocaleString('fr-FR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }) : '—'}
                                    </div>
                                  </div>
                                  <div style={{ marginTop: '6px' }}>
                                    <span style={{ fontSize: '11px', background: '#EEF2FF', color: '#4F46E5', borderRadius: '6px', padding: '2px 8px', fontWeight: 600 }}>
                                      Cliquer pour continuer →
                                    </span>
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                  {isAdmin && (
                    <div ref={adminBellRef} style={{ position: 'relative' }}>
                      <button
                        onClick={() => setAdminDropdownOpen(o => !o)}
                        style={{ background: 'none', border: 'none', cursor: 'pointer', position: 'relative', display: 'flex', alignItems: 'center', color: pendingAccountsCount > 0 ? '#F59E0B' : '#9CA3AF', padding: '4px' }}
                        title={pendingAccountsCount > 0 ? `${pendingAccountsCount} compte(s) en attente d'activation` : 'Aucun compte en attente'}
                      >
                        <UserPlus size={20} />
                        {pendingAccountsCount > 0 && (
                          <span style={{ position: 'absolute', top: '-4px', right: '-4px', background: '#EF4444', color: '#fff', borderRadius: '50%', fontSize: '10px', fontWeight: 700, width: '16px', height: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            {pendingAccountsCount}
                          </span>
                        )}
                      </button>

                      {adminDropdownOpen && (
                        <div style={{ position: 'absolute', top: 'calc(100% + 10px)', right: 0, width: '300px', background: '#fff', borderRadius: '12px', boxShadow: '0 8px 32px rgba(0,0,0,0.15)', border: '1px solid #E5E7EB', zIndex: 1000, overflow: 'hidden' }}>
                          <div style={{ padding: '14px 16px', borderBottom: '1px solid #F3F4F6', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span style={{ fontWeight: 700, fontSize: '14px', color: '#1F2937' }}>Comptes en attente</span>
                            {pendingAccountsCount > 0 && (
                              <span style={{ background: '#FEF3C7', color: '#D97706', borderRadius: '12px', fontSize: '11px', fontWeight: 700, padding: '2px 8px' }}>{pendingAccountsCount} en attente</span>
                            )}
                          </div>
                          {pendingAccountsCount === 0 ? (
                            <div style={{ padding: '24px 16px', textAlign: 'center', color: '#9CA3AF', fontSize: '13px' }}>
                              <UserPlus size={28} style={{ margin: '0 auto 8px', display: 'block', opacity: 0.3 }} />
                              Aucun compte en attente d'activation
                            </div>
                          ) : (
                            <div style={{ padding: '16px' }}>
                              <p style={{ fontSize: '13px', color: '#6B7280', margin: '0 0 12px' }}>
                                {pendingAccountsCount} compte(s) attendent votre activation.
                              </p>
                              <button
                                onClick={() => { setAdminDropdownOpen(false); navigate('/utilisateurs'); }}
                                className="sp-btn sp-btn-primary"
                                style={{ width: '100%', justifyContent: 'center', fontSize: '13px' }}
                              >
                                <UserPlus size={15} /> Gérer les comptes
                              </button>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                  {isAdmin ? (
                    <div className="sp-role-badge admin">Administrateur</div>
                  ) : (
                    <div className="sp-role-badge operator">
                      {user?.role === 'medecin' ? 'Médecin' : 'Infirmier'}
                    </div>
                  )}
              </div>
          </div>
          
          <div className="sp-content">
            {children}
          </div>
      </div>
    </>
  );
};

function AppContent() {
  const { isAuthenticated } = useAuth();

  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/" replace />} />
        <Route path="/register" element={!isAuthenticated ? <Register /> : <Navigate to="/" replace />} />
        <Route path="/mot-de-passe-oublie" element={!isAuthenticated ? <MotDePasseOublie /> : <Navigate to="/" replace />} />
        <Route path="/" element={<PrivateRoute><Layout><Dashboard /></Layout></PrivateRoute>} />
        <Route path="/profil" element={<PrivateRoute><Layout><Profil /></Layout></PrivateRoute>} />
        <Route path="/analytique" element={<PrivateRoute><Layout><Analytics /></Layout></PrivateRoute>} />
        <Route path="/consultations" element={<PrivateRoute noAdmin><Layout><Consultations /></Layout></PrivateRoute>} />
        <Route path="/consultation/nouvelle" element={<PrivateRoute noAdmin medicalOnly><Layout><ConsultationWorkflow /></Layout></PrivateRoute>} />
        <Route path="/consultation/:consultationId/details" element={<PrivateRoute noAdmin noInfirmier><Layout><ConsultationDetails /></Layout></PrivateRoute>} />
        <Route path="/dossier-patient/:patientId" element={<PrivateRoute noAdmin medicalOnly><Layout><DossierPatient /></Layout></PrivateRoute>} />
        <Route path="/mes-patients" element={<PrivateRoute noAdmin noInfirmier><Layout><MesPatients /></Layout></PrivateRoute>} />
        <Route path="/diagnostics" element={<PrivateRoute noAdmin noInfirmier><Layout><DiagnosticsIA /></Layout></PrivateRoute>} />
        <Route path="/personnel" element={<PrivateRoute><Layout><PersonnelMedical /></Layout></PrivateRoute>} />
        <Route path="/utilisateurs" element={<PrivateRoute adminOnly><Layout><Utilisateurs /></Layout></PrivateRoute>} />
        <Route path="/admin/systeme" element={<PrivateRoute adminOnly><Layout><AdminSystem /></Layout></PrivateRoute>} />
        <Route path="/admin/dataset" element={<PrivateRoute adminOnly><Layout><AdminDataset /></Layout></PrivateRoute>} />
        <Route path="/admin/ml" element={<PrivateRoute adminOnly><Layout><AdminML /></Layout></PrivateRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  );
}

function App() {
  // Initialize LocalStorage Mock DB immediately before render
  initDB();

  return (
    <AuthProvider>
      <ToastProvider>
        <ConfirmProvider>
          <BrowserRouter>
            <AppContent />
          </BrowserRouter>
        </ConfirmProvider>
      </ToastProvider>
    </AuthProvider>
  );
}

export default App;
