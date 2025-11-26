
export type Sender = 'bot' | 'user';

export interface UserProfile {
  gender?: 'مرد' | 'زن';
  age?: string;
  weight?: string;
  height?: string;
  level?: string;
  goal?: string;
  location?: string;
  frequency?: string;
  duration?: string;
  injuries?: string;
  sleep?: string;
  diet?: string;
  bodyType?: string;
  targetAreas?: string;
  history?: string;
  style?: string;
  motivation?: string;
  photo?: string;
  period?: 'بله' | 'خیر' | 'ناگفته';
  crowded?: string;
}

export interface Message {
  id: string;
  sender: Sender;
  text: string;
  isTyping?: boolean;
  type?: 'text' | 'card';
  cardData?: UserProfile;
}

export interface Question {
  id: keyof UserProfile;
  text: (profile: UserProfile) => string;
  placeholder: string;
  condition?: (profile: UserProfile) => boolean;
  inputType?: 'text' | 'image';
  validate?: (value: string) => string | null; // Returns error message if invalid, null if valid
  options?: string[]; // Quick reply options
}
