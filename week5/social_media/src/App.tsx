import React from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import FirebaseAuth from './components/FirebaseAuth';
import HomePage from './pages/HomePage';

const AppContent: React.FC = () => {
  const { user } = useAuth();

  if (!user) {
    return <FirebaseAuth onAuthSuccess={() => {}} />;
  }

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
