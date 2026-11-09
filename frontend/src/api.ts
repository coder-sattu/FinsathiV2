import type { BotReply } from './types';


const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8080/chat';

export async function startChat(): Promise<BotReply> {
  const res = await fetch(`${API_BASE}/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) {
    throw new Error('Failed to start chat session');
  }
  return res.json();
}

export async function sendMessage(
  sessionId: string,
  inputValue?: any,
  inputText?: string
): Promise<BotReply> {
  const res = await fetch(`${API_BASE}/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      input: {
        value: inputValue,
        text: inputText,
      },
    }),
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || 'Failed to send message');
  }
  return res.json();
}

export async function uploadDoc(
  sessionId: string,
  docCode: string,
  file: File
): Promise<BotReply> {
  const formData = new FormData();
  formData.append('session_id', sessionId);
  formData.append('doc_code', docCode);
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || 'Failed to upload document');
  }
  return res.json();
}

export async function getSession(sessionId: string): Promise<BotReply> {
  const res = await fetch(`${API_BASE}/session/${sessionId}`);
  if (!res.ok) {
    throw new Error('Failed to retrieve session');
  }
  return res.json();
}
