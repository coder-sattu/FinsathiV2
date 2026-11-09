import React, { useEffect, useState } from 'react';
import { Box, CssBaseline, ThemeProvider, Typography } from '@mui/material';
import { Wifi, Signal, Battery } from 'lucide-react';

import { getSession, sendMessage, startChat, uploadDoc } from './api';
import { Header } from './components/Header';
import { StepperBar } from './components/StepperBar';
import { ChatThread } from './components/ChatThread';
import { theme } from './theme';
import type { BotReply, MessageItem } from './types';

const SESSION_KEY = 'finsathi_session_id';

export const App: React.FC = () => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  const initChat = async () => {
    setLoading(true);
    try {
      const savedId = localStorage.getItem(SESSION_KEY);
      let reply: BotReply;

      if (savedId) {
        try {
          reply = await getSession(savedId);
        } catch {
          localStorage.removeItem(SESSION_KEY);
          reply = await startChat();
        }
      } else {
        reply = await startChat();
      }

      setSessionId(reply.session_id);
      localStorage.setItem(SESSION_KEY, reply.session_id);
      setMessages([
        {
          id: `bot-start-${Date.now()}`,
          sender: 'bot',
          reply,
          timestamp: new Date(),
        },
      ]);
    } catch (err: any) {
      console.error('Failed to init chat', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    initChat();
  }, []);

  const handleRestart = async () => {
    localStorage.removeItem(SESSION_KEY);
    await initChat();
  };

  const handleSendInput = async (value?: any, text?: string) => {
    if (!sessionId || loading) return;

    const userText = text || (typeof value === 'string' ? value : JSON.stringify(value));
    const userMsg: MessageItem = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: userText,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const reply = await sendMessage(sessionId, value, text);
      const botMsg: MessageItem = {
        id: `bot-${Date.now()}`,
        sender: 'bot',
        reply,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err: any) {
      const isSessionNotFound = err.message?.includes('Session not found');
      if (isSessionNotFound) {
        localStorage.removeItem(SESSION_KEY);
      }
      const errorMsg: MessageItem = {
        id: `bot-err-${Date.now()}`,
        sender: 'bot',
        text: isSessionNotFound ? 'Your previous session expired. Please start over.' : (err.message || 'An unexpected error occurred.'),
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadDoc = async (docCode: string, file: File) => {
    if (!sessionId || loading) return;

    const userMsg: MessageItem = {
      id: `user-up-${Date.now()}`,
      sender: 'user',
      text: `Uploading ${file.name} for ${docCode}...`,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const reply = await uploadDoc(sessionId, docCode, file);
      const botMsg: MessageItem = {
        id: `bot-up-${Date.now()}`,
        sender: 'bot',
        reply,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err: any) {
      const errorMsg: MessageItem = {
        id: `bot-up-err-${Date.now()}`,
        sender: 'bot',
        text: err.message || 'Failed to upload document.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const currentState = messages[messages.length - 1]?.reply?.state || 'CONSENT';

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          width: '100vw',
          height: '100dvh',
          bgcolor: '#DCE7FA', // Soft elegant light blue background matching screenshot
          backgroundImage: 'radial-gradient(circle at 50% 30%, #E6EEFF 0%, #DCE7FA 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          overflow: 'hidden',
          p: { xs: 0, sm: 2, md: 3 },
          boxSizing: 'border-box',
        }}
      >
        {/* iPhone Device Container */}
        <Box
          sx={{
            width: { xs: '100vw', sm: '390px' },
            height: { xs: '100dvh', sm: '830px' },
            maxHeight: { sm: '96dvh' },
            bgcolor: '#111827', // iPhone outer body black chassis
            borderRadius: { xs: 0, sm: '48px' },
            p: { xs: 0, sm: '10px' }, // Phone bezel border padding
            boxShadow: {
              xs: 'none',
              sm: '0 30px 70px -12px rgba(15, 23, 42, 0.4), 0 0 0 1px rgba(0, 0, 0, 0.25)',
            },
            position: 'relative',
            display: 'flex',
            flexDirection: 'column',
            boxSizing: 'border-box',
          }}
        >
          {/* Inner iPhone Screen Viewport */}
          <Box
            sx={{
              width: '100%',
              height: '100%',
              bgcolor: '#FFFFFF',
              borderRadius: { xs: 0, sm: '38px' },
              overflow: 'hidden',
              display: 'flex',
              flexDirection: 'column',
              position: 'relative',
            }}
          >
            {/* Top iOS Status Bar */}
            <Box
              sx={{
                height: { xs: 'calc(env(safe-area-inset-top, 0px) + 38px)', sm: 40 },
                bgcolor: '#0052CC',
                color: '#FFFFFF',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                px: 3,
                pt: { xs: 'env(safe-area-inset-top, 0px)', sm: 0.5 },
                position: 'relative',
                zIndex: 20,
                flexShrink: 0,
              }}
            >
              {/* Time */}
              <Typography
                sx={{
                  fontSize: '13.5px',
                  fontWeight: 600,
                  fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", Roboto',
                  letterSpacing: '-0.2px',
                }}
              >
                12:49
              </Typography>

              {/* iPhone Dynamic Island Notch */}
              <Box
                sx={{
                  position: 'absolute',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  top: { xs: 'calc(env(safe-area-inset-top, 0px) + 6px)', sm: 6 },
                  width: 105,
                  height: 25,
                  bgcolor: '#000000',
                  borderRadius: '16px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'flex-end',
                  pr: 1.2,
                }}
              >
                <Box
                  sx={{
                    width: 9,
                    height: 9,
                    borderRadius: '50%',
                    bgcolor: '#0E1726',
                    border: '1px solid #1E293B',
                  }}
                />
              </Box>

              {/* Cellular, Wifi & Battery Icons */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.65 }}>
                <Signal size={14} strokeWidth={2.5} />
                <Wifi size={14} strokeWidth={2.5} />
                <Battery size={16} strokeWidth={2.5} />
              </Box>
            </Box>

            {/* Header */}
            <Header onRestart={handleRestart} disabled={loading} />

            {/* Stepper Bar */}
            <StepperBar state={currentState} />

            {/* Main Chat Thread Area */}
            <Box sx={{ flex: 1, minHeight: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
              <ChatThread
                messages={messages}
                loading={loading}
                onSendInput={handleSendInput}
                onUploadDoc={handleUploadDoc}
                onRestart={handleRestart}
              />
            </Box>

            {/* iPhone Home Bar Line at Bottom */}
            <Box
              sx={{
                height: 16,
                bgcolor: '#FFFFFF',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                pb: 0.5,
                flexShrink: 0,
              }}
            >
              <Box
                sx={{
                  width: 130,
                  height: 4.5,
                  bgcolor: '#0F172A',
                  borderRadius: 3,
                }}
              />
            </Box>
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
};

export default App;
