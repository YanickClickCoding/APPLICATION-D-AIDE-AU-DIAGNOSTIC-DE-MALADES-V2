import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider } from './components/Toast';
import { initDB } from './db';
import { Users, Calendar, LogOut, UserCheck, Clock, Settings, Brain, User } from 'lucide-react';

// Pages
import Login from './pages/Login';
import Dashboard from './pages/DashboardNew';
import Consultations from './pages/Consultations';
import ConsultationWorkflow from './pages/ConsultationWorkflow';
import PersonnelMedical from './pages/PersonnelMedical';
import Utilisateurs from './pages/Utilisateurs';
import Register from './pages/Register';
import Identifiants from './pages/Identifiants';
import AdminSystem from './pages/AdminSystem';
import DossierPatient from './pages/DossierPatient';
import MesPatients from './pages/MesPatients';
import DiagnosticsIA from './pages/DiagnosticsIA';

const PrivateRoute = ({ children, adminOnly = false, medicalOnly = false }: { children: React.ReactNode, adminOnly?: boolean, medicalOnly?: boolean }) => {
  const { isAuthenticated, isAdmin, user } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (adminOnly && !isAdmin) return <Navigate to="/" replace />;
  if (medicalOnly && user?.role !== 'medecin' && user?.role !== 'infirmier') return <Navigate to="/consultations" replace />;
  return <>{children}</>;
};

const Sidebar = () => {
  const location = useLocation();
  const { user, isAdmin, logout } = useAuth();
  
  useEffect(() => {
    // @ts-ignore
    if (window.feather) {
      // @ts-ignore
      window.feather.replace();
    }
  }, [location.pathname]); // Seulement quand la route change
  
  return (
    <div className="sp-sidebar" id="sidebar">
      <div className="sp-logo-area">
          <div className="sp-logo-icon">
              <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                  <rect width="32" height="32" rx="10" fill="white" fillOpacity="0.15"/>
                  <path d="M16 6v20M6 16h20" stroke="white" strokeWidth="3.5" strokeLinecap="round"/>
                  <circle cx="16" cy="16" r="5" stroke="white" strokeWidth="2" fill="none"/>
              </svg>
          </div>
          <div>
              <div className="sp-logo-name">SANTÉ PLUS</div>
              <div className="sp-logo-sub">Clinique Privée · Cotonou</div>
          </div>
      </div>

      <div className="sp-nav-section">
          <div className="sp-nav-label">Navigation</div>
          <nav>
              {/* Tableau de bord — admin ET médecin */}
              <Link to="/" className={`sp-nav-item ${location.pathname === '/' ? 'active' : ''}`}>
                  <i data-feather="grid"></i>
                  <span>Tableau de bord</span>
              </Link>

              <Link to="/consultations" className={`sp-nav-item ${location.pathname === '/consultations' ? 'active' : ''}`}>
                  <Calendar size={18} />
                  <span>Consultations</span>
              </Link>

              {/* Nav médecin */}
              {!isAdmin && user?.role === 'medecin' && (
                <>
                  <Link to="/mes-patients" className={`sp-nav-item ${location.pathname === '/mes-patients' ? 'active' : ''}`}>
                      <User size={18} />
                      <span>Mes Patients</span>
                  </Link>
                  <Link to="/diagnostics" className={`sp-nav-item ${location.pathname === '/diagnostics' ? 'active' : ''}`}>
                      <Brain size={18} />
                      <span>Diagnostics IA</span>
                  </Link>
                </>
              )}

              {/* Nav admin */}
              {isAdmin && (
                <>
                  <Link to="/personnel" className={`sp-nav-item ${location.pathname === '/personnel' ? 'active' : ''}`}>
                      <UserCheck size={18} />
                      <span>Personnel Médical</span>
                  </Link>
                  <Link to="/utilisateurs" className={`sp-nav-item ${location.pathname === '/utilisateurs' ? 'active' : ''}`}>
                      <Users size={18} />
                      <span>Utilisateurs</span>
                  </Link>
                  <Link to="/identifiants" className={`sp-nav-item ${location.pathname === '/identifiants' ? 'active' : ''}`}>
                      <i data-feather="key"></i>
                      <span>Identifiants</span>
                  </Link>
                  <Link to="/admin/systeme" className={`sp-nav-item ${location.pathname === '/admin/systeme' ? 'active' : ''}`}>
                      <Settings size={18} />
                      <span>Système</span>
                  </Link>
                </>
              )}
          </nav>
      </div>

      <div className="sp-sidebar-footer">
          <div className="sp-user-card">
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
          <button onClick={logout} className="sp-logout-btn" style={{ width: '100%', border: 'none', cursor: 'pointer', textAlign: 'left', display: 'flex', alignItems: 'center' }}>
              <LogOut size={18} />
              <span>Déconnexion</span>
          </button>
      </div>
    </div>
  );
};

