/**
 * ResearchView — Technical Analysis Research Terminal
 * ====================================================
 * 
 * Uses Setup API to display:
 * 1. Full-width chart with patterns, levels, bias
 * 2. Pattern Activation Layer
 * 3. Deep Analysis Blocks
 * 4. Save Idea functionality
 */

import React, { useState, useEffect, useCallback } from 'react';
import styled from 'styled-components';
import { 
  Search, 
  RefreshCw, 
  Share2, 
  Camera, 
  Bookmark,
  Loader2,
  AlertTriangle,
  ChevronDown,
  BarChart2,
  LineChart,
  Eye,
  EyeOff,
  Settings2,
  Triangle,
  Layers,
  TrendingUp,
  Target
} from 'lucide-react';

// ═══════════════════════════════════════════════════════════════
// TA VISUALIZATION — RenderPlan + Renderers (moved from Chart Lab)
// ═══════════════════════════════════════════════════════════════
import { useRenderPlan } from '../../../store/marketStore';
import { RenderPlanOverlay } from '../renderers';

import ResearchChart from '../components/ResearchChart';
import PatternActivationLayer from '../components/PatternActivationLayer';
import DeepAnalysisBlocks from '../components/DeepAnalysisBlocks';
import MarketContextBar from '../components/MarketContextBar';
import ScenariosBlock from '../components/ScenariosBlock';
import PatternsBlock from '../components/PatternsBlock';
import ConfidenceExplanation from '../components/ConfidenceExplanation';
import ExplanationPanel from '../components/ExplanationPanel';
import IndicatorPanes from '../components/IndicatorPanes';
import ConfluenceMatrix from '../components/ConfluenceMatrix';
import IndicatorSelector from '../components/IndicatorSelector';
import ViewModeSelector from '../components/ViewModeSelector';
import TAContextPanel from '../components/TAContextPanel';
import RenderPlanReasons from '../components/RenderPlanReasons';
import TACompositionPanel from '../components/TACompositionPanel';
import UnifiedSetupPanel from '../components/UnifiedSetupPanel';
import MTFHeaderPanel from '../components/MTFHeaderPanel';
import ExecutionPanel from '../components/ExecutionPanel';
import { 
  computeVisibility, 
  getLayerLimits, 
  applyLimits, 
  getLayerStyle,
  LAYER_PRIORITY,
  VISUAL_PRIORITY 
} from '../engine/GraphVisibilityEngine';
import setupService from '../../../services/setupService';
import { buildNarrative, NarrativeSummary } from '../../../components/chart-engine/narrative';

// ════════════════════════════════════════════════════════════════
// CONFLUENCE ENGINE — TA Decision Logic (NEW!)
// ════════════════════════════════════════════════════════════════
import { buildConfluence, getLayerVisibility } from '../utils/confluenceEngine';
import { buildTradeSetup } from '../utils/setupGenerator';

// ============================================
// STYLED COMPONENTS
// ============================================

const Container = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f8fafc;
  overflow-y: auto;
`;

const TopBar = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: #ffffff;
  border-bottom: 1px solid #eef1f5;
  flex-wrap: wrap;
  gap: 12px;
`;

const ControlsLeft = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const ControlsRight = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const SearchWrapper = styled.div`
  position: relative;
`;

const SearchInput = styled.input`
  width: 160px;
  padding: 10px 14px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
  letter-spacing: 0.5px;
  
  &:focus {
    outline: none;
    border-color: #05A584;
    background: #ffffff;
  }
  
  &::placeholder {
    color: #94a3b8;
    font-weight: 500;
  }
`;

const SymbolDropdown = styled.div`
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 4px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  z-index: 100;
  max-height: 200px;
  overflow-y: auto;
`;

const SymbolOption = styled.button`
  width: 100%;
  padding: 10px 12px;
  text-align: left;
  border: none;
  background: ${({ $active }) => $active ? '#f0f9ff' : 'transparent'};
  font-size: 13px;
  font-weight: 500;
  color: #0f172a;
  cursor: pointer;
  
  &:hover {
    background: #f8fafc;
  }
`;

const TfGroup = styled.div`
  display: flex;
  gap: 2px;
  background: #f1f5f9;
  padding: 3px;
  border-radius: 8px;
`;

const TfButton = styled.button`
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  border: none;
  background: ${({ $active }) => $active ? '#ffffff' : 'transparent'};
  color: ${({ $active }) => $active ? '#0f172a' : '#64748b'};
  cursor: pointer;
  box-shadow: ${({ $active }) => $active ? '0 1px 3px rgba(0,0,0,0.08)' : 'none'};
  transition: all 0.15s ease;
  
  &:hover {
    color: #0f172a;
  }
`;

const ChartTypeGroup = styled.div`
  display: flex;
  gap: 2px;
  background: #f1f5f9;
  padding: 3px;
  border-radius: 8px;
`;

const ChartTypeBtn = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px 10px;
  border-radius: 6px;
  border: none;
  background: ${({ $active }) => $active ? '#ffffff' : 'transparent'};
  color: ${({ $active }) => $active ? '#0f172a' : '#64748b'};
  cursor: pointer;
  box-shadow: ${({ $active }) => $active ? '0 1px 3px rgba(0,0,0,0.08)' : 'none'};
  
  svg {
    width: 16px;
    height: 16px;
  }
  
  &:hover {
    color: #0f172a;
  }
`;

const ViewModeWrapper = styled.div`
  position: relative;
`;

const ViewModeButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 12px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  color: #0f172a;
  cursor: pointer;
  
  &:hover {
    border-color: #cbd5e1;
  }
  
  svg {
    width: 14px;
    height: 14px;
    color: #94a3b8;
  }
`;

const ViewModeDropdown = styled.div`
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 4px;
  min-width: 140px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 50;
  overflow: hidden;
`;

const ViewModeOption = styled.button`
  display: block;
  width: 100%;
  padding: 10px 14px;
  background: ${({ $active }) => $active ? '#f8fafc' : '#ffffff'};
  border: none;
  text-align: left;
  font-size: 13px;
  font-weight: ${({ $active }) => $active ? '600' : '500'};
  color: #0f172a;
  cursor: pointer;
  
  &:hover {
    background: #f1f5f9;
  }
`;

const ActionBtn = styled.button`
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 12px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #ffffff;
  color: #64748b;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  
  svg {
    width: 14px;
    height: 14px;
  }
  
  &:hover {
    border-color: #3b82f6;
    color: #3b82f6;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  &.primary {
    background: #3b82f6;
    border-color: #3b82f6;
    color: #ffffff;
    
    &:hover {
      background: #2563eb;
    }
  }
  
  &.loading svg {
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
`;

// LayerToggles and LayerToggleBtn removed - using ViewModeSelector instead

const MainContent = styled.div`
  flex: 1;
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const ChartSection = styled.div`
  background: #ffffff;
  border: 1px solid #eef1f5;
  border-radius: 12px;
  overflow: hidden;
`;

const ErrorBanner = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  font-size: 13px;
  
  svg {
    flex-shrink: 0;
  }
`;

const LoadingOverlay = styled.div`
  position: absolute;
  inset: 0;
  background: rgba(255,255,255,0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  z-index: 10;
  
  svg {
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
`;

