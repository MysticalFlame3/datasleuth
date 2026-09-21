import React from 'react';
import { AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

interface ApprovalModalProps {
  isOpen: boolean;
  actionDescription: string;
  onApprove: () => void;
  onReject: () => void;
}

export default function ApprovalModal({ isOpen, actionDescription, onApprove, onReject }: ApprovalModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-fade-in">
      <div className="glass w-full max-w-md rounded-2xl p-6 shadow-2xl border border-red-500/20 animate-slide-up mx-4">
        
        <div className="flex items-center gap-4 mb-6">
          <div className="p-3 bg-red-500/10 rounded-full text-red-400">
            <AlertTriangle size={28} />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Action Requires Approval</h2>
            <p className="text-textMuted text-sm">Human-in-the-loop intervention</p>
          </div>
        </div>

        <div className="bg-surface/50 rounded-lg p-4 mb-8 border border-white/5">
          <p className="text-sm font-mono text-gray-300">
            The agent is requesting to execute:
          </p>
          <p className="mt-2 text-white font-medium">
            "{actionDescription}"
          </p>
        </div>

        <div className="flex gap-3 justify-end">
          <button 
            onClick={onReject}
            className="flex items-center gap-2 px-5 py-2.5 rounded-lg font-medium bg-surfaceHover text-white hover:bg-gray-700 transition-colors border border-white/5"
          >
            <XCircle size={18} />
            Reject
          </button>
          <button 
            onClick={onApprove}
            className="flex items-center gap-2 px-5 py-2.5 rounded-lg font-medium bg-red-600 text-white hover:bg-red-700 transition-colors shadow-lg shadow-red-900/20"
          >
            <CheckCircle size={18} />
            Approve Action
          </button>
        </div>
      </div>
    </div>
  );
}
