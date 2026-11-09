import React, { useState } from 'react';
import {
  Box,
  Button,
  Chip,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Paper,
  Typography,
} from '@mui/material';
import { Check, FileText, Upload } from 'lucide-react';
import type { UI } from '../../types';

interface Props {
  ui: UI;
  onUpload: (docCode: string, file: File) => Promise<void>;
  onSend: (value: any) => void;
  disabled?: boolean;
}

export const FileWidget: React.FC<Props> = ({ ui, onUpload, onSend, disabled }) => {
  const [uploadingCode, setUploadingCode] = useState<string | null>(null);
  const checklist = ui.data?.checklist || [];

  const handleFileChange = async (docCode: string, e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadingCode(docCode);
      try {
        await onUpload(docCode, file);
      } finally {
        setUploadingCode(null);
      }
    }
  };

  return (
    <Paper
      elevation={0}
      sx={{
        p: { xs: 1.25, sm: 2 },
        mt: 1.25,
        borderRadius: '16px',
        bgcolor: '#FFFFFF',
        border: '1px solid #E2E8F0',
        boxShadow: '0 4px 14px rgba(0, 0, 0, 0.03)',
        width: '100%',
        boxSizing: 'border-box',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: { xs: 1, sm: 1.5 } }}>
        <FileText color="#0052CC" size={18} />
        <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#1E293B', fontSize: { xs: '0.85rem', sm: '0.875rem' } }}>
          Required Documents Checklist
        </Typography>
      </Box>

      <List disablePadding sx={{ mb: { xs: 1, sm: 1.5 } }}>
        {checklist.map((item: any) => (
          <ListItem
            key={item.code}
            sx={{
              px: { xs: 1, sm: 1.5 },
              py: { xs: 0.75, sm: 1 },
              mb: { xs: 0.75, sm: 1 },
              borderRadius: '12px',
              bgcolor: item.uploaded ? '#F0FDF4' : '#F8FAFC',
              border: item.uploaded ? '1px solid #BBF7D0' : '1px solid #E2E8F0',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              gap: 1,
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.2, minWidth: 0 }}>
              {item.uploaded ? (
                <Check color="#10B981" size={18} strokeWidth={2.5} style={{ flexShrink: 0 }} />
              ) : (
                <FileText color="#64748B" size={18} style={{ flexShrink: 0 }} />
              )}
              <ListItemText
                sx={{ minWidth: 0, m: 0 }}
                primary={
                  <Typography variant="body2" sx={{ fontWeight: 600, color: '#1E293B', fontSize: { xs: '0.8rem', sm: '0.875rem' }, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {item.name}
                  </Typography>
                }
                secondary={
                  <Typography variant="caption" sx={{ color: '#64748B', fontSize: '0.725rem', display: 'block' }}>
                    {item.uploaded ? `${item.file_name || 'document.pdf'} · 412 KB` : 'Pending upload'}
                  </Typography>
                }
              />
            </Box>

            {item.uploaded ? (
              <Chip
                label="Done"
                size="small"
                sx={{
                  bgcolor: '#DCFCE7',
                  color: '#15803D',
                  fontWeight: 600,
                  fontSize: '0.7rem',
                  height: 22,
                  flexShrink: 0,
                }}
              />
            ) : uploadingCode === item.code ? (
              <Chip
                icon={<CircularProgress size={12} color="inherit" />}
                label="Checking"
                size="small"
                sx={{
                  bgcolor: '#EFF6FF',
                  color: '#1D4ED8',
                  fontWeight: 600,
                  fontSize: '0.7rem',
                  height: 22,
                  flexShrink: 0,
                }}
              />
            ) : (
              <Button
                variant="outlined"
                size="small"
                component="label"
                disabled={disabled}
                startIcon={<Upload size={13} />}
                sx={{
                  fontSize: '0.75rem',
                  borderRadius: '16px',
                  borderColor: '#0052CC',
                  color: '#0052CC',
                  px: 1.5,
                  py: 0.4,
                  minHeight: 32,
                  flexShrink: 0,
                }}
              >
                Upload
                <input
                  type="file"
                  hidden
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={(e) => handleFileChange(item.code, e)}
                />
              </Button>
            )}
          </ListItem>
        ))}
      </List>

      {ui.options?.map((opt) => (
        <Button
          key={opt.value}
          variant="outlined"
          color="inherit"
          fullWidth
          disabled={disabled}
          onClick={() => onSend(opt.value)}
          sx={{ borderRadius: '20px', minHeight: 44, fontSize: '0.825rem', color: '#64748B', borderColor: '#CBD5E1' }}
        >
          {opt.label}
        </Button>
      ))}
    </Paper>
  );
};
