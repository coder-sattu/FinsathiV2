import React, { useState } from 'react';
import { Box, Card, CardActionArea, CardContent, Chip, Radio, Typography } from '@mui/material';
import { Check } from 'lucide-react';
import type { UI } from '../../types';

interface Props {
  ui: UI;
  onSend: (value: any) => void;
  disabled?: boolean;
}

export const ListWidget: React.FC<Props> = ({ ui, onSend, disabled }) => {
  const [selectedVal, setSelectedVal] = useState<string | null>(null);

  const handleSelect = (val: string) => {
    setSelectedVal(val);
    onSend(val);
  };

  const isHospitalList = ui.options?.some((o) => o.data?.hospital_id || o.label.includes('Hospital'));

  if (isHospitalList) {
    return (
      <Box sx={{ mt: 1.25, width: '100%' }}>
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(auto-fit, minmax(220px, 1fr))' }, gap: '10px' }}>
          {ui.options?.map((opt) => {
            const hData = opt.data || {};
            const isSelected = selectedVal === opt.value;
            const approxCost = hData.approx_cost ? `Approx. ₹${Number(hData.approx_cost).toLocaleString('en-IN')}` : 'Approx. ₹1,50,000';

            return (
              <Card
                key={opt.value}
                elevation={0}
                sx={{
                  bgcolor: isSelected ? '#EFF6FF' : '#FFFFFF',
                  border: isSelected ? '2px solid #0052CC' : '1px solid #E2E8F0',
                  borderRadius: '12px',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    borderColor: '#0052CC',
                    bgcolor: '#F8FAFC',
                  },
                }}
              >
                <CardActionArea disabled={disabled} onClick={() => handleSelect(opt.value)} sx={{ p: { xs: 1.25, sm: 1.5 } }}>
                  <CardContent sx={{ p: 0, '&:last-child': { pb: 0 } }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 0.5, gap: 1 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#1E293B', fontSize: { xs: '0.85rem', sm: '0.9rem' } }}>
                        {opt.label}
                      </Typography>
                      <Radio
                        checked={isSelected}
                        size="small"
                        sx={{ p: 0, color: '#CBD5E1', '&.Mui-checked': { color: '#0052CC' }, flexShrink: 0 }}
                      />
                    </Box>

                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: { xs: 0.75, sm: 1 }, fontSize: { xs: '0.7rem', sm: '0.75rem' } }}>
                      {hData.address || opt.subtext}
                    </Typography>

                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: { xs: 0.75, sm: 1 }, flexWrap: 'wrap', gap: 0.5 }}>
                      <Chip
                        icon={<Check size={12} color="#10B981" />}
                        label={opt.badge || (hData.network ? 'Network' : 'Non-network')}
                        size="small"
                        sx={{
                          bgcolor: '#ECFDF5',
                          color: '#065F46',
                          fontWeight: 600,
                          fontSize: { xs: '0.65rem', sm: '0.7rem' },
                          height: 20,
                          border: '1px solid #A7F3D0',
                        }}
                      />
                      <Typography variant="caption" sx={{ fontWeight: 700, color: '#1E293B', fontSize: { xs: '0.7rem', sm: '0.75rem' } }}>
                        {approxCost}
                      </Typography>
                    </Box>
                  </CardContent>
                </CardActionArea>
              </Card>
            );
          })}
        </Box>
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1, fontSize: { xs: '0.65rem', sm: '0.725rem' }, fontStyle: 'italic' }}>
          ⓘ Approximate cost is indicative and is not a claim approval.
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mt: 1.25, width: '100%' }}>
      {ui.options?.map((opt) => (
        <Card
          key={opt.value}
          elevation={0}
          sx={{
            bgcolor: '#FFFFFF',
            border: '1px solid #E2E8F0',
            borderRadius: '12px',
            transition: 'all 0.2s ease',
            '&:hover': {
              borderColor: '#0052CC',
              bgcolor: '#F8FAFC',
            },
          }}
        >
          <CardActionArea disabled={disabled} onClick={() => onSend(opt.value)} sx={{ p: { xs: 1.25, sm: 1.5 } }}>
            <CardContent sx={{ p: 0, '&:last-child': { pb: 0 } }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 0.5, gap: 1 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#1E293B', fontSize: { xs: '0.85rem', sm: '0.9rem' } }}>
                  {opt.label}
                </Typography>
                {opt.badge && (
                  <Chip
                    label={opt.badge}
                    size="small"
                    color={opt.badge === 'Network' ? 'success' : 'warning'}
                    variant="outlined"
                    sx={{ height: 20, fontSize: '0.68rem', flexShrink: 0 }}
                  />
                )}
              </Box>
              {opt.subtext && (
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', fontSize: { xs: '0.7rem', sm: '0.75rem' } }}>
                  {opt.subtext}
                </Typography>
              )}
            </CardContent>
          </CardActionArea>
        </Card>
      ))}
    </Box>
  );
};
