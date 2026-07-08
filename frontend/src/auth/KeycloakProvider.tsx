import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { keycloak, initializeKeycloak, getUserRoles, UserRole } from './keycloak';

interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: {
    id: string;
    email: string;
    name: string;
    roles: UserRole[];
  } | null;
  login: () => void;
  logout: () => void;
  getToken: () => string | undefined;
  hasRole: (role: UserRole) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const KeycloakProvider = ({ children }: { children: ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<AuthContextType['user']>(null);

  useEffect(() => {
    const init = async () => {
      const authenticated = await initializeKeycloak();
      setIsAuthenticated(authenticated);

      if (authenticated) {
        const tokenParsed = keycloak.tokenParsed as any;
        setUser({
          id: tokenParsed?.sub || '',
          email: tokenParsed?.email || tokenParsed?.preferred_username || '',
          name: `${tokenParsed?.given_name || ''} ${tokenParsed?.family_name || ''}`.trim(),
          roles: getUserRoles(),
        });
      }

      setIsLoading(false);
    };

    init();
  }, []);

  const login = () => keycloak.login();
  const logout = () => keycloak.logout();
  const getToken = () => keycloak.token;

  const hasRole = (role: UserRole): boolean => {
    if (!user) return false;
    return user.roles.includes('super_admin') || user.roles.includes(role);
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        isLoading,
        user,
        login,
        logout,
        getToken,
        hasRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within KeycloakProvider');
  }
  return context;
};