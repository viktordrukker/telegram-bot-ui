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
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  Box,
  CircularProgress,
  Chip,
  IconButton,
  Tooltip,
  FormHelperText,
  Divider,
  Stack,
  Switch,
  FormControlLabel,
  InputAdornment,
} from '@mui/material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import AddIcon from '@mui/icons-material/Add';
import SendIcon from '@mui/icons-material/Send';
import DeleteIcon from '@mui/icons-material/Delete';
import ImageIcon from '@mui/icons-material/Image';
import { advertisements, bots } from '../services/api';

function Advertising() {
  const [open, setOpen] = useState(false);
  const [adList, setAdList] = useState([]);
  const [botList, setBotList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    targetBots: [],
    price: '',
    mediaUrls: [],
    scheduled: false,
    scheduledFor: new Date(),
  });
  const [formError, setFormError] = useState('');
  const [broadcastInProgress, setBroadcastInProgress] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [adsData, botsData] = await Promise.all([
        advertisements.getAll(),
        bots.getAll(),
      ]);
      setAdList(adsData);
      setBotList(botsData);
      setError('');
    } catch (err) {
      setError('Failed to load data');
      console.error('Error loading data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAd = () => {
    setFormData({
      title: '',
      content: '',
      targetBots: [],
      price: '',
      mediaUrls: [],
      scheduled: false,
      scheduledFor: new Date(),
    });
    setFormError('');
    setOpen(true);
  };

  const handleSubmit = async () => {
    if (!formData.title || !formData.content || !formData.price || formData.targetBots.length === 0) {
      setFormError('All fields are required');
      return;
    }

    try {
      const data = {
        title: formData.title,
        content: formData.content,
        price: parseFloat(formData.price),
        media_urls: formData.mediaUrls,
        scheduled_for: formData.scheduled ? formData.scheduledFor.toISOString() : null,
        target_bots: formData.targetBots,
      };

      const response = await advertisements.create(data);
      setAdList([...adList, response.advertisement]);
      setOpen(false);
      setFormError('');
    } catch (err) {
      setFormError(err.response?.data?.message || 'Failed to create advertisement');
    }
  };

  const handleBroadcast = async (adId) => {
    setBroadcastInProgress(adId);
    try {
      const ad = adList.find(a => a.id === adId);
      const response = await advertisements.broadcast(adId, ad.target_bots);
      
      // Update ad status in the list
      setAdList(adList.map(a => 
        a.id === adId 
          ? { ...a, status: 'broadcasting' }
          : a
      ));
    } catch (err) {
      setError('Failed to start broadcast');
    } finally {
      setBroadcastInProgress(null);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'default';
      case 'broadcasting':
        return 'primary';
      case 'completed':
        return 'success';
      case 'failed':
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
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <div>
        <Grid container spacing={2} alignItems="center" sx={{ mb: 3 }}>
          <Grid item>
            <Typography variant="h4">Advertising</Typography>
          </Grid>
          <Grid item>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleCreateAd}
            >
              Create Ad
            </Button>
          </Grid>
        </Grid>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3}>
          {adList.map((ad) => (
            <Grid item xs={12} md={6} lg={4} key={ad.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {ad.title}
                  </Typography>
                  <Chip
                    label={ad.status}
                    color={getStatusColor(ad.status)}
                    size="small"
                    sx={{ mb: 2 }}
                  />
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Price: ${ad.price}
                  </Typography>
                  {ad.scheduled_for && (
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      Scheduled: {new Date(ad.scheduled_for).toLocaleString()}
                    </Typography>
                  )}
                  <Typography variant="body2" noWrap>
                    {ad.content}
                  </Typography>
                </CardContent>
                <Divider />
                <CardActions>
                  <Tooltip title="Broadcast Now">
                    <IconButton
                      color="primary"
                      disabled={ad.status === 'broadcasting' || broadcastInProgress === ad.id}
                      onClick={() => handleBroadcast(ad.id)}
                    >
                      {broadcastInProgress === ad.id ? (
                        <CircularProgress size={24} />
                      ) : (
                        <SendIcon />
                      )}
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton color="error">
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>

        <Dialog open={open} onClose={() => setOpen(false)} maxWidth="md" fullWidth>
          <DialogTitle>Create New Advertisement</DialogTitle>
          <DialogContent>
            {formError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {formError}
              </Alert>
            )}
            <TextField
              autoFocus
              margin="dense"
              label="Ad Title"
              fullWidth
              variant="outlined"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              label="Message Content"
              fullWidth
              multiline
              rows={4}
              variant="outlined"
              value={formData.content}
              onChange={(e) => setFormData({ ...formData, content: e.target.value })}
              sx={{ mb: 2 }}
              helperText="Supports HTML formatting"
            />
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Target Bots</InputLabel>
              <Select
                multiple
                label="Target Bots"
                value={formData.targetBots}
                onChange={(e) => setFormData({ ...formData, targetBots: e.target.value })}
              >
                {botList.map((bot) => (
                  <MenuItem key={bot.id} value={bot.id}>
                    {bot.bot_name}
                  </MenuItem>
                ))}
              </Select>
              <FormHelperText>Select bots to broadcast this advertisement</FormHelperText>
            </FormControl>
            <TextField
              margin="dense"
              label="Price"
              type="number"
              fullWidth
              variant="outlined"
              value={formData.price}
              onChange={(e) => setFormData({ ...formData, price: e.target.value })}
              InputProps={{
                startAdornment: <InputAdornment position="start">$</InputAdornment>,
              }}
              sx={{ mb: 2 }}
            />
            <Stack spacing={2}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.scheduled}
                    onChange={(e) => setFormData({ ...formData, scheduled: e.target.checked })}
                  />
                }
                label="Schedule Broadcast"
              />
              {formData.scheduled && (
                <DateTimePicker
                  label="Broadcast Time"
                  value={formData.scheduledFor}
                  onChange={(newValue) => setFormData({ ...formData, scheduledFor: newValue })}
                  renderInput={(params) => <TextField {...params} />}
                  minDateTime={new Date()}
                />
              )}
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>Cancel</Button>
            <Button variant="contained" onClick={handleSubmit}>Create</Button>
          </DialogActions>
        </Dialog>
      </div>
    </LocalizationProvider>
  );
}

export default Advertising;