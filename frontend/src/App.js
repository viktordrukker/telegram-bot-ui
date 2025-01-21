import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { NotificationProvider, useNotification } from './contexts/NotificationContext';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import BotManagement from './pages/BotManagement';
import Advertising from './pages/Advertising';
import Analytics from './pages/Analytics';
import Login from './pages/Login';
import Register from './pages/Register';
import { CircularProgress, Box } from '@mui/material';
import { wsService } from './services/websocket';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function WebSocketHandler() {
  const { user } = useAuth();
  const { showNotification } = useNotification();

  useEffect(() => {
    if (user) {
      // Connect to WebSocket
      wsService.connect(localStorage.getItem('token'));

      // Subscribe to different notification types
      const subscriptions = [
        wsService.subscribe('connection', (data) => {
          if (data.status === 'connected') {
            showNotification('Connected to server', 'success');
          } else {
            showNotification('Lost connection to server', 'warning');
          }
        }),

        wsService.subscribe('bot_status', (data) => {
          showNotification(`Bot ${data.bot_name} is now ${data.status}`, 'info');
        }),

        wsService.subscribe('broadcast_status', (data) => {
          showNotification(
            `Advertisement broadcast ${data.status}: ${data.message}`,
            data.status === 'completed' ? 'success' : 'info'
          );
        }),

        wsService.subscribe('error', (data) => {
          showNotification(data.message, 'error');
        }),
      ];

      // Cleanup subscriptions
      return () => {
        subscriptions.forEach(unsubscribe => unsubscribe());
        wsService.disconnect();
      };
    }
  }, [user, showNotification]);

  return null;
}

function PrivateRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return user ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <NotificationProvider>
          <WebSocketHandler />
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/*"
              element={
                <PrivateRoute>
                  <Layout>
                    <Routes>
                      <Route path="/" element={<Dashboard />} />
                      <Route path="/bots" element={<BotManagement />} />
                      <Route path="/advertising" element={<Advertising />} />
                      <Route path="/analytics" element={<Analytics />} />
                    </Routes>
                  </Layout>
                </PrivateRoute>
              }
            />
          </Routes>
        </NotificationProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;