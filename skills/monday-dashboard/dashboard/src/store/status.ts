import { create } from 'zustand';
import { StatusResponse, Session } from '../types';

interface StatusStore {
  state: StatusResponse['state'];
  session: Session | null;
  tokenUsage: StatusResponse['tokenUsage'];
  lastHeartbeat: { lastText: string; sentAt: number };
  
  setStatus: (status: StatusResponse) => void;
}

export const useStatusStore = create<StatusStore>((set) => ({
  state: 'idle',
  session: null,
  tokenUsage: { input: 0, output: 0, total: 0 },
  lastHeartbeat: { lastText: '', sentAt: 0 },
  
  setStatus: (status) => set({
    state: status.state,
    session: status.currentSession,
    tokenUsage: status.tokenUsage,
    lastHeartbeat: status.heartbeat
  })
}));
