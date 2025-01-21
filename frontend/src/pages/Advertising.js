import React from 'react';
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
  InputLabel
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';

function Advertising() {
  const [open, setOpen] = React.useState(false);
  const [ads, setAds] = React.useState([]);

  const handleCreateAd = () => {
    setOpen(true);
  };

  return (
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

      <Grid container spacing={3}>
        {ads.map((ad) => (
          <Grid item xs={12} md={6} lg={4} key={ad.id}>
            <Card>
              <CardContent>
                <Typography variant="h6">{ad.title}</Typography>
                <Typography color="textSecondary">Status: {ad.status}</Typography>
                <Typography>Price: ${ad.price}</Typography>
              </CardContent>
              <CardActions>
                <Button size="small">View Details</Button>
                <Button size="small" color="primary">Broadcast</Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Advertisement</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Ad Title"
            fullWidth
            variant="outlined"
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Message Content"
            fullWidth
            multiline
            rows={4}
            variant="outlined"
            sx={{ mb: 2 }}
          />
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Target Bots</InputLabel>
            <Select
              multiple
              label="Target Bots"
              value={[]}
              onChange={() => {}}
            >
              <MenuItem value="all">All Bots</MenuItem>
            </Select>
          </FormControl>
          <TextField
            margin="dense"
            label="Price"
            type="number"
            fullWidth
            variant="outlined"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setOpen(false)}>Create</Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}

export default Advertising;