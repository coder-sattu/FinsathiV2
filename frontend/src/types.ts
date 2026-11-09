export interface UIField {
  name: string;
  label: string;
  type: string;
  required?: boolean;
  value?: any;
  options_ref?: string;
  allow_other?: boolean;
  options?: Array<{ value: string; label: string }>;
}

export interface UIOption {
  value: string;
  label: string;
  subtext?: string;
  badge?: string;
  data?: Record<string, any>;
}

export interface UI {
  type: string;
  fields?: UIField[];
  options?: UIOption[];
  data?: Record<string, any>;
  disclaimer?: string;
  warnings?: string[];
}

export interface ChatError {
  field?: string;
  message: string;
}

export interface BotReply {
  session_id: string;
  state: string;
  messages: string[];
  ui: UI;
  error?: ChatError | null;
}

export interface MessageItem {
  id: string;
  sender: 'user' | 'bot';
  text?: string;
  reply?: BotReply;
  timestamp: Date;
}
