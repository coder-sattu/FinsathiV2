import React, { useEffect, useRef, useState } from 'react';
import { Box, CircularProgress, IconButton, Paper, TextField, Typography } from '@mui/material';
import { Paperclip, Send } from 'lucide-react';
import type { MessageItem } from '../types';
import { MessageBubble } from './MessageBubble';

interface Props {
  messages: MessageItem[];
  loading: boolean;
  onSendInput: (value?: any, text?: string) => void;
  onUploadDoc: (docCode: string, file: File) => Promise<void>;
  onRestart: () => void;
}

export const ChatThread: React.FC<Props> = ({
  messages,
  loading,
  onSendInput,
  onUploadDoc,
  onRestart,
}) => {
  const [inputText, setInputText] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);

  const lastMsg = messages[messages.length - 1];
  const currentState = lastMsg?.reply?.state || '';
  const isDocState = currentState.toUpperCase().includes('DOC');

  const scrollToBottom = () => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleTextSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputText.trim() && !loading) {
      onSendInput(undefined, inputText.trim());
      setInputText('');
    }
  };

  const handleFileDrop = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const docCode = isDocState ? 'DISCHARGE_SUMMARY' : 'CLAIM_FORM';
      onUploadDoc(docCode, file);
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden', bgcolor: '#F8FAFC' }}>
      {/* Messages Scroll Area */}
      <Box
        sx={{
          flex: 1,
          minHeight: 0,
          overflowY: 'auto',
          overflowX: 'hidden',
          py: { xs: '18px', sm: 2.5 },
          px: { xs: '14px', sm: 3, md: 4 }, // 14-16px horizontal padding on iPhone
          display: 'flex',
          flexDirection: 'column',
          '&::-webkit-scrollbar': { width: 5 },
          '&::-webkit-scrollbar-thumb': { bgcolor: '#CBD5E1', borderRadius: 3 },
        }}
      >
        <Box sx={{ width: '100%', maxWidth: 860, mx: 'auto', display: 'flex', flexDirection: 'column', flex: 1 }}>
          {messages.map((item, idx) => (
            <MessageBubble
              key={item.id}
              item={item}
              isLatest={idx === messages.length - 1}
              onSend={(val, txt) => onSendInput(val, txt)}
              onUpload={onUploadDoc}
              onRestart={onRestart}
              disabled={loading}
            />
          ))}

          {loading && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, my: 1, color: 'text.secondary', ml: { xs: 4.5, sm: 5 } }}>
              <CircularProgress size={16} color="primary" />
              <Typography variant="caption" color="text.secondary">
                Assistant thinking...
              </Typography>
            </Box>
          )}

          <div ref={bottomRef} />
        </Box>
      </Box>

      {/* Input Bar matching reference image, fixed to bottom, supporting safe-area */}
      <Paper
        elevation={0}
        sx={{
          p: { xs: '12px', sm: 1.5 },
          px: { xs: '14px', sm: 3, md: 4 },
          pb: { xs: 'calc(12px + env(safe-area-inset-bottom, 0px))', sm: 1.5 },
          bgcolor: '#FFFFFF',
          borderTop: '1px solid #E2E8F0',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          flexShrink: 0,
          zIndex: 10,
          width: '100%',
          boxSizing: 'border-box',
        }}
      >
        <Box
          component="form"
          onSubmit={handleTextSubmit}
          sx={{
            width: '100%',
            maxWidth: 860,
            display: 'flex',
            alignItems: 'center',
            gap: { xs: 1, sm: 1.25 },
          }}
        >
          <IconButton
            component="label"
            size="small"
            disabled={loading}
            sx={{
              color: '#64748B',
              width: 36,
              height: 36,
              flexShrink: 0,
              '&:hover': { color: '#0052CC' },
            }}
          >
            <Paperclip size={20} />
            <input type="file" hidden accept=".pdf,.jpg,.jpeg,.png" onChange={handleFileDrop} />
          </IconButton>

          <TextField
            fullWidth
            size="small"
            placeholder={
              isDocState
                ? 'Type a message or drop a file...'
                : 'Type a message…'
            }
            value={inputText}
            disabled={loading}
            onChange={(e) => setInputText(e.target.value)}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: '22px',
                bgcolor: '#F1F5F9',
                fontSize: { xs: '14.5px', sm: '0.9rem' },
                height: { xs: 44, sm: 44 },
                border: '1px solid #E2E8F0',
                px: 1.75,
                '& fieldset': { border: 'none' },
              },
            }}
          />

          <IconButton
            type="submit"
            disabled={loading || !inputText.trim()}
            sx={{
              bgcolor: '#0052CC',
              color: '#FFFFFF',
              width: 44,
              height: 44,
              borderRadius: '50%',
              flexShrink: 0,
              '&:hover': { bgcolor: '#003D99' },
              '&.Mui-disabled': { bgcolor: '#DFE5EE', color: '#8A94A2' },
            }}
          >
            <Send size={18} />
          </IconButton>
        </Box>

        <Typography
          variant="caption"
          color="text.secondary"
          sx={{
            display: { xs: 'none', sm: 'block' },
            mt: 0.6,
            fontSize: { xs: '0.65rem', sm: '0.7rem' },
            textAlign: 'center',
            lineHeight: 1.25,
            px: 1,
            maxWidth: 600,
          }}
        >
          {isDocState
            ? 'PDF, JPG or PNG · max 5 MB per file'
            : "Your details are protected. Don't share Aadhaar, PAN or bank details in chat"}
        </Typography>
      </Paper>
    </Box>
  );
};