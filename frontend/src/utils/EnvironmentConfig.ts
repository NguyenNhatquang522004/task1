/**
 * Environment variables utility for accessing configuration values
 */

export interface Neo4jConfig {
  uri: string;
  userName: string;
  password: string;
  database: string;
}

export interface AppConfig {
  backendUrl: string;
  neo4j: Neo4jConfig;
  debugMode: boolean;
}

/**
 * Get Neo4j configuration from environment variables
 */
export const getNeo4jConfig = (): Neo4jConfig => {
  return {
    uri: import.meta.env.VITE_NEO4J_URI || 'neo4j+s://localhost:7687',
    userName: import.meta.env.VITE_NEO4J_USERNAME || 'neo4j',
    password: import.meta.env.VITE_NEO4J_PASSWORD || '',
    database: import.meta.env.VITE_NEO4J_DATABASE || 'neo4j'
  };
};

/**
 * Get backend URL from environment variables
 */
export const getBackendUrl = (): string => {
  return import.meta.env.VITE_BACKEND_API_URL || 'http://localhost:8000';
};

/**
 * Get complete application configuration
 */
export const getAppConfig = (): AppConfig => {
  return {
    backendUrl: getBackendUrl(),
    neo4j: getNeo4jConfig(),
    debugMode: import.meta.env.VITE_DEBUG_MODE === 'true' || import.meta.env.VITE_ENV === 'DEV'
  };
};

/**
 * Check if all required environment variables are set
 */
export const validateEnvironmentConfig = (): { isValid: boolean; missingVars: string[] } => {
  const requiredVars = [
    'VITE_NEO4J_URI',
    'VITE_NEO4J_USERNAME', 
    'VITE_NEO4J_PASSWORD',
    'VITE_BACKEND_API_URL'
  ];

  const missingVars = requiredVars.filter(varName => !import.meta.env[varName]);
  
  return {
    isValid: missingVars.length === 0,
    missingVars
  };
};

// Debug helper - only log in development
export const logEnvironmentConfig = (): void => {
  console.log('🔧 Current Environment Variables:');
  console.log('  VITE_NEO4J_URI:', import.meta.env.VITE_NEO4J_URI);
  console.log('  VITE_NEO4J_USERNAME:', import.meta.env.VITE_NEO4J_USERNAME);
  console.log('  VITE_NEO4J_DATABASE:', import.meta.env.VITE_NEO4J_DATABASE);
  console.log('  VITE_BACKEND_API_URL:', import.meta.env.VITE_BACKEND_API_URL);
  console.log('  Has password:', !!import.meta.env.VITE_NEO4J_PASSWORD);
  
  if (import.meta.env.VITE_ENV === 'DEV') {
    console.log('🔧 Environment Configuration:', {
      neo4jUri: import.meta.env.VITE_NEO4J_URI,
      neo4jUsername: import.meta.env.VITE_NEO4J_USERNAME,
      neo4jDatabase: import.meta.env.VITE_NEO4J_DATABASE,
      backendUrl: import.meta.env.VITE_BACKEND_API_URL,
      // Don't log password for security
      hasPassword: !!import.meta.env.VITE_NEO4J_PASSWORD
    });
    
    const validation = validateEnvironmentConfig();
    if (!validation.isValid) {
      console.warn('⚠️ Missing environment variables:', validation.missingVars);
    }
  }
};
