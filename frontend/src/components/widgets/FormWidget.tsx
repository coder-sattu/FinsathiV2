import React, { useState } from 'react';
import {
  Box,
  Button,
  FormControl,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  TextField,
  Typography,
} from '@mui/material';
import { ClipboardList } from 'lucide-react';
import type { UI } from '../../types';

interface Props {
  ui: UI;
  onSend: (value: any) => void;
  disabled?: boolean;
}

export const FormWidget: React.FC<Props> = ({ ui, onSend, disabled }) => {
  const initialValues: Record<string, any> = {};
  ui.fields?.forEach((f) => {
    initialValues[f.name] = f.value || (f.options && f.options.length > 0 ? f.options[0].value : '');
  });

  const [formData, setFormData] = useState<Record<string, any>>(initialValues);

  const handleChange = (name: string, val: any) => {
    setFormData((prev) => ({ ...prev, [name]: val }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!disabled) {
      onSend(formData);
    }
  };

  return (
    <Paper
      component="form"
      onSubmit={handleSubmit}
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
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: { xs: 1.2, sm: 1.5 } }}>
        <ClipboardList color="#0052CC" size={18} />
        <Typography variant="subtitle2" sx={{ color: '#0052CC', fontWeight: 600, fontSize: { xs: '0.85rem', sm: '0.875rem' } }}>
          Please Fill Details
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: { xs: 1.25, sm: 1.75 } }}>
        {ui.fields?.map((field) => {
          if (field.type === 'select' || field.type === 'search_select') {
            return (
              <FormControl key={field.name} fullWidth size="small">
                <InputLabel id={`label-${field.name}`} sx={{ color: '#64748B', fontSize: { xs: '0.85rem', sm: '0.9rem' } }}>{field.label}</InputLabel>
                <Select
                  labelId={`label-${field.name}`}
                  label={field.label}
                  value={formData[field.name] || ''}
                  disabled={disabled}
                  onChange={(e) => handleChange(field.name, e.target.value)}
                  sx={{
                    bgcolor: '#F8FAFC',
                    color: '#1E293B',
                    borderRadius: '12px',
                    fontSize: { xs: '16px', sm: '0.875rem' },
                    minHeight: 44,
                    '& .MuiOutlinedInput-notchedOutline': { borderColor: '#CBD5E1' },
                    '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#0052CC' },
                  }}
                >
                  {field.options?.map((opt) => (
                    <MenuItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            );
          }

          return (
            <TextField
              key={field.name}
              fullWidth
              size="small"
              label={field.label}
              type={field.type === 'date' ? 'date' : field.type === 'email' ? 'email' : 'text'}
              slotProps={{ inputLabel: field.type === 'date' ? { shrink: true, sx: { color: '#64748B', fontSize: { xs: '0.85rem', sm: '0.9rem' } } } : { sx: { color: '#64748B', fontSize: { xs: '0.85rem', sm: '0.9rem' } } } }}
              value={formData[field.name] || ''}
              disabled={disabled}
              onChange={(e) => handleChange(field.name, e.target.value)}
              sx={{
                '& .MuiOutlinedInput-root': {
                  bgcolor: '#F8FAFC',
                  borderRadius: '12px',
                  color: '#1E293B',
                  fontSize: { xs: '16px', sm: '0.875rem' },
                  minHeight: 44,
                  '& fieldset': { borderColor: '#CBD5E1' },
                  '&:hover fieldset': { borderColor: '#0052CC' },
                },
              }}
            />
          );
        })}

        <Button
          type="submit"
          variant="contained"
          color="primary"
          disabled={disabled}
          sx={{
            mt: 0.5,
            py: 1.1,
            minHeight: 44,
            borderRadius: '20px',
            bgcolor: '#0052CC',
            '&:hover': { bgcolor: '#003D99' },
          }}
        >
          Save & Proceed
        </Button>
      </Box>
    </Paper>
  );
};
