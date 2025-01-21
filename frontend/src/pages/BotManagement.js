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
  TextField
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';

function BotManagement() {
  const [open, setOpen] = React.useState(false);
  const [bots, setBots] = React.useState([]);

  const handleAddBot = () => {
    setOpen(true);
  };

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

      <Grid container spacing={3}>
        {bots.map((bot) => (
          <Grid item xs={12} md={6} lg={4} key={bot.id}>
            <Card>
              <CardContent>
                <Typography variant="h6">{bot.name}</Typography>
                <Typography color="textSecondary">Status: {bot.status}</Typography>
              </CardContent>
              <CardActions>
                <Button size="small">Start</Button>
                <Button size="small">Stop</Button>
                <Button size="small">Restart</Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={open} onClose={() => setOpen(false)}>
        <DialogTitle>Add New Bot</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Bot Name"
            fullWidth
            variant="outlined"
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Bot Token"
            fullWidth
            variant="outlined"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setOpen(false)}>Add</Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}

export default BotManagement;