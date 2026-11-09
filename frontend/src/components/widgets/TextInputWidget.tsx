import React, { useState } from 'react';
import { Box, TextField, IconButton } from '@mui/material';
import { Send } from 'lucide-react';

interface Props {
  onSend: (value: string) => void;
  disabled?: boolean;
  placeholder?: string;
  type?: string;
}

export const TextInputWidget: React.FC<Props> = ({
  onSend,
  disabled,
  placeholder = 'Type your response...',
  type = 'text',
}) => {
  const [val, setVal] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (val.trim() && !disabled) {
      onSend(val.trim());
      setVal('');
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', gap: 1, mt: 1.25, width: '100%' }}>
      <TextField
        fullWidth
        size="small"
        type={type}
        variant="outlined"
        placeholder={placeholder}
        value={val}
        disabled={disabled}
        onChange={(e) => setVal(e.target.value)}
        sx={{
          '& .MuiOutlinedInput-root': {
            bgcolor: '#FFFFFF',
            borderRadius: '12px',
            color: '#1E293B',
            fontSize: { xs: '16px', sm: '0.9rem' },
            minHeight: 44,
            '& fieldset': { borderColor: '#CBD5E1' },
            '&:hover fieldset': { borderColor: '#0052CC' },
          },
        }}
      />
      <IconButton
        type="submit"
        disabled={disabled || !val.trim()}
        sx={{
          bgcolor: '#0052CC',
          color: '#FFF',
          width: 44,
          height: 44,
          flexShrink: 0,
          borderRadius: '12px',
          '&:hover': { bgcolor: '#003D99' },
          '&.Mui-disabled': { bgcolor: '#E2E8F0', color: '#94A3B8' },
        }}
      >
        <Send size={18} />
      </IconButton>
    </Box>
  );
};
