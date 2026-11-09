import React from 'react';
import { Box, Typography } from '@mui/material';
import { Check } from 'lucide-react';

interface Props {
  state: string;
}

export const StepperBar: React.FC<Props> = ({ state }) => {
  const getStepStatus = () => {
    const s = state.toUpperCase();

    if (s.includes('DOC') || s.includes('DONE') || s.includes('SR_PENDING')) {
      return 4;
    }
    if (
      s.includes('PATIENT') ||
      s.includes('ADMISSION') ||
      s.includes('HOSPITAL') ||
      s.includes('NON_NETWORK') ||
      s.includes('REVIEW')
    ) {
      return 3;
    }
    if (s.includes('CLAIM_TYPE') || s.includes('SELF_I') || s.includes('DOA')) {
      return 2;
    }
    return 1;
  };

  const currentStep = getStepStatus();

  const isDocFlow = state.toUpperCase().includes('DOC') || state.toUpperCase().includes('SR_PENDING');

  const desktopSteps = [
    { num: 1, label: 'Login' },
    { num: 2, label: 'Claim type' },
    { num: 3, label: 'Details' },
    { num: 4, label: isDocFlow ? 'Documents' : 'Review & submit' },
  ];

  const mobileSteps = [
    { num: 1, label: 'Login' },
    { num: 2, label: 'Claim' },
    { num: 3, label: 'Details' },
    { num: 4, label: isDocFlow ? 'Docs' : 'Review' },
  ];

  return (
    <Box
      sx={{
        py: { xs: 1, sm: 1.2 },
        px: { xs: 2, sm: 3 },
        bgcolor: '#FFFFFF',
        borderBottom: '1px solid #E2E8F0',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        width: '100%',
        boxSizing: 'border-box',
        overflow: 'hidden',
        flexShrink: 0,
      }}
    >
      {/* Horizontal Steps: Shortened labels, 20px circles, 11-12px font, short connectors */}
      <Box sx={{ display: 'flex', width: '100%', justifyContent: 'space-between', alignItems: 'center' }}>
        {mobileSteps.map((step, idx) => {
          const isCompleted = step.num < currentStep;
          const isActive = step.num === currentStep;

          return (
            <React.Fragment key={step.num}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, flexShrink: 0 }}>
                <Box
                  sx={{
                    width: 20,
                    height: 20,
                    borderRadius: '50%',
                    bgcolor: isCompleted
                      ? '#10B981'
                      : isActive
                      ? '#0052CC'
                      : 'transparent',
                    border: isCompleted || isActive ? 'none' : '1.5px solid #CBD5E1',
                    color: isCompleted || isActive ? '#FFFFFF' : '#64748B',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '11px',
                    fontWeight: 700,
                    flexShrink: 0,
                  }}
                >
                  {isCompleted ? <Check size={12} strokeWidth={3} /> : step.num}
                </Box>
                <Typography
                  variant="body2"
                  sx={{
                    fontWeight: isActive || isCompleted ? 600 : 500,
                    color: isCompleted
                      ? '#10B981'
                      : isActive
                      ? '#0052CC'
                      : '#64748B',
                    fontSize: '11.5px',
                    whiteSpace: 'nowrap',
                    lineHeight: 1,
                  }}
                >
                  {step.label}
                </Typography>
              </Box>

              {idx < mobileSteps.length - 1 && (
                <Box
                  sx={{
                    flex: 1,
                    minWidth: 8,
                    mx: 0.5,
                    height: 1.5,
                    bgcolor: step.num < currentStep ? '#10B981' : '#E2E8F0',
                    borderRadius: 1,
                  }}
                />
              )}
            </React.Fragment>
          );
        })}
      </Box>
    </Box>
  );
};
