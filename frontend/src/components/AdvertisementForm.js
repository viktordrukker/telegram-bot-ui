import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Stack,
  Alert,
  InputAdornment,
  Typography,
  Divider,
} from '@mui/material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import MediaUpload from './MediaUpload';

function AdvertisementForm({ open, onClose, onSubmit, bots = [], loading = false }) {
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    targetBots: [],
    price: '',
    mediaUrls: [],
    scheduled: false,
    scheduledFor: new Date(),
  });
  const [error, setError] = useState('');

  const handleChange = (field) => (event) => {
    setFormData({ ...formData, [field]: event.target.value });
  };

  const handleSubmit = () => {
    if (!formData.title || !formData.content || !formData.price || formData.targetBots.length === 0) {
      setError('All fields are required');
      return;
    }

    onSubmit({
      title: formData.title,
      content: formData.content,
      target_bots: formData.targetBots,
      price: parseFloat(formData.price),
      media_urls: formData.mediaUrls.map(file => file.url),
      scheduled_for: formData.scheduled ? formData.scheduledFor.toISOString() : null,
    });
  };

  const handleClose = () => {
    setFormData({
      title: '',
      content: '',
      targetBots: [],
      price: '',
      mediaUrls: [],
      scheduled: false,
      scheduledFor: new Date(),
    });
    setError('');
    onClose();
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogTitle>Create New Advertisement</DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          <TextField
            autoFocus
            margin="dense"
            label="Ad Title"
            fullWidth
            variant="outlined"
            value={formData.title}
            onChange={handleChange('title')}
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
            onChange={handleChange('content')}
            sx={{ mb: 2 }}
            helperText="Supports HTML formatting"
          />

          <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
            Media Attachments
          </Typography>
          <MediaUpload
            value={formData.mediaUrls}
            onChange={(files) => setFormData({ ...formData, mediaUrls: files })}
            maxFiles={5}
          />

          <Divider sx={{ my: 2 }} />

          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Target Bots</InputLabel>
            <Select
              multiple
              label="Target Bots"
              value={formData.targetBots}
              onChange={handleChange('targetBots')}
            >
              {bots.map((bot) => (
                <MenuItem key={bot.id} value={bot.id}>
                  {bot.bot_name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            margin="dense"
            label="Price"
            type="number"
            fullWidth
            variant="outlined"
            value={formData.price}
            onChange={handleChange('price')}
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
          <Button onClick={handleClose}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading ? 'Creating...' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </LocalizationProvider>
  );
}

export default AdvertisementForm;