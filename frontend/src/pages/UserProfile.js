import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  TextField,
  Button,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  CircularProgress,
  Chip,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import { useAuth } from '../contexts/AuthContext';
import { useNotification } from '../contexts/NotificationContext';

function UserProfile() {
  const { user } = useAuth();
  const { showNotification } = useNotification();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [apiKeys, setApiKeys] = useState([]);
  const [activities, setActivities] = useState([]);
  const [settings, setSettings] = useState(null);
  const [openApiKeyDialog, setOpenApiKeyDialog] = useState(false);
  const [newApiKeyName, setNewApiKeyName] = useState('');
  const [newApiKey, setNewApiKey] = useState(null);
  const [passwordDialog, setPasswordDialog] = useState(false);
  const [passwordData, setPasswordData] = useState({
    oldPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  useEffect(() => {
    loadUserData();
  }, []);

  const loadUserData = async () => {
    try {
      const [apiKeysResponse, activitiesResponse, settingsResponse] = await Promise.all([
        fetch('/api/users/me/api-keys', {
          headers: { 'x-access-token': localStorage.getItem('token') }
        }),
        fetch('/api/users/me/activity', {
          headers: { 'x-access-token': localStorage.getItem('token') }
        }),
        fetch('/api/users/me/settings', {
          headers: { 'x-access-token': localStorage.getItem('token') }
        })
      ]);

      const [apiKeysData, activitiesData, settingsData] = await Promise.all([
        apiKeysResponse.json(),
        activitiesResponse.json(),
        settingsResponse.json()
      ]);

      setApiKeys(apiKeysData);
      setActivities(activitiesData.activities);
      setSettings(settingsData);
      setError('');
    } catch (err) {
      setError('Failed to load user data');
      console.error('Error loading user data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateApiKey = async () => {
    try {
      const response = await fetch('/api/users/me/api-keys', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-access-token': localStorage.getItem('token')
        },
        body: JSON.stringify({ name: newApiKeyName })
      });

      const data = await response.json();
      if (response.ok) {
        setNewApiKey(data);
        loadUserData();
        showNotification('API key created successfully', 'success');
      } else {
        throw new Error(data.message);
      }
    } catch (err) {
      showNotification('Failed to create API key', 'error');
    }
    setOpenApiKeyDialog(false);
    setNewApiKeyName('');
  };

  const handleDeleteApiKey = async (keyId) => {
    try {
      const response = await fetch(`/api/users/me/api-keys/${keyId}`, {
        method: 'DELETE',
        headers: { 'x-access-token': localStorage.getItem('token') }
      });

      if (response.ok) {
        loadUserData();
        showNotification('API key deleted successfully', 'success');
      } else {
        throw new Error('Failed to delete API key');
      }
    } catch (err) {
      showNotification('Failed to delete API key', 'error');
    }
  };

  const handleChangePassword = async () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      showNotification('New passwords do not match', 'error');
      return;
    }

    try {
      const response = await fetch('/api/users/me', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'x-access-token': localStorage.getItem('token')
        },
        body: JSON.stringify({
          old_password: passwordData.oldPassword,
          new_password: passwordData.newPassword
        })
      });

      const data = await response.json();
      if (response.ok) {
        showNotification('Password changed successfully', 'success');
        setPasswordDialog(false);
        setPasswordData({ oldPassword: '', newPassword: '', confirmPassword: '' });
      } else {
        throw new Error(data.message);
      }
    } catch (err) {
      showNotification(err.message || 'Failed to change password', 'error');
    }
  };

  const handleUpdateSettings = async (newSettings) => {
    try {
      const response = await fetch('/api/users/me/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'x-access-token': localStorage.getItem('token')
        },
        body: JSON.stringify(newSettings)
      });

      if (response.ok) {
        setSettings(newSettings);
        showNotification('Settings updated successfully', 'success');
      } else {
        throw new Error('Failed to update settings');
      }
    } catch (err) {
      showNotification('Failed to update settings', 'error');
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" gutterBottom>
        User Profile
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Profile Information */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Profile Information
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Username"
                  value={user?.username}
                  disabled
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Email"
                  value={user?.email || ''}
                  disabled
                />
              </Grid>
              <Grid item xs={12}>
                <Button
                  variant="outlined"
                  onClick={() => setPasswordDialog(true)}
                >
                  Change Password
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Settings */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Settings
            </Typography>
            {settings && (
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Theme</InputLabel>
                    <Select
                      value={settings.theme}
                      onChange={(e) => handleUpdateSettings({ ...settings, theme: e.target.value })}
                    >
                      <MenuItem value="light">Light</MenuItem>
                      <MenuItem value="dark">Dark</MenuItem>
                      <MenuItem value="system">System</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Language</InputLabel>
                    <Select
                      value={settings.language}
                      onChange={(e) => handleUpdateSettings({ ...settings, language: e.target.value })}
                    >
                      <MenuItem value="en">English</MenuItem>
                      <MenuItem value="es">Spanish</MenuItem>
                      <MenuItem value="fr">French</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" gutterBottom>
                    Notifications
                  </Typography>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.notification_preferences.email}
                        onChange={(e) => handleUpdateSettings({
                          ...settings,
                          notification_preferences: {
                            ...settings.notification_preferences,
                            email: e.target.checked
                          }
                        })}
                      />
                    }
                    label="Email Notifications"
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.notification_preferences.web}
                        onChange={(e) => handleUpdateSettings({
                          ...settings,
                          notification_preferences: {
                            ...settings.notification_preferences,
                            web: e.target.checked
                          }
                        })}
                      />
                    }
                    label="Web Notifications"
                  />
                </Grid>
              </Grid>
            )}
          </Paper>
        </Grid>

        {/* API Keys */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                API Keys
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setOpenApiKeyDialog(true)}
              >
                Create API Key
              </Button>
            </Box>
            <List>
              {apiKeys.map((key) => (
                <ListItem key={key.id}>
                  <ListItemText
                    primary={key.name}
                    secondary={`Created: ${new Date(key.created_at).toLocaleString()}`}
                  />
                  <ListItemSecondaryAction>
                    <IconButton
                      edge="end"
                      aria-label="delete"
                      onClick={() => handleDeleteApiKey(key.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>

        {/* Activity Log */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Activity Log
            </Typography>
            <List>
              {activities.map((activity) => (
                <ListItem key={activity.id}>
                  <ListItemText
                    primary={activity.action}
                    secondary={new Date(activity.timestamp).toLocaleString()}
                  />
                  {activity.ip_address && (
                    <Chip
                      label={activity.ip_address}
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  )}
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>

      {/* API Key Dialog */}
      <Dialog
        open={openApiKeyDialog}
        onClose={() => {
          setOpenApiKeyDialog(false);
          setNewApiKey(null);
          setNewApiKeyName('');
        }}
      >
        <DialogTitle>
          {newApiKey ? 'API Key Created' : 'Create API Key'}
        </DialogTitle>
        <DialogContent>
          {newApiKey ? (
            <Box sx={{ mt: 2 }}>
              <Alert severity="warning" sx={{ mb: 2 }}>
                Make sure to copy your API key now. You won't be able to see it again!
              </Alert>
              <TextField
                fullWidth
                label="API Key"
                value={newApiKey.key}
                variant="outlined"
                InputProps={{
                  readOnly: true,
                }}
              />
            </Box>
          ) : (
            <TextField
              autoFocus
              margin="dense"
              label="API Key Name"
              fullWidth
              value={newApiKeyName}
              onChange={(e) => setNewApiKeyName(e.target.value)}
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setOpenApiKeyDialog(false);
              setNewApiKey(null);
              setNewApiKeyName('');
            }}
          >
            {newApiKey ? 'Close' : 'Cancel'}
          </Button>
          {!newApiKey && (
            <Button onClick={handleCreateApiKey} variant="contained">
              Create
            </Button>
          )}
        </DialogActions>
      </Dialog>

      {/* Change Password Dialog */}
      <Dialog
        open={passwordDialog}
        onClose={() => {
          setPasswordDialog(false);
          setPasswordData({ oldPassword: '', newPassword: '', confirmPassword: '' });
        }}
      >
        <DialogTitle>Change Password</DialogTitle>
        <DialogContent>
          <TextField
            margin="dense"
            label="Current Password"
            type="password"
            fullWidth
            value={passwordData.oldPassword}
            onChange={(e) => setPasswordData({ ...passwordData, oldPassword: e.target.value })}
          />
          <TextField
            margin="dense"
            label="New Password"
            type="password"
            fullWidth
            value={passwordData.newPassword}
            onChange={(e) => setPasswordData({ ...passwordData, newPassword: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Confirm New Password"
            type="password"
            fullWidth
            value={passwordData.confirmPassword}
            onChange={(e) => setPasswordData({ ...passwordData, confirmPassword: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPasswordDialog(false)}>Cancel</Button>
          <Button onClick={handleChangePassword} variant="contained">
            Change Password
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

export default UserProfile;