const SuccessToast = styled.div`
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 12px 20px;
  background: #05A584;
  color: #ffffff;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(5, 165, 132, 0.3);
  z-index: 1000;
  animation: slideIn 0.3s ease;
  
  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;

const DebugPanel = styled.div`
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  padding: 16px 20px;
  margin: 16px 0;
  font-family: 'Gilroy', 'Inter', -apple-system, sans-serif;
  
  .debug-title {
    font-weight: 700;
    font-size: 11px;
    color: #64748b;
    margin-bottom: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
  }
  
  .debug-row {
    display: flex;
    gap: 32px;
    padding: 8px 0;
    border-bottom: 1px solid #f1f5f9;
    
    &:last-child {
      border-bottom: none;
    }
  }
  
  .debug-label {
    min-width: 100px;
    font-size: 12px;
    font-weight: 500;
    color: #94a3b8;
  }
  
  .debug-value {
    font-size: 13px;
    font-weight: 600;
    color: #0f172a;
    
    &.bullish { color: #05A584; }
    &.bearish { color: #ef4444; }
    &.neutral { color: #64748b; }
  }
`;

// New Decision Layer UI Components
const BottomGrid = styled.div`
  display: flex;
  gap: 12px;
  margin-top: 12px;
  
  & > * {
    flex: 1;
    min-width: 0;
  }
  
  @media (max-width: 900px) {
    flex-direction: column;
  }
`;

const SubChartControls = styled.div`
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 6px;
  padding: 8px 16px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  margin: 0 0 8px 0;
  
  /* Overlay toggle section */
  .overlay-section {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 4px 8px;
    background: #f8fafc;
    border-radius: 6px;
  }
  
  .section-label {
    font-size: 10px;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    margin-right: 4px;
  }
`;

const ControlDivider = styled.div`
  width: 1px;
  height: 24px;
  background: #e2e8f0;
  margin: 0 8px;
`;

const CollapsibleButton = styled.button`
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 12px;
  background: ${({ $active }) => $active ? '#0f172a' : '#f8fafc'};
  border: 1px solid ${({ $active }) => $active ? '#0f172a' : '#e2e8f0'};
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  color: ${({ $active }) => $active ? '#ffffff' : '#64748b'};
  cursor: pointer;
  transition: all 0.15s ease;
  
  &:hover {
    border-color: ${({ $active }) => $active ? '#1e293b' : '#cbd5e1'};
    background: ${({ $active }) => $active ? '#1e293b' : '#f1f5f9'};
  }
  
  svg {
    width: 13px;
    height: 13px;
    opacity: ${({ $active }) => $active ? 1 : 0.6};
  }
  
  /* Status indicator dot */
  &::after {
    content: '';
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: ${({ $active }) => $active ? '#22c55e' : 'transparent'};
    margin-left: 4px;
  }
`;

const BottomSection = styled.div`
  margin-top: 12px;
`;

// ============================================
// CONSTANTS
// ============================================

const SYMBOLS = [
  'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT',
  'ADAUSDT', 'DOGEUSDT', 'AVAXUSDT', 'DOTUSDT', 'MATICUSDT',
  'LINKUSDT', 'UNIUSDT', 'ATOMUSDT', 'LTCUSDT', 'ETCUSDT',
  'FILUSDT', 'APTUSDT', 'ARBUSDT', 'OPUSDT', 'NEARUSDT',
  'INJUSDT', 'SUIUSDT', 'AAVEUSDT', 'MKRUSDT', 'CRVUSDT',
  'TONUSDT', 'SEIUSDT', 'TIAUSDT', 'JUPUSDT', 'WIFUSDT'
];
const TIMEFRAMES = ['4H', '1D', '7D', '30D', '180D', '1Y'];
const MTF_TIMEFRAMES = ['1D', '4H', '1H']; // Available MTF timeframes

// ============================================
// COMPONENT
// ============================================

const ResearchView = () => {
  // ═══════════════════════════════════════════════════════════════
  // RESEARCH STATE — TA-specific (isolated from Chart Lab)
  // ═══════════════════════════════════════════════════════════════
  const [symbol, setSymbol] = useState('BTCUSDT');
  const [timeframe, setTimeframe] = useState('1D');
  const [selectedTF, setSelectedTF] = useState('4H');
  const [chartType, setChartType] = useState('candles');
  const [viewMode, setViewMode] = useState('auto');
  const [showViewModeDropdown, setShowViewModeDropdown] = useState(false);
  
  const [searchQuery, setSearchQuery] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [toast, setToast] = useState(null);
  
  // ═══════════════════════════════════════════════════════════════
  // TA OVERLAY STATE — moved from Chart Lab (RESEARCH EXCLUSIVE)
  // ═══════════════════════════════════════════════════════════════
  const [showTAOverlay, setShowTAOverlay] = useState(false);  // OFF by default - reduces noise
  
  // Hook into global render plan store for TA visualization
  const { renderPlan: globalRenderPlan, loading: renderPlanLoading, refresh: refreshRenderPlan } = useRenderPlan();
  
  // Collapsible panels state — toggles overlay visibility on chart
  // ALL OFF by default to reduce visual noise - user clicks to enable
  const [showFibonacciOverlay, setShowFibonacciOverlay] = useState(false);
  const [showPatternOverlay, setShowPatternOverlay] = useState(false);
  const [showSetupOverlay, setShowSetupOverlay] = useState(false);
  
  // Data - NEW: MTF data structure
  const [tfMap, setTfMap] = useState({});
  const [mtfContext, setMtfContext] = useState(null);
  const [setupData, setSetupData] = useState(null);
  const [candles, setCandles] = useState([]);
  
  // Active elements for pattern activation
  const [activeElements, setActiveElements] = useState({});
  
  // Active pattern for switching between primary/alternatives
  const [activePatternId, setActivePatternId] = useState('primary');
  
  // Layer visibility now controlled by viewMode through layerVisibilityComputed
  // Removed manual layerVisibility state to avoid duplication
  
  // Indicator selection state (max 2 overlays, max 2 panes)
  const [selectedOverlays, setSelectedOverlays] = useState(['ema_20', 'ema_50']);
  const [selectedPanes, setSelectedPanes] = useState(['rsi', 'macd']);

  // Fetch MTF data from per-timeframe pipeline
  // CRITICAL: Fetch ALL timeframes at once, not one by one
  const fetchSetup = useCallback(async () => {
    console.log('[MTF] Starting fetch for ALL timeframes...');
    setLoading(true);
    setError(null);
    
    try {
      // Extract base symbol (BTC from BTCUSDT)
      const baseSymbol = symbol.replace('USDT', '');
      
      // CRITICAL: Request ALL TIMEFRAMES at once (was MTF_TIMEFRAMES, now TIMEFRAMES)
      const allTFs = TIMEFRAMES.join(',');
      const url = `/api/ta-engine/mtf/${baseSymbol}?timeframes=${allTFs}`;
      console.log('[MTF] Fetching ALL TFs:', url);
      
      // Add timeout controller - increased to 35s for MTF endpoint
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 35000);
      
      // Fetch MTF data
      const response = await fetch(url, { signal: controller.signal });
      clearTimeout(timeoutId);
      
      console.log('[MTF] Response status:', response.status);
      
      if (!response.ok) {
        throw new Error('Failed to fetch MTF analysis');
      }
      
      const data = await response.json();
      const tfKeys = Object.keys(data.tf_map || {});
      console.log('[MTF] Data received, tf_map keys:', tfKeys);
      
      // Store ALL MTF data in cache
      setTfMap(data.tf_map || {});
      setMtfContext(data.mtf_context || null);
      
      // Set active TF data as setupData for compatibility
      const activeTFData = data.tf_map?.[selectedTF] || {};
      setSetupData(activeTFData);
      setCandles(activeTFData.candles || []);
      setActivePatternId('primary');
      
      // 🔥 CRITICAL LOG: Verify each TF has different render_plan
      tfKeys.forEach(tf => {
        const tfData = data.tf_map[tf];
        const rp = tfData?.render_plan;
        console.log(`[MTF] TF=${tf}: candles=${tfData?.candles?.length}, swings=${rp?.structure?.swings?.length}, levels=${rp?.levels?.length}`);
      });
      
    } catch (err) {
      if (err.name === 'AbortError') {
        console.error('[MTF] Fetch timeout');
        setError('Analysis timeout - please try again');
      } else {
        console.error('[MTF] Fetch error:', err);
        setError(err.message || 'Failed to load analysis');
      }
    } finally {
      setLoading(false);
      console.log('[MTF] Fetch complete');
    }
  }, [symbol, selectedTF]);

  // Update setupData when selectedTF changes — use cached data
  useEffect(() => {
    if (tfMap[selectedTF]) {
      // Data already cached — use it IMMEDIATELY
      const tfData = tfMap[selectedTF];
      setSetupData(tfData);
      setCandles(tfData.candles || []);
      
      // 🔥 CRITICAL LOG: Verify TF switch changes data
      const rp = tfData.render_plan;
      console.log('[MTF] ═══════════════════════════════════════');
      console.log('[MTF] TF SWITCHED TO:', selectedTF);
      console.log('[MTF] Candles:', tfData.candles?.length);
      console.log('[MTF] render_plan:', !!rp);
      if (rp) {
        console.log('[MTF] > Structure swings:', rp.structure?.swings?.length);
        console.log('[MTF] > Levels:', rp.levels?.length);
        console.log('[MTF] > Market state:', rp.market_state?.trend);
        console.log('[MTF] > Execution:', rp.execution?.status);
      }
      console.log('[MTF] ═══════════════════════════════════════');
    } else if (Object.keys(tfMap).length === 0) {
      // No data at all — need initial fetch
      console.log('[MTF] No cached data, will fetch on mount');
    } else {
      // Data for some TFs exists but not for selected one
      console.log('[MTF] TF not in cache:', selectedTF, 'available:', Object.keys(tfMap));
    }
  }, [selectedTF, tfMap]);

  // Initial load
  useEffect(() => {
    fetchSetup();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [symbol]); // Only re-fetch when symbol changes

  // Handle symbol change
  const handleSymbolSelect = (s) => {
    setSymbol(s);
    setSearchQuery('');
    setShowDropdown(false);
  };

  // Handle search - filter and show first 5
  const filteredSymbols = searchQuery
    ? SYMBOLS.filter(s => 
        s.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.replace('USDT', '').toLowerCase().includes(searchQuery.toLowerCase())
      ).slice(0, 5)
    : SYMBOLS.slice(0, 5);

  // Toggle element visibility
  const handleToggleElement = (elementKey) => {
    setActiveElements(prev => ({
      ...prev,
      [elementKey]: !prev[elementKey]
    }));
  };

  // Save idea
  const handleSaveIdea = async () => {
    try {
      setLoading(true);
      const result = await setupService.createIdea(symbol, timeframe);
      
      if (result.ok) {
        setToast(`Idea saved: ${result.idea.idea_id}`);
        setTimeout(() => setToast(null), 3000);
      }
    } catch (err) {
      setError('Failed to save idea');
    } finally {
      setLoading(false);
    }
  };

  // Share (placeholder)
  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: `${symbol} Technical Analysis`,
        text: `${setupData?.technical_bias?.toUpperCase()} bias with ${Math.round((setupData?.bias_confidence || 0) * 100)}% confidence`,
        url: window.location.href,
      });
    }
  };

  // Derived data - Map backend v2 format to component format
  // v2 returns: { primary_pattern, alternative_patterns, decision, scenarios, confidence_explanation, ... }
  
  // Get pattern based on activePatternId
  const primaryPattern = setupData?.primary_pattern;
  const alternativePatterns = setupData?.alternative_patterns || [];
  
  // Determine which pattern to display on chart
  const getActivePattern = () => {
    if (activePatternId === 'primary') return primaryPattern;
    const altIndex = parseInt(activePatternId.replace('alt-', ''));
    return alternativePatterns[altIndex] || primaryPattern;
  };
  
  const pattern = getActivePattern();
  
  // LEVELS — use from render_plan (max 5, ranked by strength)
  const levels = React.useMemo(() => {
    const rpLevels = setupData?.render_plan?.levels;
    if (rpLevels?.length) {
      // Convert to format ResearchChart expects
      return rpLevels.map(l => ({
        price: l.price,
        type: l.type, // support/resistance
        strength: l.strength,
        source: l.source,
      }));
    }
    return setupData?.levels || [];
  }, [setupData?.render_plan?.levels, setupData?.levels]);
  
  const structure = setupData?.structure;
  const setup = setupData?.setup;
  
  // New v2 data
  const decision = setupData?.decision;
  
  // BUILD scenarios from decision and structure
  const scenarios = React.useMemo(() => {
    if (!setupData) return [];
    
    const decisionData = setupData.decision;
    const structure = setupData.structure_context;
    const pattern = setupData.primary_pattern;
    const rp = setupData.render_plan;
    const currentPrice = setupData.current_price || rp?.market_state?.current_price;
    const levels = rp?.levels || [];
    
    const result = [];
    
    // Bullish scenario
    const resistances = levels.filter(l => l.type === 'resistance' && l.price > currentPrice);
    const nearestResistance = resistances.length > 0 ? resistances.reduce((a, b) => b.price < a.price ? b : a) : null;
    
    if (nearestResistance) {
      result.push({
        id: 'bullish',
        type: 'bullish',
        title: 'Bullish Breakout',
        description: `Break above ${nearestResistance.price?.toFixed(0)} triggers bullish continuation`,
        probability: decisionData?.bias === 'bullish' ? 0.6 : decisionData?.bias === 'neutral' ? 0.4 : 0.3,
        trigger_price: nearestResistance.price,
        target_price: nearestResistance.price * 1.03,
      });
    }
    
    // Bearish scenario
    const supports = levels.filter(l => l.type === 'support' && l.price < currentPrice);
    const nearestSupport = supports.length > 0 ? supports.reduce((a, b) => b.price > a.price ? b : a) : null;
    
    if (nearestSupport) {
      result.push({
        id: 'bearish',
        type: 'bearish',
        title: 'Bearish Breakdown',
        description: `Break below ${nearestSupport.price?.toFixed(0)} triggers bearish move`,
        probability: decisionData?.bias === 'bearish' ? 0.6 : decisionData?.bias === 'neutral' ? 0.4 : 0.3,
        trigger_price: nearestSupport.price,
        target_price: nearestSupport.price * 0.97,
      });
    }
    
    // Range scenario (if both levels exist)
    if (nearestResistance && nearestSupport) {
      result.push({
        id: 'range',
        type: 'neutral',
        title: 'Range Continuation',
        description: `Price consolidates between ${nearestSupport.price?.toFixed(0)} - ${nearestResistance.price?.toFixed(0)}`,
        probability: decisionData?.bias === 'neutral' ? 0.5 : 0.3,
        trigger_price: currentPrice,
        target_price: null,
      });
    }
    
    return result;
  }, [setupData]);
  
  // BUILD confidenceExplanation from decision - format for ConfidenceExplanation component
  const confidenceExplanation = React.useMemo(() => {
    if (!setupData?.decision) return {};
    
    const d = setupData.decision;
    const pattern = setupData.primary_pattern;
    
    // If we have pattern scores, use them
    if (pattern?.scores) {
      const scores = pattern.scores;
      return {
        geometry: scores.geometry || 0.5,
        structure: scores.structure || 0.5,
        level: scores.level || 0.5,
        recency: scores.recency || 0.5,
        cleanliness: scores.cleanliness || 0.5,
      };
    }
    
    // Otherwise build from decision data
    // Convert string bias to numeric score
    const biasToScore = (bias) => {
      if (bias === 'bullish' || bias === 'bearish') return 0.8;
      if (bias === 'lean_bullish' || bias === 'lean_bearish') return 0.6;
      return 0.5;
    };
    
    const strengthToScore = (strength) => {
      if (strength === 'high' || strength === 'strong') return 0.85;
      if (strength === 'medium' || strength === 'moderate') return 0.65;
      return 0.45;
    };
    
    return {
      structure: biasToScore(d.indicator_bias),
      level: strengthToScore(d.strength),
      geometry: d.confidence || 0.5,
      recency: d.alignment === 'aligned' ? 0.8 : d.alignment === 'mixed' ? 0.5 : 0.4,
      cleanliness: d.tradeability === 'high' ? 0.8 : d.tradeability === 'medium' ? 0.6 : 0.4,
    };
  }, [setupData]);
  
  // BUILD explanation from decision and pattern — format for ExplanationPanel
  const explanation = React.useMemo(() => {
    if (!setupData) return null;
    
    const d = setupData.decision;
    const pattern = setupData.primary_pattern;
    const levels = setupData.render_plan?.levels || [];
    const currentPrice = setupData.current_price;
    
    if (!d && !pattern) return null;
    
    // Build summary
    let summary = '';
    if (d?.summary) {
      summary = d.summary;
    } else if (pattern?.type) {
      summary = `${pattern.type.replace(/_/g, ' ')} pattern detected with ${pattern.direction || 'neutral'} bias.`;
    } else {
      summary = 'Market conditions being analyzed.';
    }
    
    // Build action
    let action = '';
    if (d?.bias === 'bullish' && d?.tradeability === 'high') {
      action = 'Look for long entries on pullbacks to support.';
    } else if (d?.bias === 'bearish' && d?.tradeability === 'high') {
      action = 'Look for short entries on rallies to resistance.';
    } else if (d?.tradeability === 'medium') {
      action = 'Wait for clearer setup before taking position.';
    } else {
      action = 'No clear action — observe and wait for better conditions.';
    }
    
    // Build risk
    let risk = '';
    const resistances = levels.filter(l => l.type === 'resistance' && l.price > currentPrice);
    const supports = levels.filter(l => l.type === 'support' && l.price < currentPrice);
    
    if (d?.bias === 'bullish' && supports.length > 0) {
      const nearestSupport = supports.reduce((a, b) => b.price > a.price ? b : a);
      risk = `Invalidation below ${nearestSupport.price?.toFixed(0)} support level.`;
    } else if (d?.bias === 'bearish' && resistances.length > 0) {
      const nearestResistance = resistances.reduce((a, b) => b.price < a.price ? b : a);
      risk = `Invalidation above ${nearestResistance.price?.toFixed(0)} resistance level.`;
    } else {
      risk = 'Define clear stop-loss before entering any position.';
    }
    
    // Confidence
    let confidence = 'medium';
    if (d?.confidence >= 0.7 || d?.tradeability === 'high') confidence = 'high';
    else if (d?.confidence <= 0.3 || d?.tradeability === 'low') confidence = 'low';
    
    return { summary, action, risk, confidence };
  }, [setupData]);
  
  // TRADE SETUP — Execution-ready entry/stop/targets
  const tradeSetup = setupData?.trade_setup || null;
  
  // BASE LAYER — always visible
  const baseLayer = setupData?.base_layer || null;
  
  // Structure context from V2 engine (rich data)
  const structureContext = setupData?.structure_context || null;
  
  // STRUCTURE VISUALIZATION — pivot points, BOS/CHOCH, trendlines
  const structureVisualization = setupData?.structure_visualization || null;
  
  // CHART STRUCTURE — build from render_plan.structure for chart rendering
  // Format: { labels: [{time, price, label, type}], breaks: [...], legs: [...] }
  const chartStructure = React.useMemo(() => {
    const rpStructure = setupData?.render_plan?.structure;
    if (!rpStructure?.swings?.length) return null;
    
    // Convert swings to labels format that ResearchChart expects
    const labels = rpStructure.swings.map(s => ({
      time: s.time,
      price: s.price,
      label: s.type, // HH/HL/LH/LL
      type: s.type?.includes('H') && s.type !== 'HL' ? 'high' : 'low',
    }));
    
    // Build breaks from BOS/CHOCH
    const breaks = [];
    if (rpStructure.bos) {
      breaks.push({
        time: rpStructure.bos.time,
        level: rpStructure.bos.price,
        type: 'bos',
        direction: rpStructure.bos.direction,
      });
    }
    if (rpStructure.choch) {
      breaks.push({
        time: rpStructure.choch.time,
        level: rpStructure.choch.price,
        type: 'choch',
        direction: rpStructure.choch.direction,
      });
    }
    
    return { labels, breaks, legs: [] };
  }, [setupData?.render_plan?.structure]);
  
  // TA CONTEXT — unified contributions from all TA sources
  // Transform backend format to TAContextPanel expected format
  const taContext = React.useMemo(() => {
    const rawContext = setupData?.ta_context;
    if (!rawContext) return null;
    
    const indicators = rawContext.indicators || {};
    const signals = indicators.signals || [];
    
    // Count bullish/bearish/neutral from signals
    let bullishCount = 0;
    let bearishCount = 0;
    let neutralCount = 0;
    let bullishScore = 0;
    let bearishScore = 0;
    
    const bullishSignals = [];
    const bearishSignals = [];
    const neutralSignals = [];
    
    signals.forEach(s => {
      const direction = s.direction?.toLowerCase();
      const strength = s.strength || 0;
      const item = {
        name: s.name,
        signal_type: s.signal_type,
        strength: strength,
        description: s.description,
        signal: direction,
        score: direction === 'bullish' ? strength : direction === 'bearish' ? -strength : 0,
        source: 'indicator',
        impact: strength / (signals.length || 1),
      };
      
      if (direction === 'bullish') {
        bullishCount++;
        bullishScore += strength;
        bullishSignals.push(item);
      } else if (direction === 'bearish') {
        bearishCount++;
        bearishScore += strength;
        bearishSignals.push(item);
      } else {
        neutralCount++;
        neutralSignals.push(item);
      }
    });
    
    // Calculate aggregated bias and score
    const totalScore = bullishScore - bearishScore;
    const maxPossibleScore = signals.length * 1; // max strength is 1
    const normalizedScore = maxPossibleScore > 0 ? totalScore / maxPossibleScore : 0;
    
    let aggregatedBias = 'neutral';
    if (normalizedScore > 0.1) aggregatedBias = 'bullish';
    else if (normalizedScore < -0.1) aggregatedBias = 'bearish';
    
    // Sort by strength for top_drivers
    const allContribs = [...bullishSignals, ...bearishSignals, ...neutralSignals]
      .sort((a, b) => Math.abs(b.strength) - Math.abs(a.strength));
    
    return {
      summary: {
        aggregated_bias: aggregatedBias,
        aggregated_score: normalizedScore,
        aggregated_confidence: Math.min(1, (bullishCount + bearishCount) / (signals.length || 1)),
        total_sources: signals.length,
        active_sources: bullishCount + bearishCount,
      },
      indicators: {
        bullish: bullishCount,
        bearish: bearishCount,
        neutral: neutralCount,
        total: signals.length,
      },
      top_drivers: allContribs.slice(0, 10),
      all_contributions: allContribs,
      hidden_but_used: [],
      rendered_default: [],
    };
  }, [setupData?.ta_context]);
  
  // RENDER PLAN — brain → chart mapping (from VisualMappingEngine)
  const renderPlan = setupData?.render_plan || null;
  
  // ════════════════════════════════════════════════════════════════
  // CONFLUENCE ENGINE — TA Decision Logic (NEW!)
  // Transforms raw data into actionable analysis
  // ════════════════════════════════════════════════════════════════
  const confluence = React.useMemo(() => {
    const result = buildConfluence(renderPlan);
    if (result) {
      console.log('[CONFLUENCE] ═══════════════════════════════════');
      console.log('[CONFLUENCE] TF:', selectedTF);
      console.log('[CONFLUENCE] Bias:', result.bias, '| Strength:', result.strength);
      console.log('[CONFLUENCE] Score:', result.score);
      console.log('[CONFLUENCE] Decision:', result.decision);
      console.log('[CONFLUENCE] Signals:', result.signals);
      console.log('[CONFLUENCE] ═══════════════════════════════════');
    }
    return result;
  }, [renderPlan, selectedTF]);
  
  // TRADE SETUP — generated from confluence analysis
  const generatedTradeSetup = React.useMemo(() => {
    return buildTradeSetup(renderPlan, confluence);
  }, [renderPlan, confluence]);
  
  // MODE-BASED LAYER VISIBILITY — Auto/Classic/Smart/Minimal
  const modeLayerVisibility = React.useMemo(() => {
    return getLayerVisibility(viewMode);
  }, [viewMode]);
  
  // TA COMPOSITION — complete technical setup view (BUILD FROM DATA!)
  const taComposition = React.useMemo(() => {
    if (!setupData) return null;
    
    const pattern = setupData.primary_pattern;
    const fib = setupData.fib;
    const rp = setupData.render_plan;
    const indicators = setupData.indicators;
    const decision = setupData.decision;
    
    // Если нет паттерна и нет данных — нет setup
    const hasPattern = pattern && pattern.type;
    const hasFib = fib && fib.levels?.length > 0;
    
    // Build active_figure from primary_pattern
    let active_figure = null;
    if (hasPattern) {
      active_figure = {
        type: pattern.type,
        direction: pattern.direction,
        confidence: pattern.confidence || 0.5,
        breakout_level: pattern.breakout_price || pattern.upper_line?.end_price,
        invalidation_level: pattern.invalidation_price || pattern.lower_line?.end_price,
      };
    }
    
    // Build active_fib from fib data
    let active_fib = null;
    if (hasFib) {
      const fibLevels = fib.levels || [];
      active_fib = {
        swing_type: fib.type || 'retracement',
        current_position: fib.current_zone || 'between_levels',
        key_levels: fibLevels.slice(0, 5).map(l => ({
          level: l.level,
          price: l.price,
          status: l.status || 'active',
        })),
      };
    }
    
    // Build relevant_overlays from indicators
    const relevant_overlays = [];
    if (indicators?.overlays) {
      indicators.overlays.slice(0, 3).forEach(o => {
        const lastValue = o.data?.[o.data.length - 1]?.value;
        if (lastValue) {
          relevant_overlays.push({
            display_name: o.name || o.id,
            current_value: lastValue,
          });
        }
      });
    }
    
    // Build breakout_logic from pattern or levels
    let breakout_logic = null;
    const levels = rp?.levels || setupData.levels || [];
    const currentPrice = setupData.current_price || rp?.market_state?.current_price;
    
    if (levels.length > 0 && currentPrice) {
      const resistances = levels.filter(l => l.type === 'resistance' && l.price > currentPrice);
      const supports = levels.filter(l => l.type === 'support' && l.price < currentPrice);
      
      const nearestResistance = resistances.length > 0 ? resistances.reduce((a, b) => b.price < a.price ? b : a) : null;
      const nearestSupport = supports.length > 0 ? supports.reduce((a, b) => b.price > a.price ? b : a) : null;
      
      if (nearestResistance || nearestSupport) {
        breakout_logic = {
          breakout_level: nearestResistance?.price,
          invalidation_level: nearestSupport?.price,
          breakout_type: 'resistance_break',
          risk_pct: currentPrice && nearestSupport ? ((currentPrice - nearestSupport.price) / currentPrice * 100) : null,
        };
      }
    }
    
    // Determine setup quality
    let setup_quality = 'low';
    if (hasPattern && pattern.confidence > 0.7) setup_quality = 'high';
    else if (hasPattern && pattern.confidence > 0.5) setup_quality = 'medium';
    else if (hasFib || levels.length > 0) setup_quality = 'medium';
    
    // Build setup_summary
    let setup_summary = '';
    if (hasPattern) {
      setup_summary = `${pattern.type?.replace(/_/g, ' ')} pattern detected with ${Math.round((pattern.confidence || 0.5) * 100)}% confidence`;
      if (pattern.direction) {
        setup_summary += ` — ${pattern.direction} bias`;
      }
    } else if (decision?.summary) {
      setup_summary = decision.summary;
    } else {
      setup_summary = 'Analyzing market structure...';
    }
    
    return {
      has_active_setup: hasPattern || hasFib || levels.length > 0,
      setup_quality,
      setup_summary,
      active_figure,
      active_fib,
      relevant_overlays,
      breakout_logic,
      active_zone: null,
      structure_context: decision?.context || 'neutral',
    };
  }, [setupData]);
  
  // ═══════════════════════════════════════════════════════════════
  // MARKET MECHANICS — POI, Liquidity from render_plan
  // ═══════════════════════════════════════════════════════════════
  const poi = setupData?.poi || null;
  
  // LIQUIDITY — prioritize render_plan over raw data
  const liquidity = React.useMemo(() => {
    const rpLiquidity = setupData?.render_plan?.liquidity;
    if (rpLiquidity) {
      // Convert render_plan format to MarketMechanicsRenderer format
      const pools = [];
      
      // Add BSL (above price)
      (rpLiquidity.bsl || []).forEach(bsl => {
        const price = typeof bsl.price === 'number' ? bsl.price : parseFloat(bsl.price);
        pools.push({
          type: 'buy_side_liquidity',
          side: 'high',
          price: price,
          strength: bsl.strength,
          touches: bsl.touches,
          label: bsl.label || `BSL @ ${price ? Math.round(price) : 'N/A'}`,
          status: 'active',
        });
      });
      
      // Add SSL (below price)
      (rpLiquidity.ssl || []).forEach(ssl => {
        const price = typeof ssl.price === 'number' ? ssl.price : parseFloat(ssl.price);
        pools.push({
          type: 'sell_side_liquidity',
          side: 'low',
          price: price,
          strength: ssl.strength,
          touches: ssl.touches,
          label: ssl.label || `SSL @ ${price ? Math.round(price) : 'N/A'}`,
          status: 'active',
        });
      });
      
      return {
        pools,
        sweeps: rpLiquidity.sweeps || [],
        equal_highs: [],
        equal_lows: [],
      };
    }
    return setupData?.liquidity || null;
  }, [setupData?.render_plan?.liquidity, setupData?.liquidity]);
  
  const chochValidation = setupData?.choch_validation || null;
  const displacement = setupData?.displacement || null;
  
  // ═══════════════════════════════════════════════════════════════
  // EXECUTION — prioritize render_plan execution (always visible!)
  // ═══════════════════════════════════════════════════════════════
  const execution = React.useMemo(() => {
    const rpExecution = setupData?.render_plan?.execution;
    if (rpExecution) {
      return rpExecution;
    }
    return setupData?.execution || null;
  }, [setupData?.render_plan?.execution, setupData?.execution]);
  
  const chainMap = setupData?.chain_map || [];
  const unifiedSetupData = setupData?.unified_setup || null;
  const fib = setupData?.fib || null;
  
  // Handle pattern click (switch between primary/alternatives)
  const handlePatternClick = (patternId) => {
    setActivePatternId(patternId);
  };
  
  // Handle scenario click (highlight corresponding pattern)
  const handleScenarioClick = (scenario) => {
    // Map scenario to pattern
    if (scenario.pattern) {
      const altIndex = alternativePatterns.findIndex(p => p.type === scenario.pattern);
      if (altIndex >= 0) {
        setActivePatternId(`alt-${altIndex}`);
      } else if (primaryPattern?.type === scenario.pattern) {
        setActivePatternId('primary');
      }
    }
  };
  
  // Map structure to array format for PatternActivationLayer
  const structureArray = structure ? [
    ...Array(structure.hh || 0).fill({ type: 'HH' }),
    ...Array(structure.hl || 0).fill({ type: 'HL' }),
    ...Array(structure.lh || 0).fill({ type: 'LH' }),
    ...Array(structure.ll || 0).fill({ type: 'LL' }),
  ] : [];
  
  // Build unified setup object for all components
  const unifiedSetup = React.useMemo(() => {
    if (!setupData) return null;
    
    const d = setupData.decision;
    const rp = setupData.render_plan;
    const indicators = setupData.indicator_result || setupData.ta_context?.indicators?.signals || [];
    const structureState = setupData.structure_state || setupData.structure_context;
    
    // Build structure array from structure_state swings or render_plan structure
    const buildStructureArray = () => {
      const swings = rp?.structure?.swings || [];
      if (swings.length > 0) {
        return swings.map(s => ({ type: s.type, time: s.time, price: s.price }));
      }
      // Fallback to structure_state counts
      if (structureState) {
        const arr = [];
        for (let i = 0; i < (structureState.hh_count || 0); i++) arr.push({ type: 'HH' });
        for (let i = 0; i < (structureState.hl_count || 0); i++) arr.push({ type: 'HL' });
        for (let i = 0; i < (structureState.lh_count || 0); i++) arr.push({ type: 'LH' });
        for (let i = 0; i < (structureState.ll_count || 0); i++) arr.push({ type: 'LL' });
        return arr;
      }
      return structureArray;
    };
    
    // Build indicators array from indicator_result
    const buildIndicatorsArray = () => {
      if (Array.isArray(indicators) && indicators.length > 0) {
        return indicators.map(ind => ({
          name: ind.name,
          direction: ind.direction?.toLowerCase(),
          signal_type: ind.signal_type,
          strength: ind.strength,
          description: ind.description,
        }));
      }
      return [];
    };
    
    // Derive bias and confidence from decision
    const derivedBias = d?.bias || (pattern?.direction) || 'neutral';
    const derivedConfidence = d?.confidence || pattern?.confidence || 0;
    const derivedSetupType = pattern?.type || (rp?.market_state?.trend_direction) || 'analysis';
    
    return {
      // Pattern as array (for PatternActivationLayer)
      patterns: pattern ? [{
        type: pattern.type,
        confidence: pattern.confidence,
        direction: pattern.direction || derivedBias,
        points: pattern.points,
      }] : [],
      
      // Single pattern object (for ResearchChart)
      pattern: pattern,
      
      // Levels array - from render_plan or computed levels
      levels: levels,
      
      // Structure as array with actual data
      structure: buildStructureArray(),
      
      // Setup details from decision
      setup_type: derivedSetupType,
      direction: derivedBias,
      confidence: derivedConfidence,
      confluence_score: d?.confidence || 0,
      trigger: setup?.trigger,
      invalidation: setup?.invalidation,
      targets: setup?.targets || [],
      
      // Indicators from API
      indicators: buildIndicatorsArray(),
      
      // Conflicts/risks
      conflicts: [],
      
      // Market context from decision and render_plan
      market_regime: rp?.market_state?.trend_direction || structureState?.regime || d?.context || 'neutral',
      asset: symbol,
      timeframe: selectedTF,
      current_price: setupData.current_price,
      
      // Additional fields for DeepAnalysisBlocks
      primary_confluence: d ? {
        score: d.confidence,
        components: [d.bias, d.strength].filter(Boolean),
      } : null,
      explanation: d?.summary,
    };
  }, [setupData, pattern, levels, structureArray, setup, symbol, selectedTF]);
  
  const technicalBias = unifiedSetup?.direction || 'neutral';
  const biasConfidence = unifiedSetup?.confidence || 0;

  // ═══════════════════════════════════════════════════════════════
  // GRAPH VISIBILITY ENGINE — Intelligent layer prioritization
  // ═══════════════════════════════════════════════════════════════
  const currentPrice = candles?.length > 0 ? candles[candles.length - 1]?.close : null;
  
  const visibilityContext = {
    setup: setupData?.setup,
    pattern_primary: setupData?.primary_pattern,
    pattern_alternative: setupData?.alternative_patterns?.[0],
    poi: poi,
    liquidity: liquidity,
    fib: setupData?.fibonacci,
    indicators: setupData?.indicators,
    choch: chochValidation,
    displacement: displacement,
    structure_context: structureContext || structure,
    current_price: currentPrice,
  };
  
  const layerVisibilityComputed = computeVisibility(visibilityContext, viewMode, renderPlan);
  console.log('[Visibility] viewMode:', viewMode, 'renderPlan:', renderPlan);
  console.log('[Visibility] computed:', layerVisibilityComputed);
  console.log('[Visibility] context keys with data:', Object.keys(visibilityContext).filter(k => visibilityContext[k]));
  const limits = getLayerLimits(viewMode);
  
  // Apply limits to data with price-based prioritization
  const limitedPOI = poi ? {
    ...poi,
    zones: applyLimits(poi.zones, 'poi_zones', limits, currentPrice),
  } : null;
  
  const limitedLiquidity = liquidity ? {
    ...liquidity,
    equal_highs: applyLimits(liquidity.equal_highs, 'liquidity_levels', limits, currentPrice),
    equal_lows: applyLimits(liquidity.equal_lows, 'liquidity_levels', limits, currentPrice),
  } : null;

  // Get visual styles for layers
  const poiStyle = getLayerStyle('poi');
  const liquidityStyle = getLayerStyle('liquidity');
  const patternStyle = getLayerStyle('pattern_primary');
  const fibStyle = getLayerStyle('fib');

  // Determine what to show based on view mode (unified - using layerVisibilityComputed only)
  const showPatterns = viewMode !== 'clean' && layerVisibilityComputed.patterns;
  const showLevels = layerVisibilityComputed.levels !== false;
  const showStructure = layerVisibilityComputed.structure;
  const showIndicators = viewMode === 'manual';
  const showBaseLayer = viewMode !== 'minimal';

  return (
    <Container data-testid="research-view">
      {/* Top Control Bar */}
      <TopBar>
        <ControlsLeft>
          {/* Search Asset */}
          <SearchWrapper>
            <SearchInput
              type="text"
              placeholder="Search"
              value={showDropdown ? searchQuery : (searchQuery || '')}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setShowDropdown(true);
              }}
              onFocus={() => setShowDropdown(true)}
              onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
              data-testid="asset-search"
            />
            {showDropdown && filteredSymbols.length > 0 && (
              <SymbolDropdown>
                {filteredSymbols.map(s => (
                  <SymbolOption
                    key={s}
                    $active={s === symbol}
                    onMouseDown={() => handleSymbolSelect(s)}
                  >
                    {s.replace('USDT', '')}
                  </SymbolOption>
                ))}
              </SymbolDropdown>
            )}
          </SearchWrapper>

          {/* MTF Timeframe Selector — ALL TIMEFRAMES */}
          <TfGroup>
            {TIMEFRAMES.map(tf => (
              <TfButton
                key={tf}
                $active={selectedTF === tf}
                onClick={() => setSelectedTF(tf)}
                data-testid={`tf-${tf}`}
              >
                {tf}
              </TfButton>
            ))}
          </TfGroup>

          {/* Chart Type */}
          <ChartTypeGroup>
            <ChartTypeBtn
              $active={chartType === 'candles'}
              onClick={() => setChartType('candles')}
              title="Candles"
            >
              <BarChart2 />
            </ChartTypeBtn>
            <ChartTypeBtn
              $active={chartType === 'line'}
              onClick={() => setChartType('line')}
              title="Line"
            >
              <LineChart />
            </ChartTypeBtn>
          </ChartTypeGroup>

          {/* Layer Toggles removed - using ViewModeSelector below chart instead */}
        </ControlsLeft>
      </TopBar>

      {/* ════════════════════════════════════════════════════════════════ */}
      {/* CHART CONTROLS — View mode, Indicators, Overlays (moved above chart) */}
      {/* ════════════════════════════════════════════════════════════════ */}
      {!loading && (
        <SubChartControls data-testid="sub-chart-controls">
          {/* View Mode Section */}
          <span className="section-label">View</span>
          <ViewModeSelector
            mode={viewMode}
            onChange={setViewMode}
          />
          
          <ControlDivider />
          
          {/* Indicators Section */}
          <span className="section-label">Indicators</span>
          <IndicatorSelector
            selectedOverlays={selectedOverlays}
            selectedPanes={selectedPanes}
            onOverlaysChange={setSelectedOverlays}
            onPanesChange={setSelectedPanes}
          />
          
          <ControlDivider />
          
          {/* Chart Overlays Section - OFF by default */}
          <span className="section-label">Overlays</span>
          <div className="overlay-section">
            <CollapsibleButton
              $active={showFibonacciOverlay}
              onClick={() => setShowFibonacciOverlay(!showFibonacciOverlay)}
              data-testid="fibonacci-toggle-btn"
              title="Show Fibonacci retracement levels on chart"
            >
              <RefreshCw size={13} />
              Fib
            </CollapsibleButton>
            <CollapsibleButton
              $active={showPatternOverlay}
              onClick={() => setShowPatternOverlay(!showPatternOverlay)}
              data-testid="pattern-toggle-btn"
              title="Show detected pattern info card on chart"
            >
              <Triangle size={13} />
              Pattern
            </CollapsibleButton>
            <CollapsibleButton
              $active={showSetupOverlay}
              onClick={() => setShowSetupOverlay(!showSetupOverlay)}
              data-testid="setup-toggle-btn"
              title="Show trade setup info card on chart"
            >
              <Target size={13} />
              Setup
            </CollapsibleButton>
            <CollapsibleButton
              $active={showTAOverlay}
              onClick={() => setShowTAOverlay(!showTAOverlay)}
              data-testid="ta-overlay-toggle-btn"
              title="Show full TA analysis overlay on chart"
            >
              <Layers size={13} />
              TA
            </CollapsibleButton>
          </div>
        </SubChartControls>
      )}

      {/* Main Content */}
      <MainContent>
        {/* Error Banner */}
        {error && (
          <ErrorBanner>
            <AlertTriangle size={18} />
            {error}
          </ErrorBanner>
        )}

        {/* ════════════════════════════════════════════════════════════════ */}
        {/* CHART FIRST — Main focus at the top */}
        {/* ════════════════════════════════════════════════════════════════ */}
        <ChartSection style={{ position: 'relative' }}>
          <ResearchChart
            candles={candles}
            // PRIMARY DATA SOURCE: render_plan from backend
            renderPlan={renderPlan}
            // TA MODE — controls layer visibility (Auto/Classic/Smart/Minimal)
            mode={viewMode}
            // TRADE SETUP — generated from confluence analysis (toggle with showSetupOverlay)
            tradeSetupOverlay={showSetupOverlay ? generatedTradeSetup : null}
            // Legacy props for backward compatibility
            pattern={pattern}
            levels={levels}
            setup={setup}
            structure={structureContext || structure}
            baseLayer={baseLayer}
            structureVisualization={structureVisualization}
            chartStructure={chartStructure}
            tradeSetup={tradeSetup}
            // Market Mechanics - use limited data based on visibility
            poi={layerVisibilityComputed.poi ? (poi || limitedPOI) : null}
            liquidity={layerVisibilityComputed.liquidity ? (liquidity || limitedLiquidity) : null}
            chochValidation={layerVisibilityComputed.choch ? chochValidation : null}
            displacement={layerVisibilityComputed.displacement ? displacement : null}
            // NEW: Execution layer from per-TF pipeline
            execution={execution}
            chainMap={chainMap}
            chartType={chartType}
            height={420}
            showLevels={showLevels}
            showPattern={showPatterns && layerVisibilityComputed.pattern_primary}
            showBaseLayer={showBaseLayer}
            showStructure={showStructure}
            showTargets={false}
            showExecutionOverlay={execution?.valid || layerVisibilityComputed.trade_setup}
            // Market Mechanics toggles - controlled by visibility engine
            showMarketMechanics={viewMode !== 'classic'}
            showPOI={layerVisibilityComputed.poi}
            showLiquidity={layerVisibilityComputed.liquidity}
            showSweeps={layerVisibilityComputed.sweep_markers}
            showCHOCH={layerVisibilityComputed.choch}
            showNarrative={viewMode !== 'minimal'}
            decision={decision}
            // Indicator Overlays - filtered by selection and mode
            // Classic/Auto mode: show selected indicators + fallback to user selection
            indicatorOverlays={
              layerVisibilityComputed.indicators_overlay
                ? (setupData?.indicators?.overlays || [])
                    .filter(o => {
                      // ALWAYS use user selection (selectedOverlays) - gives user control
                      return selectedOverlays.includes(o.id);
                    })
                    .slice(0, limits.overlays)
                : []
            }
            // Pattern Engine V2 - use primary_pattern from API
            patternV2={{ primary_pattern: setupData?.primary_pattern, alternative_patterns: setupData?.alternative_patterns }}
            // Fibonacci - use from per-TF pipeline
            fibonacci={fib || setupData?.fibonacci}
            // Toggle overlays visibility via buttons
            showFibonacciOverlay={showFibonacciOverlay}
            showPatternOverlay={showPatternOverlay}
          />
          {loading && (
            <LoadingOverlay>
              <Loader2 size={24} color="#3b82f6" />
              <span style={{ color: '#64748b', fontSize: 13 }}>Analyzing {symbol}...</span>
            </LoadingOverlay>
          )}
          
          {/* ═══════════════════════════════════════════════════════════════ */}
          {/* RENDER PLAN OVERLAY — TA visualization (moved from Chart Lab) */}
          {/* This is the ONLY place for TA renderers per product rules */}
          {/* ═══════════════════════════════════════════════════════════════ */}
          {showTAOverlay && (globalRenderPlan || renderPlan) && (
            <RenderPlanOverlay 
              renderPlan={globalRenderPlan || renderPlan}
              onChainStepClick={(step) => console.log('[Research/TA] Step clicked:', step)}
            />
          )}
          
        </ChartSection>
        

        {/* ════════════════════════════════════════════════════════════════ */}
        {/* UNIFIED ANALYSIS BAR — Below chart, combines all context panels */}
        {/* Replaces: MarketContextBar, Confluence Panel, MTFHeader, TAContext */}
        {/* ════════════════════════════════════════════════════════════════ */}
        {decision && (
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '12px',
            margin: '16px 0',
          }}>
            {/* LEFT: Market Context Summary */}
            <div style={{
              background: '#fff',
              border: '1px solid #e2e8f0',
              borderRadius: '12px',
              padding: '16px',
            }}>
              <div style={{
                fontSize: '11px',
                fontWeight: '600',
                color: '#64748b',
                textTransform: 'uppercase',
                marginBottom: '12px',
              }}>
                Market Context — {selectedTF}
              </div>
              
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: '12px',
              }}>
                {/* Bias */}
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '10px', color: '#94a3b8', marginBottom: '4px' }}>BIAS</div>
                  <div style={{
                    fontSize: '14px',
                    fontWeight: '700',
                    color: decision.bias === 'bullish' ? '#16a34a' :
                           decision.bias === 'bearish' ? '#dc2626' : '#64748b',
                  }}>
                    {(decision.bias || 'neutral').toUpperCase()}
                  </div>
                </div>
                
                {/* Confidence */}
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '10px', color: '#94a3b8', marginBottom: '4px' }}>CONFIDENCE</div>
                  <div style={{
                    fontSize: '14px',
                    fontWeight: '700',
                    color: decision.confidence >= 0.6 ? '#16a34a' :
                           decision.confidence >= 0.4 ? '#f59e0b' : '#64748b',
                  }}>
                    {Math.round((decision.confidence || 0) * 100)}%
                  </div>
                </div>
                
                {/* Strength */}
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '10px', color: '#94a3b8', marginBottom: '4px' }}>STRENGTH</div>
                  <div style={{
                    fontSize: '14px',
                    fontWeight: '700',
                    color: decision.strength === 'high' ? '#16a34a' :
                           decision.strength === 'medium' ? '#f59e0b' : '#94a3b8',
                  }}>
                    {(decision.strength || 'low').toUpperCase()}
                  </div>
                </div>
              </div>
              
              {/* Summary text */}
              {decision.summary && (
                <div style={{
                  marginTop: '12px',
                  padding: '10px',
                  background: '#f8fafc',
                  borderRadius: '8px',
                  fontSize: '12px',
                  color: '#475569',
                }}>
                  {decision.summary}
                </div>
              )}
            </div>
            
            {/* RIGHT: Pattern & Structure */}
            <div style={{
              background: '#fff',
              border: '1px solid #e2e8f0',
              borderRadius: '12px',
              padding: '16px',
            }}>
              <div style={{
                fontSize: '11px',
                fontWeight: '600',
                color: '#64748b',
                textTransform: 'uppercase',
                marginBottom: '12px',
              }}>
                Technical Setup
              </div>
              
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(2, 1fr)',
                gap: '12px',
              }}>
                {/* Pattern */}
                <div style={{
                  background: '#f8fafc',
                  borderRadius: '8px',
                  padding: '10px',
                }}>
                  <div style={{ fontSize: '10px', color: '#94a3b8', marginBottom: '4px' }}>PATTERN</div>
                  <div style={{
                    fontSize: '13px',
                    fontWeight: '600',
                    color: primaryPattern?.type ? '#0f172a' : '#94a3b8',
                  }}>
                    {primaryPattern?.type?.replace(/_/g, ' ') || 'None detected'}
                  </div>
                  {primaryPattern?.direction && (
                    <div style={{
                      fontSize: '10px',
                      marginTop: '4px',
                      color: primaryPattern.direction === 'bullish' ? '#16a34a' : 
                             primaryPattern.direction === 'bearish' ? '#dc2626' : '#64748b',
                    }}>
                      {primaryPattern.direction.toUpperCase()}
                    </div>
                  )}
                </div>
                
                {/* Levels Count */}
                <div style={{
                  background: '#f8fafc',
                  borderRadius: '8px',
                  padding: '10px',
                }}>
                  <div style={{ fontSize: '10px', color: '#94a3b8', marginBottom: '4px' }}>KEY LEVELS</div>
                  <div style={{
                    fontSize: '13px',
                    fontWeight: '600',
                    color: '#0f172a',
                  }}>
                    {levels?.length || 0} active
                  </div>
                  <div style={{ fontSize: '10px', marginTop: '4px', color: '#64748b' }}>
                    {levels?.filter(l => l.type === 'support').length || 0} support, {levels?.filter(l => l.type === 'resistance').length || 0} resistance
                  </div>
                </div>
              </div>
              
              {/* Tradeability Badge */}
              <div style={{
                marginTop: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}>
                <span style={{ fontSize: '11px', color: '#94a3b8' }}>Tradeability</span>
                <span style={{
                  fontSize: '11px',
                  fontWeight: '600',
                  padding: '4px 10px',
                  borderRadius: '4px',
                  background: decision.tradeability === 'high' ? 'rgba(34, 197, 94, 0.1)' :
                             decision.tradeability === 'medium' ? 'rgba(245, 158, 11, 0.1)' :
                             'rgba(239, 68, 68, 0.1)',
                  color: decision.tradeability === 'high' ? '#16a34a' :
                         decision.tradeability === 'medium' ? '#f59e0b' : '#dc2626',
                }}>
                  {(decision.tradeability || 'low').toUpperCase()}
                </span>
              </div>
            </div>
          </div>
        )}
        
        {/* NARRATIVE SUMMARY — Market Story Chain (includes Why reasoning) */}
        {!loading && decision && (
          <NarrativeSummary
            narrative={buildNarrative({
              liquidity,
              displacement,
              chochValidation,
              poi,
              decision,
              tradeSetup,
            })}
            decision={decision}
          />
        )}

        {/* UNIFIED SETUP + EXECUTION GRID */}
        {(setupData?.unified_setup || setupData?.execution_plan) && (
          <BottomGrid>
            {/* Left: Unified Setup — Validation Chain */}
            <UnifiedSetupPanel unifiedSetup={setupData.unified_setup} />
            
            {/* Right: Execution Plan — Prop-Trader Execution */}
            <ExecutionPanel executionPlan={setupData.execution_plan} />
          </BottomGrid>
        )}

        {/* PATTERNS + SCENARIOS GRID - NEW */}
        <BottomGrid>
          {/* Left: TA Composition — TECHNICAL SETUP VIEW */}
          <TACompositionPanel composition={taComposition} />
          
          {/* Right: Scenarios */}
          <ScenariosBlock
            scenarios={scenarios}
            onScenarioClick={handleScenarioClick}
          />
        </BottomGrid>
        
        {/* PATTERNS BLOCK — Below main grid */}
        <BottomSection>
          <PatternsBlock
            primaryPattern={primaryPattern}
            alternativePatterns={alternativePatterns}
            activePatternId={activePatternId}
            onPatternClick={handlePatternClick}
          />
        </BottomSection>

        {/* EXPLANATION PANEL — System Explanation (from Explanation Engine V1) */}
        <ExplanationPanel explanation={explanation} />

        {/* ═══════════════════════════════════════════════════════════════ */}
        {/* INDICATOR VISUALIZATION LAYER — Controlled by Visibility Engine */}
        {/* ═══════════════════════════════════════════════════════════════ */}
        {layerVisibilityComputed.indicators_panes && setupData?.indicators?.panes?.length > 0 && (
          <BottomSection>
            <IndicatorPanes 
              indicators={setupData.indicators}
              visiblePanes={
                renderPlan && viewMode !== 'manual'
                  ? (renderPlan.panes || []).slice(0, limits.panes)
                  : selectedPanes.slice(0, limits.panes)
              }
              paneHeight={80}
            />
          </BottomSection>
        )}
        
        {/* CONFLUENCE MATRIX — Hidden in minimal mode */}
        {/* Build confluence from taContext indicators for ConfluenceMatrix component */}
        {/* Now includes TA Brain expandable section */}
        {viewMode !== 'minimal' && taContext && (
          <BottomSection>
            <ConfluenceMatrix 
              confluence={{
                bullish: taContext.top_drivers?.filter(d => d.signal === 'bullish') || [],
                bearish: taContext.top_drivers?.filter(d => d.signal === 'bearish') || [],
                neutral: taContext.top_drivers?.filter(d => d.signal === 'neutral') || [],
                conflicts: [],
                overall_strength: taContext.summary?.aggregated_score || 0,
                overall_bias: taContext.summary?.aggregated_bias || 'neutral',
                confidence: taContext.summary?.aggregated_confidence || 0,
                summary: `${taContext.indicators?.bullish || 0} bullish, ${taContext.indicators?.bearish || 0} bearish signals`,
              }}
              taContext={taContext}
            />
          </BottomSection>
        )}

        {/* CONFIDENCE EXPLANATION - NEW */}
        <BottomSection>
          <ConfidenceExplanation explanation={confidenceExplanation} />
        </BottomSection>

        {/* Pattern Activation Layer */}
        <PatternActivationLayer
          setup={unifiedSetup}
          activeElements={activeElements}
          onToggleElement={handleToggleElement}
        />

        {/* Deep Analysis Blocks */}
        <DeepAnalysisBlocks
          setup={unifiedSetup}
          technicalBias={technicalBias}
          biasConfidence={biasConfidence}
        />
      </MainContent>

      {/* Toast */}
      {toast && <SuccessToast>{toast}</SuccessToast>}
    </Container>
  );
};

export default ResearchView;