const Layout = ({ children }: { children: React.ReactNode }) => {
  const { isAdmin, user } = useAuth();
  
  const getPageTitle = () => {
    const path = window.location.pathname;
    if (path === '/') return 'Tableau de bord';
    if (path === '/consultations') return 'Consultations';
    if (path === '/mes-patients') return 'Mes Patients';
    if (path === '/diagnostics') return 'Diagnostics IA';
    if (path === '/personnel') return 'Personnel Médical';
    if (path === '/utilisateurs') return 'Utilisateurs';
    if (path === '/identifiants') return 'Identifiants';
    if (path === '/admin/systeme') return 'Administration Système';
    if (path.startsWith('/dossier-patient')) return 'Dossier Patient';
    return 'Accueil';
  };
  
  return (
    <>
      <Sidebar />
      <div className="sp-main">
          {/* Top Bar */}
          <div className="sp-topbar">
              <div className="sp-topbar-left">
                  <div className="sp-breadcrumb">
                      <span className="sp-breadcrumb-home">Accueil</span>
                      <span className="sp-breadcrumb-sep">›</span>
                      <span className="sp-breadcrumb-current">{getPageTitle()}</span>
                  </div>
              </div>
              <div className="sp-topbar-right">
                  <div className="sp-date-display">
                      <Clock size={16} />
                      <span>{new Date().toLocaleDateString('fr-FR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })} à {new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}</span>
                  </div>
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
    <Routes>
      <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/" replace />} />
      <Route path="/register" element={!isAuthenticated ? <Register /> : <Navigate to="/" replace />} />
      <Route path="/" element={<PrivateRoute><Layout><Dashboard /></Layout></PrivateRoute>} />
      <Route path="/consultations" element={<PrivateRoute><Layout><Consultations /></Layout></PrivateRoute>} />
      <Route path="/consultation/nouvelle" element={<PrivateRoute medicalOnly><Layout><ConsultationWorkflow /></Layout></PrivateRoute>} />
      <Route path="/dossier-patient/:patientId" element={<PrivateRoute><Layout><DossierPatient /></Layout></PrivateRoute>} />
      <Route path="/mes-patients" element={<PrivateRoute><Layout><MesPatients /></Layout></PrivateRoute>} />
      <Route path="/diagnostics" element={<PrivateRoute><Layout><DiagnosticsIA /></Layout></PrivateRoute>} />
      <Route path="/personnel" element={<PrivateRoute><Layout><PersonnelMedical /></Layout></PrivateRoute>} />
      <Route path="/utilisateurs" element={<PrivateRoute adminOnly><Layout><Utilisateurs /></Layout></PrivateRoute>} />
      <Route path="/identifiants" element={<PrivateRoute adminOnly><Layout><Identifiants /></Layout></PrivateRoute>} />
      <Route path="/admin/systeme" element={<PrivateRoute adminOnly><Layout><AdminSystem /></Layout></PrivateRoute>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  // Initialize LocalStorage Mock DB immediately before render
  initDB();

  return (
    <AuthProvider>
      <ToastProvider>
        <BrowserRouter>
          <AppContent />
        </BrowserRouter>
      </ToastProvider>
    </AuthProvider>
  );
}

export default App;
