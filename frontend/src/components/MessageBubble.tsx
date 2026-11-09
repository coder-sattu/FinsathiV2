import React from 'react';
import { Alert, Avatar, Box, Paper, Typography } from '@mui/material';
import { Shield, User } from 'lucide-react';
import type { MessageItem } from '../types';
import { ButtonsWidget } from './widgets/ButtonsWidget';
import { ConsentWidget } from './widgets/ConsentWidget';
import { ExtractionWidget } from './widgets/ExtractionWidget';
import { FileWidget } from './widgets/FileWidget';
import { FormWidget } from './widgets/FormWidget';
import { HandoffWidget } from './widgets/HandoffWidget';
import { ListWidget } from './widgets/ListWidget';
import { OtpWidget } from './widgets/OtpWidget';
import { SummaryWidget } from './widgets/SummaryWidget';
import { TextInputWidget } from './widgets/TextInputWidget';

interface Props {
  item: MessageItem;
  isLatest: boolean;
  onSend: (value: any, text?: string) => void;
  onUpload: (docCode: string, file: File) => Promise<void>;
  onRestart: () => void;
  disabled?: boolean;
}

export const MessageBubble: React.FC<Props> = ({
  item,
  isLatest,
  onSend,
  onUpload,
  onRestart,
  disabled,
}) => {
  const isUser = item.sender === 'user';
  const reply = item.reply;
  const ui = reply?.ui;

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: isUser ? 'flex-end' : 'flex-start',
        mb: { xs: 1.5, sm: 2 },
        width: '100%',
      }}
    >
      <Box
        sx={{
          display: 'flex',
          gap: { xs: 1, sm: 1.25 },
          maxWidth: isUser ? { xs: '85%', sm: '75%' } : '100%',
          width: isUser ? 'auto' : '100%',
          flexDirection: isUser ? 'row-reverse' : 'row',
        }}
      >
        <Avatar
          sx={{
            width: 32,
            height: 32,
            bgcolor: '#0052CC',
            boxShadow: { xs: 'none', sm: '0 2px 8px rgba(0, 82, 204, 0.2)' },
            flexShrink: 0,
            mt: 0.25,
          }}
        >
          {isUser ? <User size={15} color="#FFF" /> : <Shield size={15} color="#FFF" fill="#FFF" />}
        </Avatar>

        <Box sx={{ flex: 1, minWidth: 0, width: '100%' }}>
          {item.text && (
            <Paper
              elevation={0}
              sx={{
                p: { xs: 1.25, sm: 1.5 },
                px: { xs: 1.75, sm: 2.25 },
                borderRadius: isUser ? '20px 20px 4px 20px' : { xs: '4px 18px 18px 18px', sm: '20px 20px 20px 4px' },
                bgcolor: isUser ? '#0052CC' : '#FFFFFF',
                color: isUser ? '#FFFFFF' : '#1E293B',
                border: isUser ? 'none' : '1px solid #E2E8F0',
                boxShadow: isUser ? '0 4px 12px rgba(0, 82, 204, 0.25)' : '0 2px 8px rgba(0, 0, 0, 0.03)',
                display: 'inline-block',
                maxWidth: '100%',
                wordBreak: 'break-word',
              }}
            >
              <Typography variant="body1" sx={{ wordBreak: 'break-word', fontWeight: isUser ? 500 : 400, fontSize: { xs: '14.5px', sm: '0.925rem' }, lineHeight: 1.5 }}>
                {item.text}
              </Typography>
            </Paper>
          )}

          {reply?.messages && reply.messages.length > 0 && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mt: item.text ? 1 : 0 }}>
              {reply.messages.map((msg, idx) => (
                <Paper
                  key={idx}
                  elevation={0}
                  sx={{
                    p: { xs: '13px', sm: 1.5 },
                    px: { xs: '15px', sm: 2.25 },
                    borderRadius: { xs: '4px 18px 18px 18px', sm: '20px 20px 20px 4px' },
                    bgcolor: '#FFFFFF',
                    color: '#1E293B',
                    border: '1px solid #E2E8F0',
                    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.03)',
                    wordBreak: 'break-word',
                  }}
                >
                  <Typography variant="body1" sx={{ wordBreak: 'break-word', color: '#1E293B', fontSize: { xs: '14.5px', sm: '0.925rem' }, lineHeight: 1.5 }}>
                    {msg}
                  </Typography>
                </Paper>
              ))}
            </Box>
          )}

          {reply?.error && (
            <Alert severity="error" sx={{ mt: 1, borderRadius: 3 }}>
              {reply.error.message}
            </Alert>
          )}

          {ui?.warnings && ui.warnings.length > 0 && (
            <Box sx={{ mt: 1 }}>
              {ui.warnings.map((w, idx) => (
                <Alert key={idx} severity="warning" sx={{ mb: 0.5, borderRadius: 3 }}>
                  {w}
                </Alert>
              ))}
            </Box>
          )}

          {/* Render Active UI Widgets only for the latest message */}
          {ui && isLatest && (
            <Box sx={{ mt: 1 }}>
              {ui.type === 'consent' && <ConsentWidget ui={ui} onSend={(val) => onSend(val)} disabled={disabled} />}
              {ui.type === 'buttons' && <ButtonsWidget ui={ui} onSend={(val) => onSend(val)} disabled={disabled} />}
              {ui.type === 'text' && <TextInputWidget onSend={(val) => onSend(val)} disabled={disabled} />}
              {ui.type === 'date' && <TextInputWidget type="date" onSend={(val) => onSend(val)} disabled={disabled} />}
              {ui.type === 'otp' && <OtpWidget onSend={(val) => onSend(val)} disabled={disabled} />}
              {ui.type === 'list' && <ListWidget ui={ui} onSend={(val) => onSend(val)} disabled={disabled} />}
              {ui.type === 'form' && <FormWidget ui={ui} onSend={(val) => onSend(val)} disabled={disabled} />}
              {ui.type === 'summary' && <SummaryWidget ui={ui} onSend={(val) => onSend(val)} disabled={disabled} />}
              {ui.type === 'file' && <FileWidget ui={ui} onUpload={onUpload} onSend={(val) => onSend(val)} disabled={disabled} />}
              {ui.type === 'extraction' && <ExtractionWidget ui={ui} onSend={(val) => onSend(val)} disabled={disabled} />}
              {ui.type === 'handoff' && <HandoffWidget onRestart={onRestart} />}
            </Box>
          )}
        </Box>
      </Box>

      <Typography variant="caption" color="text.secondary" sx={{ mt: 0.75, px: { xs: 0, sm: 1 }, ml: { xs: isUser ? 0 : '41px', sm: 0 }, fontSize: { xs: '11px', sm: '0.65rem' } }}>
        {item.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
      </Typography>
    </Box>
  );
};