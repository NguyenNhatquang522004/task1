import React, { useEffect } from 'react';
import { useCredentials } from '../../context/UserCredentials';
import { getNeo4jConfig, logEnvironmentConfig } from '../../utils/EnvironmentConfig';

/**
 * Component to auto-fill Neo4j credentials from environment variables
 * Useful for development and testing
 */
const EnvironmentCredentialsLoader: React.FC = () => {
  const { setUserCredentials, userCredentials, connectionStatus } = useCredentials();

  useEffect(() => {
    // Log environment config for debugging
    logEnvironmentConfig();

    // Only auto-fill if no credentials are set and not connected
    if (!connectionStatus && (!userCredentials || Object.keys(userCredentials).length === 0)) {
      const envConfig = getNeo4jConfig();
      
      // Check if all required env vars are available
      if (envConfig.uri && envConfig.userName && envConfig.password) {
        console.log('🔧 Auto-filling credentials from environment variables');
        setUserCredentials({
          uri: envConfig.uri,
          userName: envConfig.userName,
          password: envConfig.password,
          database: envConfig.database,
          email: '' // Required field, but can be empty for development
        });
      } else {
        console.warn('⚠️ Environment credentials incomplete - manual input required');
      }
    }
  }, [connectionStatus, userCredentials, setUserCredentials]);

  // This component doesn't render anything
  return null;
};

export default EnvironmentCredentialsLoader;
