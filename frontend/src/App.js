import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import BotManagement from './pages/BotManagement';
import Advertising from './pages/Advertising';
import Analytics from './pages/Analytics';

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

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/bots" element={<BotManagement />} />
          <Route path="/advertising" element={<Advertising />} />
          <Route path="/analytics" element={<Analytics />} />
        </Routes>
      </Layout>
    </ThemeProvider>
  );
}

export default App;