import React, { useState } from 'react';
import ChatInterface from './components/ChatInterface';
import DynamicDataView from './components/DynamicDataView';
import ApprovalModal from './components/ApprovalModal';
import { Database, ShieldAlert, Code } from 'lucide-react';

function App() {
  const [showApproval, setShowApproval] = useState(false);
  const [pendingQuery, setPendingQuery] = useState("");
  const [sqlData, setSqlData] = useState<any[] | null>(null);
  const [sqlQuery, setSqlQuery] = useState<string | null>(null);

  const handleDataReceived = (data: any[], query: string) => {
    setSqlData(data);
    setSqlQuery(query);
  };

  const handleRequireApproval = (query: string) => {
    setPendingQuery(query);
    setShowApproval(true);
  };

  const handleDecision = async (approved: boolean) => {
    setShowApproval(false);
    
    try {
      const response = await fetch('http://localhost:8000/resume', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approved })
      });
      const data = await response.json();
      
      if (data.requires_approval) {
        // It requires approval again! 
        handleRequireApproval(data.sql_query);
        return;
      }
      
      // Dispatch custom event for ChatInterface
      window.dispatchEvent(new CustomEvent('hitl_resume_result', { detail: data }));
      
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="min-h-screen bg-background text-textMain flex flex-col font-sans">
      <header className="border-b border-white/5 bg-surface/50 backdrop-blur-md px-6 py-4 flex justify-between items-center sticky top-0 z-40">
        <div className="flex items-center gap-3">
          <div className="bg-primary/20 p-2 rounded-lg">
            <Database className="text-primary" size={24} />
          </div>
          <h1 className="text-xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
            DataSleuth
          </h1>
        </div>
        <div className="flex items-center gap-2 text-sm text-green-400 bg-green-500/10 px-4 py-2 rounded-full font-medium">
          <ShieldAlert size={16} /> HITL Active
        </div>
      </header>

      <main className="flex-1 p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 overflow-hidden max-h-[calc(100vh-80px)]">
        <section className="lg:col-span-4 h-full flex flex-col">
          <ChatInterface 
            onDataReceived={handleDataReceived} 
            onRequireApproval={handleRequireApproval} 
          />
        </section>

        <section className="lg:col-span-8 h-full flex flex-col gap-4">
          <DynamicDataView data={sqlData || []} title="Query Results" />
          
          {sqlQuery && (
            <div className="glass p-4 rounded-xl text-sm font-mono text-gray-300 overflow-x-auto border-l-4 border-l-primary animate-slide-up">
              <div className="flex items-center gap-2 text-primary mb-2 font-sans font-semibold">
                <Code size={16} /> Generated SQL
              </div>
              {sqlQuery}
            </div>
          )}
        </section>
      </main>

      <ApprovalModal 
        isOpen={showApproval}
        actionDescription={pendingQuery}
        onApprove={() => handleDecision(true)}
        onReject={() => handleDecision(false)}
      />
    </div>
  );
}

export default App;
