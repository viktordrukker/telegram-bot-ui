import React from 'react';
import {
  Typography,
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';

function Analytics() {
  return (
    <div>
      <Grid container spacing={2} alignItems="center" sx={{ mb: 3 }}>
        <Grid item>
          <Typography variant="h4">Analytics</Typography>
        </Grid>
        <Grid item>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
          >
            Download Logs
          </Button>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Bot Performance</Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Bot Name</TableCell>
                    <TableCell align="right">Active Users</TableCell>
                    <TableCell align="right">Messages Sent</TableCell>
                    <TableCell align="right">Ads Delivered</TableCell>
                    <TableCell align="right">Success Rate</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {/* Sample data - will be replaced with real data */}
                  <TableRow>
                    <TableCell>No data available</TableCell>
                    <TableCell align="right">-</TableCell>
                    <TableCell align="right">-</TableCell>
                    <TableCell align="right">-</TableCell>
                    <TableCell align="right">-</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Advertisement Performance</Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Ad Title</TableCell>
                    <TableCell align="right">Reach</TableCell>
                    <TableCell align="right">Engagement</TableCell>
                    <TableCell align="right">Cost</TableCell>
                    <TableCell align="right">ROI</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {/* Sample data - will be replaced with real data */}
                  <TableRow>
                    <TableCell>No data available</TableCell>
                    <TableCell align="right">-</TableCell>
                    <TableCell align="right">-</TableCell>
                    <TableCell align="right">-</TableCell>
                    <TableCell align="right">-</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>
    </div>
  );
}

export default Analytics;