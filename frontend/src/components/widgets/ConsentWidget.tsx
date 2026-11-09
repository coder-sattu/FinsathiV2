import React from 'react';
import { Box, Button, Typography, Paper } from '@mui/material';
import { ShieldCheck } from 'lucide-react';
import type { UI } from '../../types';

interface Props {
  ui: UI;
  onSend: (value: any) => void;
  disabled?: boolean;
}

export const ConsentWidget: React.FC<Props> = ({ ui, onSend, disabled }) => {
  return (
    <Paper
      elevation={0}
      sx={{
        p: { xs: '16px 15px', sm: 2.25 },
        mt: 1.25,
        borderRadius: '16px',
        bgcolor: '#FFFFFF',
        border: '1px solid #E2E8F0',
        boxShadow: '0 4px 16px rgba(0, 0, 0, 0.04)',
        width: '100%',
        boxSizing: 'border-box',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: { xs: 1.75, sm: 1.2 } }}>
        <ShieldCheck color="#0052CC" size={20} />
        <Typography variant="h6" sx={{ color: '#0052CC', fontWeight: 600, fontSize: { xs: '1rem', sm: '1.05rem' } }}>
          Data Privacy & Consent
        </Typography>
      </Box>

      {ui.disclaimer && (
        <Typography
          variant="body2"
          sx={{
            color: '#475569',
            mb: { xs: 1.5, sm: 2 },
            fontSize: { xs: '0.8rem', sm: '0.875rem' },
            lineHeight: 1.45,
            wordBreak: 'break-word',
          }}
        >
          {ui.disclaimer}
        </Typography>
      )}

      {/* Mobile: Vertical stack, full width, 48px tall, pill shape, 10px gap */}
      <Box
        sx={{
          display: 'flex',
          flexDirection: { xs: 'column', sm: 'row' },
          gap: { xs: '10px', sm: '12px' },
        }}
      >
        {ui.options?.map((opt) => (
          <Button
            key={opt.value}
            variant={opt.value === 'YES' ? 'contained' : 'outlined'}
            color={opt.value === 'YES' ? 'primary' : 'inherit'}
            disabled={disabled}
            onClick={() => onSend(opt.value)}
            sx={{
              flex: { xs: 'none', sm: 1 },
              width: '100%',
              height: { xs: 48, sm: 'auto' },
              minHeight: 48,
              borderRadius: '24px', // pill shape
              bgcolor: opt.value === 'YES' ? '#0052CC' : '#FFFFFF',
              borderColor: opt.value === 'YES' ? '#0052CC' : '#CBD5E1',
              color: opt.value === 'YES' ? '#FFFFFF' : '#1E293B',
              fontSize: { xs: '0.9rem', sm: '0.875rem' },
              fontWeight: 600,
              textTransform: 'none',
              boxShadow: opt.value === 'YES' ? { xs: '0 4px 12px rgba(0, 82, 204, 0.25)', sm: 'none' } : 'none',
              '&:hover': {
                bgcolor: opt.value === 'YES' ? '#003D99' : '#F8FAFC',
                borderColor: opt.value === 'YES' ? '#003D99' : '#94A3B8',
              },
            }}
          >
            {opt.label}
          </Button>
        ))}
      </Box>
    </Paper>
  );
};