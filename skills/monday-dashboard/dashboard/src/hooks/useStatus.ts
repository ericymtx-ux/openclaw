import { useEffect } from 'react';
import { useStatusStore } from '../store/status';
import { fetchStatus } from '../api/client';

export function useStatus(pollInterval = 2000) {
  const setStatus = useStatusStore(state => state.setStatus);
  
  useEffect(() => {
    const poll = async () => {
      try {
        const data = await fetchStatus();
        setStatus(data);
      } catch (err) {
        console.error('Failed to fetch status:', err);
      }
    };
    
    poll();
    const interval = setInterval(poll, pollInterval);
    return () => clearInterval(interval);
  }, [pollInterval, setStatus]);
}
