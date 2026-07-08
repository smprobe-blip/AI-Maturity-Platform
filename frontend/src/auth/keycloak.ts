import Keycloak from 'keycloak-js';

const keycloakConfig = {
  url: import.meta.env.VITE_KEYCLOAK_URL || 'http://localhost:8080',
  realm: import.meta.env.VITE_KEYCLOAK_REALM || 'ai-maturity',
  clientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID || 'frontend-spa',
};

export const keycloak = new Keycloak(keycloakConfig);

export type UserRole =
  | 'super_admin'
  | 'facilitator'
  | 'analyst'
  | 'sales'
  | 'client'
  | 'auditor';

export const getUserRoles = (): UserRole[] => {
  const tokenParsed = keycloak.tokenParsed as any;
  if (!tokenParsed) return [];

  const realmRoles: string[] = tokenParsed.realm_access?.roles || [];
  const clientRoles: string[] =
    tokenParsed.resource_access?.[keycloakConfig.clientId]?.roles || [];

  const allRoles = [...realmRoles, ...clientRoles];
  const validRoles: UserRole[] = [
    'super_admin',
    'facilitator',
    'analyst',
    'sales',
    'client',
    'auditor',
  ];

  return allRoles.filter((r): r is UserRole => validRoles.includes(r as UserRole));
};

export const hasRole = (role: UserRole): boolean => {
  const roles = getUserRoles();
  return roles.includes('super_admin') || roles.includes(role);
};

export const hasAnyRole = (roles: UserRole[]): boolean => {
  return roles.some((role) => hasRole(role));
};

export const initializeKeycloak = async (): Promise<boolean> => {
  try {
    const authenticated = await keycloak.init({
      onLoad: 'check-sso',
      silentCheckSsoRedirectUri:
        window.location.origin + '/silent-check-sso.html',
      pkceMethod: 'S256',
      checkLoginIframe: false,
    });

    if (authenticated) {
      // Token refresh
      setInterval(async () => {
        try {
          await keycloak.updateToken(30);
        } catch {
          keycloak.login();
        }
      }, 60000);
    }

    return authenticated;
  } catch (error) {
    console.error('Keycloak init failed:', error);
    return false;
  }
};