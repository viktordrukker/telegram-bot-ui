import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  CircularProgress,
  Box,
  Alert,
  IconButton,
  Tooltip,
  Button,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  Timeline,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as ChartTooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import RefreshIcon from '@mui/icons-material/Refresh';
import DownloadIcon from '@mui/icons-material/Download';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import { analytics } from '../services/api';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [timeRange, setTimeRange] = useState('24h');
  const [anchorEl, setAnchorEl] = useState(null);

  useEffect(() => {
    loadMetrics();
  }, [timeRange]);

  const loadMetrics = async () => {
    try {
      const data = await analytics.getDashboard();
      setMetrics(data);
      setError('');
    } catch (err) {
      setError('Failed to load metrics');
      console.error('Error loading metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    setLoading(true);
    loadMetrics();
  };

  const handleExport = async () => {
    try {
      const data = await analytics.exportData();
      // Convert to CSV and download
      const csv = convertToCSV(data);
      downloadCSV(csv, 'analytics_export.csv');
    } catch (err) {
      setError('Failed to export data');
    }
  };

  const handleTimeRangeClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleTimeRangeSelect = (range) => {
    setTimeRange(range);
    setAnchorEl(null);
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
          <Typography variant="h4">Dashboard</Typography>
        </Grid>
        <Grid item>
          <Button
            variant="outlined"
            startIcon={<CalendarTodayIcon />}
            onClick={handleTimeRangeClick}
          >
            {getTimeRangeLabel(timeRange)}
          </Button>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={() => setAnchorEl(null)}
          >
            <MenuItem onClick={() => handleTimeRangeSelect('24h')}>Last 24 Hours</MenuItem>
            <MenuItem onClick={() => handleTimeRangeSelect('7d')}>Last 7 Days</MenuItem>
            <MenuItem onClick={() => handleTimeRangeSelect('30d')}>Last 30 Days</MenuItem>
          </Menu>
        </Grid>
        <Grid item>
          <Tooltip title="Refresh">
            <IconButton onClick={handleRefresh}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Grid>
        <Grid item>
          <Tooltip title="Export Data">
            <IconButton onClick={handleExport}>
              <DownloadIcon />
            </IconButton>
          </Tooltip>
        </Grid>
      </Grid>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Summary Cards */}
        <Grid item xs={12} md={6} lg={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" color="textSecondary" gutterBottom>
              Total Bots
            </Typography>
            <Typography variant="h4">{metrics?.total_bots || 0}</Typography>
            <Typography variant="body2" color="textSecondary">
              {metrics?.active_bots || 0} Active
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6} lg={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" color="textSecondary" gutterBottom>
              Total Users
            </Typography>
            <Typography variant="h4">{metrics?.total_users || 0}</Typography>
            <Typography variant="body2" color="textSecondary">
              Across all bots
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6} lg={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" color="textSecondary" gutterBottom>
              Messages Sent
            </Typography>
            <Typography variant="h4">{metrics?.total_messages || 0}</Typography>
            <Typography variant="body2" color="textSecondary">
              Last {getTimeRangeLabel(timeRange)}
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6} lg={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" color="textSecondary" gutterBottom>
              Active Ads
            </Typography>
            <Typography variant="h4">{metrics?.active_ads || 0}</Typography>
            <Typography variant="body2" color="textSecondary">
              {metrics?.completed_ads || 0} Completed
            </Typography>
          </Paper>
        </Grid>

        {/* Charts */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              User Activity
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={metrics?.user_activity || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" />
                <YAxis />
                <ChartTooltip />
                <Line
                  type="monotone"
                  dataKey="active_users"
                  stroke="#8884d8"
                  name="Active Users"
                />
                <Line
                  type="monotone"
                  dataKey="messages"
                  stroke="#82ca9d"
                  name="Messages"
                />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Message Types
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={metrics?.message_types || []}
                  dataKey="value"
                  nameKey="type"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label
                >
                  {(metrics?.message_types || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <ChartTooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Bot Performance */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Bot Performance
            </Typography>
            <Grid container spacing={2}>
              {(metrics?.bot_metrics || []).map((bot) => (
                <Grid item xs={12} md={6} lg={4} key={bot.id}>
                  <Paper variant="outlined" sx={{ p: 2 }}>
                    <Typography variant="subtitle1" gutterBottom>
                      {bot.name}
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">
                          Users
                        </Typography>
                        <Typography variant="h6">{bot.users}</Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">
                          Messages
                        </Typography>
                        <Typography variant="h6">{bot.messages}</Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">
                          Ads Delivered
                        </Typography>
                        <Typography variant="h6">{bot.ads_delivered}</Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">
                          Success Rate
                        </Typography>
                        <Typography variant="h6">{bot.success_rate}%</Typography>
                      </Grid>
                    </Grid>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </div>
  );
}

function getTimeRangeLabel(range) {
  switch (range) {
    case '24h':
      return 'Last 24 Hours';
    case '7d':
      return 'Last 7 Days';
    case '30d':
      return 'Last 30 Days';
    default:
      return 'Last 24 Hours';
  }
}

function convertToCSV(data) {
  const headers = Object.keys(data[0]).join(',');
  const rows = data.map(obj => Object.values(obj).join(','));
  return [headers, ...rows].join('\n');
}

function downloadCSV(csv, filename) {
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

export default Dashboard;