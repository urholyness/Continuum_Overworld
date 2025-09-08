import React, { useState, useEffect } from 'react';
import { Activity, Mail, AlertCircle, CheckCircle, Clock, Users, TrendingUp, RefreshCw } from 'lucide-react';

const AgentDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [showLogs, setShowLogs] = useState(false);

  // Simulate API calls (replace with actual API endpoints)
  const fetchDashboardData = async () => {
    // Simulated data - replace with actual API call
    const mockData = {
      timestamp: new Date().toISOString(),
      agents: [
        {
          agent_id: "email_manager_001",
          name: "Email Management Agent",
          status: "idle",
          last_action: {
            action_type: "inbox_processed",
            timestamp: new Date(Date.now() - 300000).toISOString(),
            status: "success"
          },
          total_actions: 42
        },
        {
          agent_id: "sales_agent_001",
          name: "Sales Outreach Agent",
          status: "working",
          last_action: {
            action_type: "lead_contacted",
            timestamp: new Date(Date.now() - 60000).toISOString(),
            status: "success"
          },
          total_actions: 28
        },
        {
          agent_id: "research_agent_001",
          name: "Market Research Agent",
          status: "idle",
          last_action: null,
          total_actions: 15
        }
      ],
      recent_actions: [
        {
          agent_id: "email_manager_001",
          action_type: "email_classified",
          action_data: { category: "inquiry", confidence: 0.92 },
          timestamp: new Date(Date.now() - 120000).toISOString(),
          status: "success",
          requires_approval: false
        },
        {
          agent_id: "email_manager_001",
          action_type: "response_generated",
          action_data: { email_id: "email_003", requires_approval: true },
          timestamp: new Date(Date.now() - 180000).toISOString(),
          status: "awaiting_approval",
          requires_approval: true
        }
      ],
      pending_approvals: [
        {
          agent_id: "email_manager_001",
          agent_name: "Email Management Agent",
          action_index: 1,
          action: {
            action_type: "response_generated",
            action_data: {
              email_id: "email_003",
              suggested_response: "Thank you for your partnership inquiry..."
            },
            timestamp: new Date(Date.now() - 180000).toISOString()
          }
        }
      ],
      system_metrics: {
        total_agents: 3,
        active_agents: 1,
        total_actions: 85,
        pending_approvals: 1
      }
    };
    
    setDashboardData(mockData);
    setLoading(false);
  };

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 5000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'working': return 'text-green-600 bg-green-100';
      case 'idle': return 'text-gray-600 bg-gray-100';
      case 'error': return 'text-red-600 bg-red-100';
      case 'awaiting_approval': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'working': return <Activity className="w-4 h-4" />;
      case 'idle': return <Clock className="w-4 h-4" />;
      case 'error': return <AlertCircle className="w-4 h-4" />;
      case 'awaiting_approval': return <AlertCircle className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString();
  };

  const handleApproval = (approvalItem) => {
    // Simulate API call to approve action
    console.log('Approving action:', approvalItem);
    alert('Action approved successfully!');
    fetchDashboardData();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-green-600" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">Farm 5.0 Agent Dashboard</h1>
              <span className="ml-4 text-sm text-gray-500">
                Last updated: {formatTimestamp(dashboardData.timestamp)}
              </span>
            </div>
            <button
              onClick={fetchDashboardData}
              className="flex items-center px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </button>
          </div>
        </div>
      </header>

      {/* Metrics Cards */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Agents</p>
                <p className="text-2xl font-bold text-gray-900">{dashboardData.system_metrics.total_agents}</p>
              </div>
              <Users className="w-8 h-8 text-green-600" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Now</p>
                <p className="text-2xl font-bold text-gray-900">{dashboardData.system_metrics.active_agents}</p>
              </div>
              <Activity className="w-8 h-8 text-green-600" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Actions</p>
                <p className="text-2xl font-bold text-gray-900">{dashboardData.system_metrics.total_actions}</p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-600" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Pending Approvals</p>
                <p className="text-2xl font-bold text-gray-900">{dashboardData.system_metrics.pending_approvals}</p>
              </div>
              <AlertCircle className="w-8 h-8 text-yellow-600" />
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Agents List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow">
              <div className="p-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Active Agents</h2>
              </div>
              <div className="p-4">
                <div className="space-y-3">
                  {dashboardData.agents.map((agent) => (
                    <div
                      key={agent.agent_id}
                      className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                      onClick={() => setSelectedAgent(agent)}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-medium text-gray-900">{agent.name}</h3>
                        <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(agent.status)}`}>
                          {getStatusIcon(agent.status)}
                          <span className="ml-1">{agent.status}</span>
                        </span>
                      </div>
                      <p className="text-sm text-gray-600">
                        Actions: {agent.total_actions}
                      </p>
                      {agent.last_action && (
                        <p className="text-xs text-gray-500 mt-1">
                          Last: {agent.last_action.action_type} ({formatTimestamp(agent.last_action.timestamp)})
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Recent Actions & Pending Approvals */}
          <div className="lg:col-span-2 space-y-6">
            {/* Pending Approvals */}
            {dashboardData.pending_approvals.length > 0 && (
              <div className="bg-white rounded-lg shadow">
                <div className="p-4 border-b border-gray-200">
                  <h2 className="text-lg font-semibold text-gray-900">Pending Approvals</h2>
                </div>
                <div className="p-4">
                  <div className="space-y-3">
                    {dashboardData.pending_approvals.map((approval, index) => (
                      <div key={index} className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h4 className="font-medium text-gray-900">{approval.agent_name}</h4>
                            <p className="text-sm text-gray-600 mt-1">
                              Action: {approval.action.action_type}
                            </p>
                            {approval.action.action_data.suggested_response && (
                              <p className="text-sm text-gray-500 mt-2 italic">
                                "{approval.action.action_data.suggested_response.substring(0, 100)}..."
                              </p>
                            )}
                            <p className="text-xs text-gray-500 mt-2">
                              {formatTimestamp(approval.action.timestamp)}
                            </p>
                          </div>
                          <button
                            onClick={() => handleApproval(approval)}
                            className="ml-4 px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
                          >
                            Approve
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Recent Actions */}
            <div className="bg-white rounded-lg shadow">
              <div className="p-4 border-b border-gray-200 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">Recent Actions</h2>
                <button
                  onClick={() => setShowLogs(!showLogs)}
                  className="text-sm text-green-600 hover:text-green-700"
                >
                  {showLogs ? 'Hide' : 'Show'} All
                </button>
              </div>
              <div className="p-4">
                <div className="space-y-2">
                  {dashboardData.recent_actions.slice(0, showLogs ? undefined : 5).map((action, index) => (
                    <div key={index} className="flex items-start space-x-3 py-2 border-b border-gray-100 last:border-0">
                      <div className={`mt-1 ${action.status === 'success' ? 'text-green-600' : 'text-yellow-600'}`}>
                        {action.status === 'success' ? <CheckCircle className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">
                          {action.action_type.replace(/_/g, ' ').charAt(0).toUpperCase() + action.action_type.replace(/_/g, ' ').slice(1)}
                        </p>
                        <p className="text-xs text-gray-500">
                          {dashboardData.agents.find(a => a.agent_id === action.agent_id)?.name || action.agent_id} • {formatTimestamp(action.timestamp)}
                        </p>
                        {action.action_data.category && (
                          <p className="text-xs text-gray-600 mt-1">
                            Category: {action.action_data.category} (Confidence: {(action.action_data.confidence * 100).toFixed(0)}%)
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Agent Detail Modal */}
        {selectedAgent && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" onClick={() => setSelectedAgent(null)}>
            <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white" onClick={(e) => e.stopPropagation()}>
              <div className="mt-3">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">{selectedAgent.name}</h3>
                <div className="mt-2 px-4 py-3 bg-gray-50 rounded">
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">ID:</span> {selectedAgent.agent_id}
                  </p>
                  <p className="text-sm text-gray-600 mt-2">
                    <span className="font-medium">Status:</span>
                    <span className={`ml-2 inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(selectedAgent.status)}`}>
                      {getStatusIcon(selectedAgent.status)}
                      <span className="ml-1">{selectedAgent.status}</span>
                    </span>
                  </p>
                  <p className="text-sm text-gray-600 mt-2">
                    <span className="font-medium">Total Actions:</span> {selectedAgent.total_actions}
                  </p>
                  {selectedAgent.last_action && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <p className="text-sm font-medium text-gray-900">Last Action</p>
                      <p className="text-sm text-gray-600 mt-1">
                        Type: {selectedAgent.last_action.action_type}
                      </p>
                      <p className="text-sm text-gray-600">
                        Status: {selectedAgent.last_action.status}
                      </p>
                      <p className="text-sm text-gray-600">
                        Time: {formatTimestamp(selectedAgent.last_action.timestamp)}
                      </p>
                    </div>
                  )}
                </div>
                <div className="mt-5 sm:mt-6 space-y-2">
                  <button
                    onClick={() => {
                      console.log('View logs for:', selectedAgent.agent_id);
                      setSelectedAgent(null);
                    }}
                    className="w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 sm:text-sm"
                  >
                    View Full Logs
                  </button>
                  <button
                    onClick={() => setSelectedAgent(null)}
                    className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-green-600 text-base font-medium text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 sm:text-sm"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AgentDashboard;
                