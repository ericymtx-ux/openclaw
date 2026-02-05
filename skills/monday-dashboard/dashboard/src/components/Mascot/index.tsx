;
import { useStatusStore } from '../../store/status';
import './Mascot.css';

export function Mascot() {
  const state = useStatusStore(s => s.state);
  
  return (
    <div className={`mascot-container ${state}`}>
      <div className="mascot-body">
        <div className="mascot-face">
          <div className="mascot-eyes">
            <div className="eye left"></div>
            <div className="eye right"></div>
          </div>
          <div className="mascot-mouth"></div>
        </div>
      </div>
      <div className="mascot-status-label">{state.toUpperCase()}</div>
    </div>
  );
}
