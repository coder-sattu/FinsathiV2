import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#0052CC', // Claim Assist Royal Blue
      light: '#4C8DFF',
      dark: '#003D99',
    },
    secondary: {
      main: '#10B981', // Emerald Green
    },
    warning: {
      main: '#D97706', // Amber Mismatch
      light: '#FEF3C7',
    },
    background: {
      default: '#F4F6F9', // Clean light desktop canvas
      paper: '#FFFFFF',
    },
    text: {
      primary: '#1E293B', // Slate 800
      secondary: '#64748B', // Slate 500
    },
  },
  typography: {
    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    h6: {
      fontWeight: 700,
      fontSize: '1.15rem',
    },
    subtitle1: {
      fontWeight: 600,
      fontSize: '0.95rem',
    },
    subtitle2: {
      fontWeight: 600,
      fontSize: '0.875rem',
    },
    body1: {
      fontSize: '0.925rem',
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.85rem',
    },
    button: {
      textTransform: 'none',
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: '20px', // Pill buttons matching reference design
          padding: '6px 20px',
          boxShadow: 'none',
          fontWeight: 600,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: '16px',
          border: '1px solid #E2E8F0',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.04)',
        },
      },
    },
  },
});
