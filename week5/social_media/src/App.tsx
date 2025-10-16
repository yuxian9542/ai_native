import React from 'react';
import { AuthProvider } from './contexts/AuthContext';
import HomePage from './pages/HomePage';

const AppContent: React.FC = () => {
  // Always show HomePage, whether user is logged in or not
  return <HomePage />;
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;
