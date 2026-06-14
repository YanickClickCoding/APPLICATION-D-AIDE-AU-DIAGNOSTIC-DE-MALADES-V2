import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

interface User {
  utilisateur_id: number;
  nom: string;
  prenoms: string;
  email: string;
  role: string;
  actif: boolean;
  medecin_id?: number;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<User>;
  updateUser: (partial: Partial<User>) => void;
  logout: () => void;
  isAuthenticated: boolean;
  isAdmin: boolean;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Charger l'utilisateur depuis le localStorage au démarrage
  useEffect(() => {
    const savedToken = localStorage.getItem('sp_token');
    const savedUser = localStorage.getItem('sp_user');

    if (savedToken && savedUser) {
      try {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
      } catch (error) {
        console.error('Erreur lors du chargement des données utilisateur:', error);
        localStorage.removeItem('sp_token');
        localStorage.removeItem('sp_user');
      }
    }
    setIsLoading(false);
  }, []);

  // Écouter les expirations de session émises par fetchAPI
  useEffect(() => {
    const handleSessionExpired = () => {
      // Éviter de déclencher si déjà déconnecté
      if (!localStorage.getItem('sp_token')) return;
      localStorage.removeItem('sp_token');
      localStorage.removeItem('sp_user');
      setUser(null);
      setToken(null);
      window.location.href = '/login?session=expired';
    };
    window.addEventListener('auth:session-expired', handleSessionExpired);
    return () => window.removeEventListener('auth:session-expired', handleSessionExpired);
  }, []);

  const login = async (email: string, password: string) => {
    console.log('📡 AuthContext.login appelé avec:', email);
    try {
      const response = await authAPI.login({ email, password });
      console.log('✅ Réponse API reçue:', response);
      
      // Sauvegarder le token et l'utilisateur
      setToken(response.access_token);
      setUser(response.user);
      
      localStorage.setItem('sp_token', response.access_token);
      localStorage.setItem('sp_user', JSON.stringify(response.user));
      
      console.log('✅ Token et utilisateur sauvegardés');
      return response.user;
    } catch (error) {
      console.error('❌ Erreur dans AuthContext.login:', error);
      throw error;
    }
  };

  // Met à jour l'utilisateur en mémoire + localStorage (après édition du profil)
  const updateUser = (partial: Partial<User>) => {
    setUser(prev => {
      if (!prev) return prev;
      const next = { ...prev, ...partial };
      localStorage.setItem('sp_user', JSON.stringify(next));
      return next;
    });
  };

  const logout = () => {
    // Nettoyer l'état local immédiatement
    setUser(null);
    setToken(null);
    localStorage.removeItem('sp_token');
    localStorage.removeItem('sp_user');

    // Notifier le serveur (best-effort, erreurs ignorées)
    if (token) {
      authAPI.logout(token).catch(() => {});
    }
  };

  return (
    <AuthContext.Provider value={{
      user,
      token,
      login,
      updateUser,
      logout,
      isAuthenticated: !!user && !!token,
      isAdmin: user?.role === 'admin',
      isLoading,
    }}>
      {children}
    </AuthContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
