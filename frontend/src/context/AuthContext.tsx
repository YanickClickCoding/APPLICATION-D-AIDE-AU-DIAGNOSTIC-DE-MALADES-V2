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

  const logout = () => {
    // Appeler l'API de déconnexion si on a un token
    if (token) {
      authAPI.logout(token).catch(console.error);
    }

    // Nettoyer l'état et le localStorage
    setUser(null);
    setToken(null);
    localStorage.removeItem('sp_token');
    localStorage.removeItem('sp_user');
  };

  return (
    <AuthContext.Provider value={{
      user,
      token,
      login,
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
