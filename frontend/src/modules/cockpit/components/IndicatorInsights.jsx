/**
 * IndicatorInsights Component
 * ===========================
 * Displays interpreted RSI/MACD insights with state, bias, and summary.
 * 
 * For Research view - shows meaning, not just raw numbers.
 */

import React from 'react';
import styled from 'styled-components';
import { TrendingUp, TrendingDown, Minus, Activity } from 'lucide-react';

// ============================================
// STYLED COMPONENTS
// ============================================

const InsightsContainer = styled.div`
  display: flex;
  gap: 12px;
  padding: 12px 16px;
  background: #ffffff;
  border: 1px solid #eef1f5;
  border-radius: 10px;
  margin-top: 8px;
`;

const InsightCard = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 10px 12px;
  background: ${({ $bgColor }) => $bgColor || '#f8fafc'};
  border-radius: 8px;
  border-left: 3px solid ${({ $accentColor }) => $accentColor || '#64748b'};
`;

const InsightHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const InsightTitle = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  
  .name {
    font-size: 11px;
    font-weight: 700;
    color: #334155;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  
  .value {
    font-size: 12px;
    font-weight: 600;
    color: #64748b;
  }
`;

const StateBadge = styled.span`
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  background: ${({ $color }) => $color ? `${$color}20` : '#f1f5f9'};
  color: ${({ $color }) => $color || '#64748b'};
`;

const InsightSummary = styled.p`
  margin: 0;
  font-size: 12px;
  color: #475569;
  line-height: 1.4;
`;

const BiasIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
  
  .bias-label {
    font-size: 10px;
    color: #94a3b8;
    text-transform: uppercase;
  }
  
  .bias-value {
    font-size: 10px;
    font-weight: 600;
    color: ${({ $color }) => $color || '#64748b'};
  }
`;

// ============================================
// HELPER FUNCTIONS
// ============================================

const getBiasIcon = (bias) => {
  if (bias?.includes('bullish')) return <TrendingUp size={12} />;
  if (bias?.includes('bearish')) return <TrendingDown size={12} />;
  return <Minus size={12} />;
};

const getBiasColor = (bias) => {
  if (bias?.includes('bullish')) return '#22c55e';
  if (bias?.includes('bearish')) return '#ef4444';
  return '#64748b';
};

const formatState = (state) => {
  if (!state) return 'Unknown';
  return state
    .replace(/_/g, ' ')
    .replace(/\b\w/g, c => c.toUpperCase());
};

const getBackgroundColor = (color) => {
  if (!color) return '#f8fafc';
  // Make it very light
  return `${color}10`;
};

// ============================================
// MAIN COMPONENT
// ============================================

const IndicatorInsights = ({ insights }) => {
  if (!insights || (!insights.rsi && !insights.macd)) {
    return null;
  }

  const { rsi, macd } = insights;

  return (
    <InsightsContainer data-testid="indicator-insights">
      {/* RSI Insight */}
      {rsi && (
        <InsightCard 
          $bgColor={getBackgroundColor(rsi.color)}
          $accentColor={rsi.color}
          data-testid="rsi-insight"
        >
          <InsightHeader>
            <InsightTitle>
              <Activity size={14} color={rsi.color} />
              <span className="name">RSI</span>
              <span className="value">{rsi.value}</span>
            </InsightTitle>
            <StateBadge $color={rsi.color}>
              {formatState(rsi.state)}
            </StateBadge>
          </InsightHeader>
          
          <InsightSummary>{rsi.summary}</InsightSummary>
          
          <BiasIndicator $color={getBiasColor(rsi.bias)}>
            {getBiasIcon(rsi.bias)}
            <span className="bias-label">Bias:</span>
            <span className="bias-value">{formatState(rsi.bias)}</span>
            <span className="bias-label" style={{ marginLeft: '8px' }}>Strength:</span>
            <span className="bias-value">{rsi.strength?.toUpperCase()}</span>
          </BiasIndicator>
        </InsightCard>
      )}

      {/* MACD Insight */}
      {macd && (
        <InsightCard 
          $bgColor={getBackgroundColor(macd.color)}
          $accentColor={macd.color}
          data-testid="macd-insight"
        >
          <InsightHeader>
            <InsightTitle>
              <Activity size={14} color={macd.color} />
              <span className="name">MACD</span>
              <span className="value">{macd.histogram?.toFixed(1)}</span>
            </InsightTitle>
            <StateBadge $color={macd.color}>
              {formatState(macd.state)}
            </StateBadge>
          </InsightHeader>
          
          <InsightSummary>{macd.summary}</InsightSummary>
          
          <BiasIndicator $color={getBiasColor(macd.bias)}>
            {getBiasIcon(macd.bias)}
            <span className="bias-label">Bias:</span>
            <span className="bias-value">{formatState(macd.bias)}</span>
            <span className="bias-label" style={{ marginLeft: '8px' }}>Strength:</span>
            <span className="bias-value">{macd.strength?.toUpperCase()}</span>
          </BiasIndicator>
        </InsightCard>
      )}
    </InsightsContainer>
  );
};

export default IndicatorInsights;
