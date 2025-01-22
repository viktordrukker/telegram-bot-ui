import React, { createContext, useContext, useState, useCallback } from 'react';
import { Snackbar, Alert } from '@mui/material';

const NotificationContext = createContext(null);

export const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);

  const showNotification = useCallback((message, severity = 'info') => {
    const id = Date.now();
    setNotifications(prev => [...prev, { id, message, severity }]);
    return id;
  }, []);

  const hideNotification = useCallback((id) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  }, []);

  const value = {
    showNotification,
    hideNotification,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
      {notifications.map(({ id, message, severity }) => (
        <Snackbar
          key={id}
          open={true}
          autoHideDuration={6000}
          onClose={() => hideNotification(id)}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert
            onClose={() => hideNotification(id)}
            severity={severity}
            variant="filled"
            sx={{ width: '100%' }}
          >
            {message}
          </Alert>
        </Snackbar>
      ))}
    </NotificationContext.Provider>
  );
};

export const useNotification = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  return context;
};