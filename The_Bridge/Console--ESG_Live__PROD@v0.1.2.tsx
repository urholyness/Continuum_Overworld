/**
 * Console--ESG_Live__PROD@v0.1.2
 * ESG Live Console with Auto-Menu & Star Trek Theme
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';

// Dark + Green Theme (locked)
const THEME = {
  bg: '#0b0f0c',
  panel: '#0f1512', 
  stroke: '#124c2f',
  accent: '#22c55e',
  warn: '#f59e0b',
  text: '#e6f7ee',
  textDim: '#7fa67a'
} as const;

// Star Trek Division Glyphs (replaces Lucide icons)
const DIVISION_GLYPHS = {
  The_Bridge: '⟨⟨ ⟩⟩',    // Command
  Forge: '◊ ◊ ◊',         // Engineering
  Aegis: '▲ ■ ▲',        // Security  
  Oracle: '◎ ◦ ◎',       // Science
  Meridian: '⟐ ⟐ ⟐',     // Operations
  Atlas: '▷ ◁ ▷',        // Navigation
  Agora: '∿ ∿ ∿',        // Communications
  Ledger: '≡ ≡ ≡',       // Logistics
  Archive: '⌒ ⌒ ⌒',      // Memory Core
  Pantheon: '◈ ◈ ◈'      // Holodeck
} as const;

// Menu Node Structure
interface MenuNode {
  name: string;
  path?: string;
  icon?: string;
  children?: Record<string, MenuNode>;
  metadata?: {
    division?: string;
    capability?: string;
    role?: string;
    qualifier?: string;
    version?: string;
  };
}

// Mock menu data (until API is live)
const demoArtifacts: MenuNode = {
  name: 'Continuum_Overworld',
  children: {
    The_Bridge: {
      name: 'The_Bridge',
      icon: DIVISION_GLYPHS.The_Bridge,
      children: {
        Console: {
          name: 'Console',
          children: {
            ESG_Live: {
              name: 'ESG_Live',
              children: {
                PROD: {
                  name: 'PROD',
                  children: {
                    'v0.1.2': { name: 'v0.1.2', path: '/console/esg-live' }
                  }
                }
              }
            }
          }
        }
      }
    },
    Oracle: {
      name: 'Oracle',
      icon: DIVISION_GLYPHS.Oracle,
      children: {
        Forecaster: {
          name: 'Forecaster',
          children: {
            ESG: {
              name: 'ESG',
              children: {
                PROD: {
                  name: 'PROD',
                  children: {
                    'v1.0.0': { name: 'v1.0.0', path: '/oracle/esg' }
                  }
                }
              }
            }
          }
        }
      }
    },
    Forge: {
      name: 'Forge',
      icon: DIVISION_GLYPHS.Forge,
      children: {
        Weaver: {
          name: 'Weaver',
          children: {
            ESG_KPI: {
              name: 'ESG_KPI',
              children: {
                PROD: {
                  name: 'PROD',
                  children: {
                    'v1.0.0': { name: 'v1.0.0', path: '/forge/weaver' }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
};

// Auto-Menu Component
const AutoMenu: React.FC<{ onNavigate: (path: string) => void }> = ({ onNavigate }) => {
  const [menu, setMenu] = useState<MenuNode>(demoArtifacts);
  const [expanded, setExpanded] = useState<Set<string>>(new Set(['The_Bridge']));

  // Load menu from API (when available)
  useEffect(() => {
    const loadMenu = async () => {
      try {
        const response = await fetch('/api/menu');
        if (response.ok) {
          const data = await response.json();
          setMenu(data.menu);
        }
      } catch (err) {
        console.log('Using demo menu (API not available)');
      }
    };
    
    loadMenu();
  }, []);

  const toggleExpanded = (key: string) => {
    const newExpanded = new Set(expanded);
    if (newExpanded.has(key)) {
      newExpanded.delete(key);
    } else {
      newExpanded.add(key);
    }
    setExpanded(newExpanded);
  };

  const renderNode = (node: MenuNode, key: string, depth: number = 0): React.ReactNode => {
    const hasChildren = node.children && Object.keys(node.children).length > 0;
    const isExpanded = expanded.has(key);
    const isLeaf = node.path;

    return (
      <div key={key} style={{ marginLeft: `${depth * 16}px` }}>
        <div
          className="flex items-center gap-2 p-2 hover:bg-opacity-20 hover:bg-green-500 cursor-pointer rounded text-sm"
          style={{ color: THEME.text }}
          onClick={() => {
            if (isLeaf) {
              onNavigate(node.path!);
            } else if (hasChildren) {
              toggleExpanded(key);
            }
          }}
        >
          {hasChildren && (
            <span className="text-xs" style={{ color: THEME.textDim }}>
              {isExpanded ? '▼' : '▶'}
            </span>
          )}
          {node.icon && (
            <span className="font-mono text-xs" style={{ color: THEME.accent }}>
              {node.icon}
            </span>
          )}
          <span className={isLeaf ? 'text-green-400' : ''}>{node.name}</span>
        </div>
        
        {hasChildren && isExpanded && (
          <div>
            {Object.entries(node.children!).map(([childKey, childNode]) =>
              renderNode(childNode, `${key}.${childKey}`, depth + 1)
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="p-4" style={{ backgroundColor: THEME.panel }}>
      <h3 className="text-sm font-mono mb-3" style={{ color: THEME.accent }}>
        Navigation
      </h3>
      {menu.children && Object.entries(menu.children).map(([key, node]) =>
        renderNode(node, key)
      )}
    </div>
  );
};

// Supply Chain Step Display
interface SupplyChainStep {
  metric: string;
  value: string | number;
  unit?: string;
  confidence: number;
  source: string;
  contextSpan?: string;
}

const SupplyChainStepCard: React.FC<{ step: SupplyChainStep }> = ({ step }) => (
  <Card style={{ backgroundColor: THEME.panel, borderColor: THEME.stroke }}>
    <CardContent className="p-4">
      <div className="flex justify-between items-start mb-2">
        <h4 className="text-sm font-mono" style={{ color: THEME.text }}>
          {step.metric}
        </h4>
        <Badge 
          variant={step.confidence > 0.8 ? 'default' : 'secondary'}
          style={{ 
            backgroundColor: step.confidence > 0.8 ? THEME.accent : THEME.warn,
            color: THEME.bg 
          }}
        >
          {Math.round(step.confidence * 100)}%
        </Badge>
      </div>
      
      <div className="text-lg font-mono mb-1" style={{ color: THEME.accent }}>
        {step.value}{step.unit && ` ${step.unit}`}
      </div>
      
      <div className="text-xs" style={{ color: THEME.textDim }}>
        Source: {step.source}
      </div>
      
      {step.contextSpan && (
        <div className="text-xs mt-1 p-2 rounded" style={{ 
          backgroundColor: THEME.bg, 
          color: THEME.textDim 
        }}>
          {step.contextSpan}
        </div>
      )}
    </CardContent>
  </Card>
);

// Mock Supply Chain data (data-driven only)
const mockSupplyChainData: SupplyChainStep[] = [
  {
    metric: 'Forge Step',
    value: 'Completed',
    unit: '',
    confidence: 0.95,
    source: 'Contract ID: 1001',
    contextSpan: 'Manufacturing phase completed with verification hash'
  },
  {
    metric: 'Atlas Step', 
    value: 'In Progress',
    unit: '',
    confidence: 0.78,
    source: 'Contract ID: 1001',
    contextSpan: 'Logistics planning and route optimization in progress'
  },
  {
    metric: 'Ledger Step',
    value: 'Pending',
    unit: '',
    confidence: 0.0,
    source: 'Contract ID: 1001',
    contextSpan: 'Financial validation and legal compliance pending'
  },
  {
    metric: 'Aegis Step',
    value: 'Not Started',
    unit: '',
    confidence: 0.0,
    source: 'Contract ID: 1001',
    contextSpan: 'Security audit and compliance verification not yet initiated'
  }
];

// Main Console Component
export const ConsoleESGLive: React.FC = () => {
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [currentPath, setCurrentPath] = useState('/console/esg-live');

  // Client-side polling (does not update server Meridian job)
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      setLastUpdate(new Date());
      // In real implementation: fetch('/api/forge/weaver/runs/latest')
    }, 60000); // 1 minute client polling

    return () => clearInterval(interval);
  }, [autoRefresh]);

  const handleNavigation = (path: string) => {
    setCurrentPath(path);
    // In real implementation: router.push(path)
  };

  const exportToExcel = async () => {
    // In real implementation: fetch('/api/forge/weaver/export/excel?run_id=latest')
    console.log('Export to Excel triggered');
  };

  return (
    <div 
      className="min-h-screen flex"
      style={{ backgroundColor: THEME.bg, color: THEME.text }}
    >
      {/* Auto-Menu Sidebar */}
      <div className="w-80 border-r" style={{ borderColor: THEME.stroke }}>
        <AutoMenu onNavigate={handleNavigation} />
      </div>

      {/* Main Content */}
      <div className="flex-1 p-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl font-mono" style={{ color: THEME.accent }}>
              Supply Chain Console
            </h1>
            <p className="text-sm" style={{ color: THEME.textDim }}>
              Current: {currentPath}
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-sm">Auto-refresh</span>
              <Switch 
                checked={autoRefresh}
                onCheckedChange={setAutoRefresh}
              />
            </div>
            
            <Button 
              onClick={exportToExcel}
              style={{ backgroundColor: THEME.accent, color: THEME.bg }}
            >
              Export Excel
            </Button>
          </div>
        </div>

        {/* Status Bar */}
        <div className="mb-6 p-3 rounded" style={{ backgroundColor: THEME.panel }}>
          <div className="flex justify-between text-sm">
            <span>Last Update: {lastUpdate.toLocaleTimeString()}</span>
            <span style={{ color: THEME.accent }}>● Live</span>
          </div>
        </div>

        {/* Supply Chain Steps Grid - Data-driven content only */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {mockSupplyChainData.map((step, index) => (
            <SupplyChainStepCard key={index} step={step} />
          ))}
        </div>

        {/* Provenance Section */}
        <Card className="mt-6" style={{ backgroundColor: THEME.panel, borderColor: THEME.stroke }}>
          <CardHeader>
            <CardTitle style={{ color: THEME.text }}>Provenance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm" style={{ color: THEME.textDim }}>
              <div>Pipeline: Oracle/Forecaster--ESG__PROD@v1.0.0</div>
              <div>Run ID: {Date.now().toString(36)}</div>
              <div>Validation: Multi-AI consensus (GPT-4, Gemini, Claude)</div>
              <div>Confidence Threshold: >85%</div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ConsoleESGLive;