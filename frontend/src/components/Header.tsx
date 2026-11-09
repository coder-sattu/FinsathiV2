import React from 'react';
import { Box, Button, IconButton, Typography } from '@mui/material';
import { Phone, RefreshCw, Shield } from 'lucide-react';

interface Props {
  onRestart: () => void;
  disabled?: boolean;
}

export const Header: React.FC<Props> = ({ onRestart, disabled }) => {
  return (
    <Box
      sx={{
        pt: 'calc(env(safe-area-inset-top, 0px) + 8px)',
        pb: { xs: 2, sm: 1.25 },
        px: { xs: 1.75, sm: 2.5, md: 3 },
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        bgcolor: '#0052CC', // Claim Assist Navy Blue
        color: '#FFFFFF',
        flexShrink: 0,
        width: '100%',
        boxSizing: 'border-box',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: { xs: 1, sm: 1.5 }, minWidth: 0 }}>
        <Box
          sx={{
            width: { xs: 34, sm: 38 },
            height: { xs: 34, sm: 38 },
            borderRadius: '50%',
            bgcolor: '#FFFFFF',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          <Box sx={{ display: { xs: 'block', sm: 'none' } }}>
            <Shield color="#0052CC" size={19} fill="#0052CC" />
          </Box>
          <Box sx={{ display: { xs: 'none', sm: 'block' } }}>
            <Shield color="#0052CC" size={22} fill="#0052CC" />
          </Box>
        </Box>
        <Box sx={{ minWidth: 0 }}>
          <Typography
            variant="h6"
            sx={{
              fontWeight: 700,
              color: '#FFFFFF',
              lineHeight: 1.15,
              fontSize: { xs: '1rem', sm: '1.15rem' },
              whiteSpace: 'nowrap',
            }}
          >
            Claim Assist
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.2 }}>
            <Box
              sx={{
                width: 6,
                height: 6,
                borderRadius: '50%',
                bgcolor: '#10B981',
                flexShrink: 0,
              }}
            />
            <Typography
              variant="caption"
              sx={{
                color: 'rgba(255, 255, 255, 0.85)',
                fontSize: { xs: '0.68rem', sm: '0.75rem' },
                lineHeight: 1,
                whiteSpace: 'nowrap',
              }}
            >
              <Box component="span" sx={{ display: { xs: 'none', sm: 'inline' } }}>Health insurance claim intimation</Box>
              <Box component="span" sx={{ display: { xs: 'inline', sm: 'none' } }}>Health insurance claim intimation</Box>
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Action Buttons: 36px circular icon buttons with white outline */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexShrink: 0 }}>
        <IconButton
          component="a"
          href="tel:18000000000"
          size="small"
          title="Helpline 1800-000-0000"
          sx={{
            width: 36,
            height: 36,
            borderRadius: '50%',
            border: '1px solid rgba(255, 255, 255, 0.35)',
            bgcolor: 'rgba(255, 255, 255, 0.15)',
            color: '#FFFFFF',
            p: 0,
            '&:hover': {
              border: '1px solid #FFFFFF',
              bgcolor: 'rgba(255, 255, 255, 0.25)',
            },
          }}
        >
          <Phone size={16} />
        </IconButton>

        <IconButton
          size="small"
          disabled={disabled}
          onClick={onRestart}
          title="Restart Chat"
          sx={{
            width: 36,
            height: 36,
            borderRadius: '50%',
            border: '1px solid rgba(255, 255, 255, 0.35)',
            bgcolor: 'rgba(255, 255, 255, 0.15)',
            color: '#FFFFFF',
            p: 0,
            '&:hover': {
              border: '1px solid #FFFFFF',
              bgcolor: 'rgba(255, 255, 255, 0.25)',
            },
            '&.Mui-disabled': { color: 'rgba(255,255,255,0.6)' },
          }}
        >
          <RefreshCw size={16} />
        </IconButton>
      </Box>
    </Box>
  );
};