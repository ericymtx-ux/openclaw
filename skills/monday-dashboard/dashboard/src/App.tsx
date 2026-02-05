;
import { Mascot } from './components/Mascot';
import { useStatus } from './hooks/useStatus';
import { useStatusStore } from './store/status';

function App() {
  useStatus();
  const { session, tokenUsage } = useStatusStore();

  return (
    <div className="min-h-screen p-8 flex flex-col items-center">
      <header className="w-full max-w-6xl flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Monday Dashboard</h1>
        <div className="text-sm text-gray-500">
          Session: {session?.sessionId || 'None'}
        </div>
      </header>

      <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Left Sidebar: Status & Mascot */}
        <div className="lg:col-span-1 flex flex-col items-center bg-white p-6 rounded-xl shadow-sm">
          <Mascot />
          
          <div className="mt-8 w-full space-y-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Token Usage</h3>
              <div className="flex justify-between text-sm">
                <span>Input</span>
                <span className="font-mono">{tokenUsage.input}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Output</span>
                <span className="font-mono">{tokenUsage.output}</span>
              </div>
              <div className="border-t mt-2 pt-2 flex justify-between font-bold">
                <span>Total</span>
                <span className="font-mono">{tokenUsage.total}</span>
              </div>
            </div>

            {session?.lastHeartbeatText && (
              <div className="p-4 bg-blue-50 rounded-lg">
                <h3 className="text-xs font-semibold text-blue-400 uppercase tracking-wider mb-2">Last Activity</h3>
                <p className="text-sm text-blue-800 italic">"{session.lastHeartbeatText}"</p>
              </div>
            )}
          </div>
        </div>

        {/* Right Content: Boards */}
        <div className="lg:col-span-3 bg-white p-6 rounded-xl shadow-sm min-h-[600px]">
          <div className="flex space-x-4 border-b mb-6">
            <button className="px-4 py-2 border-b-2 border-blue-500 font-medium text-blue-600">TODOs</button>
            <button className="px-4 py-2 text-gray-500 hover:text-gray-700">Ideas</button>
            <button className="px-4 py-2 text-gray-500 hover:text-gray-700">Projects</button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Placeholder for Columns */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-3 flex items-center justify-between">
                Pending <span className="bg-gray-200 text-xs px-2 py-1 rounded-full">0</span>
              </h3>
              <div className="space-y-2">
                {/* Items will go here */}
              </div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-3 flex items-center justify-between">
                In Progress <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">0</span>
              </h3>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-3 flex items-center justify-between">
                Completed <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">0</span>
              </h3>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
