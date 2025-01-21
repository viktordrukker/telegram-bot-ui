import React, { useState, useEffect } from 'react';
import {
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Chip,
  IconButton,
  Tooltip,
  CircularProgress,
  Box,
  Divider,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';
import RefreshIcon from '@mui/icons-material/Refresh';
import BarChartIcon from '@mui/icons-material/BarChart';
import { bots } from '../services/api';

function BotManagement() {
  const [open, setOpen] = useState(false);
  const [botList, setBotList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    botName: '',
    botToken: '',
  });
  const [formError, setFormError] = useState('');
  const [actionInProgress, setActionInProgress] = useState(null);

  useEffect(() => {
    loadBots();
  }, []);

  const loadBots = async () => {
    try {
      const data = await bots.getAll();
      setBotList(data);
      setError('');
    } catch (err) {
      setError('Failed to load bots');
      console.error('Error loading bots:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddBot = () => {
    setFormData({ botName: '', botToken: '' });
    setFormError('');
    setOpen(true);
  };

  const handleSubmit = async () => {
    if (!formData.botName || !formData.botToken) {
      setFormError('All fields are required');
      return;
    }

    try {
      const response = await bots.add(formData.botToken, formData.botName);
      setBotList([...botList, response.bot]);
      setOpen(false);
      setFormError('');
    } catch (err) {
      setFormError(err.response?.data?.message || 'Failed to add bot');
    }
  };

  const handleAction = async (botId, action) => {
    setActionInProgress(botId);
    try {
      let response;
      switch (action) {
        case 'start':
          response = await bots.start(botId);
          break;
        case 'stop':
          response = await bots.stop(botId);
          break;
        case 'restart':
          response = await bots.restart(botId);
          break;
        default:
          throw new Error('Invalid action');
      }
      
      // Update bot status in the list
      setBotList(botList.map(bot => 
        bot.id === botId 
          ? { ...bot, status: action === 'stop' ? 'stopped' : 'running' }
          : bot
      ));
    } catch (err) {
      setError(\`Failed to \${action} bot\`);
    } finally {
      setActionInProgress(null);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running':
        return 'success';
      case 'stopped':
        return 'error';
      case 'error':
        return 'error';
      default:
        return 'default';
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
    <div>
      <Grid container spacing={2} alignItems="center" sx={{ mb: 3 }}>
        <Grid item>
          <Typography variant="h4">Bot Management</Typography>
        </Grid>
        <Grid item>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleAddBot}
          >
            Add Bot
          </Button>
        </Grid>
      </Grid>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {botList.map((bot) => (
          <Grid item xs={12} md={6} lg={4} key={bot.id}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {bot.bot_name}
                </Typography>
                <Chip
                  label={bot.status}
                  color={getStatusColor(bot.status)}
                  size="small"
                  sx={{ mb: 2 }}
                />
                <Typography variant="body2" color="textSecondary">
                  Last Active: {bot.last_active ? new Date(bot.last_active).toLocaleString() : 'Never'}
                </Typography>
              </CardContent>
              <Divider />
              <CardActions>
                <Tooltip title="Start Bot">
                  <IconButton
                    color="success"
                    disabled={bot.status === 'running' || actionInProgress === bot.id}
                    onClick={() => handleAction(bot.id, 'start')}
                  >
                    {actionInProgress === bot.id ? (
                      <CircularProgress size={24} />
                    ) : (
                      <PlayArrowIcon />
                    )}
                  </IconButton>
                </Tooltip>
                <Tooltip title="Stop Bot">
                  <IconButton
                    color="error"
                    disabled={bot.status === 'stopped' || actionInProgress === bot.id}
                    onClick={() => handleAction(bot.id, 'stop')}
                  >
                    <StopIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Restart Bot">
                  <IconButton
                    color="primary"
                    disabled={actionInProgress === bot.id}
                    onClick={() => handleAction(bot.id, 'restart')}
                  >
                    <RefreshIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="View Metrics">
                  <IconButton
                    onClick={() => {/* TODO: Implement metrics view */}}
                  >
                    <BarChartIcon />
                  </IconButton>
                </Tooltip>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New Bot</DialogTitle>
        <DialogContent>
          {formError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {formError}
            </Alert>
          )}
          <TextField
            autoFocus
            margin="dense"
            label="Bot Name"
            fullWidth
            variant="outlined"
            value={formData.botName}
            onChange={(e) => setFormData({ ...formData, botName: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Bot Token"
            fullWidth
            variant="outlined"
            value={formData.botToken}
            onChange={(e) => setFormData({ ...formData, botToken: e.target.value })}
            helperText="Get this token from @BotFather on Telegram"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit}>Add</Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}

export default BotManagement;