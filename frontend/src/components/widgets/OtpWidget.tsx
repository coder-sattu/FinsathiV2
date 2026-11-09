import React, { useState } from 'react';
import { Box, Button, TextField, Typography } from '@mui/material';
import { KeyRound } from 'lucide-react';

interface Props {
  onSend: (value: string) => void;
  disabled?: boolean;
}

export const OtpWidget: React.FC<Props> = ({ onSend, disabled }) => {
  const [otp, setOtp] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (otp.length === 6 && !disabled) {
      onSend(otp);
    }
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
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
        <KeyRound color="#D97706" size={18} />
        <Typography variant="body2" sx={{ fontWeight: 600, color: '#1E293B', fontSize: { xs: '0.8rem', sm: '0.875rem' } }}>
          Enter 6-Digit OTP (Dev default: 123456)
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', gap: 1, flexDirection: { xs: 'column', sm: 'row' } }}>
        <TextField
          fullWidth
          size="small"
          placeholder="123456"
          slotProps={{ htmlInput: { maxLength: 6, inputMode: 'numeric', pattern: '[0-9]*' } }}
          sx={{
            '& .MuiOutlinedInput-root': {
              bgcolor: '#F8FAFC',
              borderRadius: '12px',
              color: '#1E293B',
              minHeight: 44,
              '& fieldset': { borderColor: '#CBD5E1' },
              '&:hover fieldset': { borderColor: '#0052CC' },
            },
            input: { textAlign: 'center', letterSpacing: { xs: 4, sm: 6 }, fontSize: '1.1rem', fontWeight: 600 },
          }}
          value={otp}
          disabled={disabled}
          onChange={(e) => setOtp(e.target.value)}
        />
        <Button
          type="submit"
          variant="contained"
          color="primary"
          disabled={disabled || otp.length !== 6}
          sx={{
            minWidth: { xs: '100%', sm: 100 },
            minHeight: 44,
            borderRadius: '20px',
            bgcolor: '#0052CC',
            '&:hover': { bgcolor: '#003D99' },
          }}
        >
          Verify
        </Button>
      </Box>
    </Box>
  );
};
