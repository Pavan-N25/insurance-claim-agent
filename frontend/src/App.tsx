import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { DashboardPage } from './pages/DashboardPage';
import { ClaimsListPage } from './pages/ClaimsListPage';
import { ClaimDetailPage } from './pages/ClaimDetailPage';
import { CustomerPortalPage } from './pages/CustomerPortalPage';
import { FraudNetworkPage } from './pages/FraudNetworkPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { CopilotPage } from './pages/CopilotPage';
import { KnowledgePage } from './pages/KnowledgePage';
import { AdminSettingsPage } from './pages/AdminSettingsPage';
import { AuditLogPage } from './pages/AuditLogPage';
import { LivePipelineModal } from './components/LivePipelineModal';
import { apiClient } from './api/client';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [selectedClaimId, setSelectedClaimId] = useState<string | null>(null);
  const [userRole, setUserRole] = useState<string>('reviewer');

  // Live Pipeline WebSocket Modal state
  const [pipelineModalOpen, setPipelineModalOpen] = useState<boolean>(false);
  const [pipelineClaimId, setPipelineClaimId] = useState<string>('');
  const [pipelineStep, setPipelineStep] = useState<string>('INITIALIZED');
  const [pipelineProgress, setPipelineProgress] = useState<number>(0);
  const [pipelineMessage, setPipelineMessage] = useState<string>('Starting multi-agent triage...');

  const handleSelectClaim = (claimId: string) => {
    setSelectedClaimId(claimId);
    setCurrentTab('detail');
  };

  const handleRunTriage = async (claimId: string) => {
    setPipelineClaimId(claimId);
    setPipelineStep('INTAKE');
    setPipelineProgress(10);
    setPipelineMessage('Initializing multi-agent pipeline...');
    setPipelineModalOpen(true);

    // Connect to WebSocket for live real-time milestone streaming
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/api/v1/ws/triage/${claimId}`;
    let socket: WebSocket | null = null;
    try {
      socket = new WebSocket(wsUrl);
      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.step) {
            setPipelineStep(data.step);
            setPipelineProgress(data.progress);
            setPipelineMessage(data.message);
          }
        } catch (e) {
          // ignore
        }
      };
    } catch (e) {
      console.warn("WebSocket fallback to polling:", e);
    }

    try {
      await apiClient.post(`/claims/${claimId}/analyze`);
      setPipelineStep('COMPLETED');
      setPipelineProgress(100);
      setPipelineMessage('Claim triage completed successfully.');
    } catch (err: any) {
      setPipelineMessage(`Error running triage: ${err.message}`);
    } finally {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.close();
      }
    }
  };

  const handleClosePipelineModal = () => {
    setPipelineModalOpen(false);
    if (pipelineClaimId) {
      handleSelectClaim(pipelineClaimId);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-blue-600 selection:text-white">
      {/* Top Header */}
      <Navbar
        currentTab={currentTab}
        setCurrentTab={(tab) => {
          setCurrentTab(tab);
          if (tab !== 'detail') setSelectedClaimId(null);
        }}
        userRole={userRole}
        setUserRole={setUserRole}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {currentTab === 'dashboard' && (
          <DashboardPage 
            onSelectClaim={handleSelectClaim} 
            onNavigateTab={setCurrentTab} 
          />
        )}

        {currentTab === 'claims' && (
          <ClaimsListPage
            onSelectClaim={handleSelectClaim}
            onNewClaim={() => setCurrentTab('portal')}
            onAnalyzeClaim={handleRunTriage}
          />
        )}

        {currentTab === 'detail' && selectedClaimId && (
          <ClaimDetailPage
            claimId={selectedClaimId}
            onBack={() => {
              setSelectedClaimId(null);
              setCurrentTab('claims');
            }}
            onAnalyzeClaim={handleRunTriage}
          />
        )}

        {currentTab === 'portal' && (
          <CustomerPortalPage
            onClaimSubmitted={(id) => {
              setPipelineClaimId(id);
              handleRunTriage(id);
            }}
          />
        )}

        {currentTab === 'fraud' && <FraudNetworkPage />}
        {currentTab === 'analytics' && <AnalyticsPage />}
        {currentTab === 'copilot' && <CopilotPage />}
        {currentTab === 'knowledge' && <KnowledgePage />}
        {currentTab === 'settings' && <AdminSettingsPage />}
        {currentTab === 'audit' && <AuditLogPage />}
      </main>

      {/* Live Pipeline Execution Modal */}
      <LivePipelineModal
        isOpen={pipelineModalOpen}
        onClose={handleClosePipelineModal}
        currentStep={pipelineStep}
        progress={pipelineProgress}
        message={pipelineMessage}
        claimId={pipelineClaimId}
      />

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-4 text-center text-xs text-slate-500">
        InsurAI Triage Platform &bull; Autonomous Multi-Agent Decision Support System &bull; Production Ready
      </footer>
    </div>
  );
};

export default App;
