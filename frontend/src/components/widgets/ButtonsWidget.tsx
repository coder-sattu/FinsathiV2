import React from 'react';
import { Box, Button } from '@mui/material';
import type { UI } from '../../types';

interface Props {
  ui: UI;
  onSend: (value: any) => void;
  disabled?: boolean;
}

export const ButtonsWidget: React.FC<Props> = ({ ui, onSend, disabled }) => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mt: 1.25, width: '100%' }}>
      {ui.options?.map((opt) => (
        <Button
          key={opt.value}
          variant="contained"
          disabled={disabled}
          onClick={() => onSend(opt.value)}
          sx={{
            py: 1.1,
            px: 2,
            minHeight: 44,
            width: '100%',
            bgcolor: '#EFF6FF',
            color: '#0052CC',
            border: '1px solid #BFDBFE',
            fontWeight: 600,
            fontSize: { xs: '0.85rem', sm: '0.875rem' },
            textAlign: 'center',
            lineHeight: 1.3,
            whiteSpace: 'normal',
            wordBreak: 'break-word',
            borderRadius: '20px',
            '&:hover': {
              bgcolor: '#0052CC',
              color: '#FFFFFF',
            },
          }}
        >
          {opt.label}
        </Button>
      ))}
    </Box>
  );
};
