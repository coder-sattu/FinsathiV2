import React from 'react';
import { Box, Button, Divider, Paper, Typography } from '@mui/material';
import { CheckCircle2, Edit3 } from 'lucide-react';
import type { UI } from '../../types';

interface Props {
  ui: UI;
  onSend: (value: any) => void;
  disabled?: boolean;
}

export const SummaryWidget: React.FC<Props> = ({ ui, onSend, disabled }) => {
  const summaryData = ui.data || {};

  return (
    <Paper
      elevation={0}
      sx={{
        p: { xs: 1.5, sm: 2.25 },
        mt: 1.25,
        borderRadius: '16px',
        bgcolor: '#FFFFFF',
        border: '1px solid #E2E8F0',
        boxShadow: '0 4px 16px rgba(0, 0, 0, 0.04)',
        width: '100%',
        boxSizing: 'border-box',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.2 }}>
        <CheckCircle2 color="#10B981" size={18} />
        <Typography variant="subtitle2" sx={{ color: '#10B981', fontWeight: 700, fontSize: { xs: '0.85rem', sm: '0.875rem' } }}>
          Summary & Confirmation
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.75, mb: 1.5 }}>
        {Object.entries(summaryData).map(([key, val]) => (
          <Box key={key} sx={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', gap: 1 }}>
            <Typography variant="caption" sx={{ color: '#64748B', fontSize: { xs: '0.72rem', sm: '0.75rem' }, flexShrink: 0 }}>
              {key.replace(/_/g, ' ').toUpperCase()}:
            </Typography>
            <Typography variant="caption" sx={{ color: '#1E293B', fontWeight: 600, fontSize: { xs: '0.75rem', sm: '0.8rem' }, textAlign: 'right', wordBreak: 'break-word' }}>
              {String(val)}
            </Typography>
          </Box>
        ))}
      </Box>

      <Divider sx={{ my: 1.2, borderColor: '#E2E8F0' }} />

      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
        {ui.options?.map((opt) => {
          const isConfirm = opt.value.includes('YES') || opt.value.includes('CONFIRM');
          return (
            <Button
              key={opt.value}
              variant={isConfirm ? 'contained' : 'outlined'}
              startIcon={!isConfirm ? <Edit3 size={15} /> : undefined}
              disabled={disabled}
              onClick={() => onSend(opt.value)}
              sx={{
                flex: { xs: '1 1 100%', sm: isConfirm ? 2 : 1 },
                width: { xs: '100%', sm: 'auto' },
                minHeight: 44,
                borderRadius: '20px',
                bgcolor: isConfirm ? '#10B981' : 'transparent',
                color: isConfirm ? '#FFFFFF' : '#475569',
                borderColor: isConfirm ? '#10B981' : '#CBD5E1',
                fontSize: { xs: '0.85rem', sm: '0.875rem' },
                fontWeight: 600,
                '&:hover': {
                  bgcolor: isConfirm ? '#059669' : '#F8FAFC',
                },
              }}
            >
              {opt.label}
            </Button>
          );
        })}
      </Box>
    </Paper>
  );
};
