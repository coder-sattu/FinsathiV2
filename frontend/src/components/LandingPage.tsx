import React from 'react';
import { Box, Button, Card, Container, Typography } from '@mui/material';
import { FileText, Shield, Stethoscope, Wallet } from 'lucide-react';

interface Props {
  onStartClaim: () => void;
}

export const LandingPage: React.FC<Props> = ({ onStartClaim }) => {
  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#F8FAFC', color: '#1E293B' }}>
      {/* Website Navigation Header */}
      <Box sx={{ bgcolor: '#0052CC', color: '#FFF', py: 1.5, px: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Shield size={24} fill="#FFF" />
          <Typography variant="h6" sx={{ fontWeight: 700 }}>
            Your Insurance Co.
          </Typography>
        </Box>
        <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 3, fontSize: '0.9rem' }}>
          <span>Health plans</span>
          <span>Claims</span>
          <span>Renew policy</span>
          <span>Network hospitals</span>
          <span>Support</span>
        </Box>
        <Button variant="outlined" color="inherit" size="small" sx={{ borderRadius: '20px', borderColor: '#FFF' }}>
          Login
        </Button>
      </Box>

      {/* Hero Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '32px', alignItems: 'center' }}>
          <div>
            <Typography variant="h3" sx={{ fontWeight: 800, color: '#0F172A', mb: 2, lineHeight: 1.15 }}>
              Hospitalised? Intimate your claim in minutes.
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 4, fontSize: '1.1rem' }}>
              Cashless or reimbursement, our claim assistant guides you step by step, 24x7.
            </Typography>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                onClick={onStartClaim}
                sx={{ bgcolor: '#0052CC', px: 4, py: 1.5, borderRadius: '24px', fontSize: '1rem', '&:hover': { bgcolor: '#003D99' } }}
              >
                Intimate a claim
              </Button>
              <Button
                variant="outlined"
                sx={{ borderColor: '#0052CC', color: '#0052CC', px: 4, py: 1.5, borderRadius: '24px', fontSize: '1rem' }}
              >
                Track claim
              </Button>
            </Box>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <Card sx={{ p: 3, bgcolor: '#FFFFFF', borderRadius: '16px', border: '1px solid #E2E8F0' }}>
              <Typography variant="h5" sx={{ fontWeight: 700, color: '#0052CC' }}>
                10,000+
              </Typography>
              <Typography variant="caption" color="text.secondary">
                network hospitals
              </Typography>
            </Card>
            <Card sx={{ p: 3, bgcolor: '#FFFFFF', borderRadius: '16px', border: '1px solid #E2E8F0' }}>
              <Typography variant="h5" sx={{ fontWeight: 700, color: '#10B981' }}>
                15 days
              </Typography>
              <Typography variant="caption" color="text.secondary">
                claim processing
              </Typography>
            </Card>
          </div>
        </div>

        {/* Features Row */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '24px', marginTop: '48px' }}>
          <Card sx={{ p: 3, bgcolor: '#FFFFFF', borderRadius: '16px', border: '1px solid #E2E8F0' }}>
            <Stethoscope color="#0052CC" size={28} />
            <Typography variant="subtitle1" sx={{ fontWeight: 700, mt: 1.5 }}>
              Cashless treatment
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Get treated at a network hospital without paying upfront.
            </Typography>
          </Card>

          <Card sx={{ p: 3, bgcolor: '#FFFFFF', borderRadius: '16px', border: '1px solid #E2E8F0' }}>
            <Wallet color="#0052CC" size={28} />
            <Typography variant="subtitle1" sx={{ fontWeight: 700, mt: 1.5 }}>
              Reimbursement
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Paid the hospital yourself? Upload bills and get reimbursed.
            </Typography>
          </Card>

          <Card sx={{ p: 3, bgcolor: '#FFFFFF', borderRadius: '16px', border: '1px solid #E2E8F0' }}>
            <FileText color="#0052CC" size={28} />
            <Typography variant="subtitle1" sx={{ fontWeight: 700, mt: 1.5 }}>
              Form & Documents
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Automated document reader validates your uploads instantly.
            </Typography>
          </Card>
        </div>
      </Container>
    </Box>
  );
};
