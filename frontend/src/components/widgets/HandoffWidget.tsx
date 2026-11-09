import React from 'react';
import { Box, Button, Paper, Typography } from '@mui/material';
import { Headset, RefreshCw } from 'lucide-react';

interface Props {
  onRestart: () => void;
}

export const HandoffWidget: React.FC<Props> = ({ onRestart }) => {
  return (
    <Paper
      elevation={0}
      sx={{
        p: { xs: 1.5, sm: 2.5 },
        mt: 1.25,
        borderRadius: '16px',
        bgcolor: '#FEF2F2',
        border: '1px solid #FECACA',
        boxShadow: '0 4px 16px rgba(0, 0, 0, 0.03)',
        width: '100%',
        boxSizing: 'border-box',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.2, mb: 1 }}>
        <Headset color="#DC2626" size={22} />
        <Typography variant="subtitle1" sx={{ color: '#991B1B', fontWeight: 700, fontSize: { xs: '0.9rem', sm: '1rem' } }}>
          Executive Support Requested
        </Typography>
      </Box>
      <Typography variant="body2" sx={{ color: '#7F1D1D', mb: 1.5, fontSize: { xs: '0.8rem', sm: '0.875rem' } }}>
        Our claims executive will get in touch with you shortly on your registered contact details.
      </Typography>
      <Button
        variant="outlined"
        startIcon={<RefreshCw size={15} />}
        onClick={onRestart}
        size="small"
        sx={{
          color: '#991B1B',
          borderColor: '#FCA5A5',
          borderRadius: '20px',
          minHeight: 44,
          width: { xs: '100%', sm: 'auto' },
          '&:hover': { bgcolor: '#FEE2E2', borderColor: '#DC2626' },
        }}
      >
        Start New Intimation
      </Button>
    </Paper>
  );
};
