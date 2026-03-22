/**
 * IndicatorInsights Component
 * ===========================
 * Compact clickable cards for RSI/MACD.
 * Click = toggle indicator pane visibility.
 * No extra text, no modals.
 */

import React from 'react';
import styled from 'styled-components';
import { Activity } from 'lucide-react';

// ============================================
// STYLED COMPONENTS
// ============================================

const InsightsContainer = styled.div`
  display: flex;
  gap: 8px;
  padding: 8px 16px;
`;

const InsightCard = styled.button`
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: ${({ $active, $color }) => $active ? `${$color}15` : '#f8fafc'};
  border: 1px solid ${({ $active, $color }) => $active ? $color : '#e2e8f0'};
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
  
  &:hover {
    background: ${({ $color }) => `${$color}10`};
    border-color: ${({ $color }) => $color};
  }
`;

const IndicatorName = styled.span`
  font-size: 11px;
  font-weight: 700;
  color: #334155;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const IndicatorValue = styled.span`
  font-size: 13px;
  font-weight: 600;
  color: ${({ $color }) => $color || '#64748b'};
`;

const StateBadge = styled.span`
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  background: ${({ $color }) => `${$color}20`};
  color: ${({ $color }) => $color};
`;

// ============================================
// HELPER FUNCTIONS
// ============================================

const getRSIState = (value) => {
  if (value < 30) return { label: 'OVERSOLD', color: '#22c55e' };
  if (value > 70) return { label: 'OVERBOUGHT', color: '#ef4444' };
  return { label: 'NEUTRAL', color: '#64748b' };
};

const getMACDState = (histogram) => {
  if (histogram > 0) return { label: 'POSITIVE', color: '#22c55e' };
  return { label: 'NEGATIVE', color: '#ef4444' };
};

// ============================================
// MAIN COMPONENT
// ============================================

const IndicatorInsights = ({ 
  insights, 
  activeIndicators = { rsi: false, macd: false },
  onToggle 
}) => {
  if (!insights) return null;

  const { rsi, macd } = insights;
  
  const rsiState = rsi ? getRSIState(rsi.value) : null;
  const macdState = macd ? getMACDState(macd.histogram) : null;

  return (
    <InsightsContainer data-testid="indicator-insights">
      {/* RSI Card */}
      {rsi && (
        <InsightCard 
          $active={activeIndicators.rsi}
          $color={rsiState.color}
          onClick={() => onToggle?.('rsi')}
          data-testid="rsi-card"
        >
          <Activity size={14} color={rsiState.color} />
          <IndicatorName>RSI</IndicatorName>
          <IndicatorValue $color={rsiState.color}>
            {rsi.value?.toFixed(1)}
          </IndicatorValue>
          <StateBadge $color={rsiState.color}>
            {rsiState.label}
          </StateBadge>
        </InsightCard>
      )}

      {/* MACD Card */}
      {macd && (
        <InsightCard 
          $active={activeIndicators.macd}
          $color={macdState.color}
          onClick={() => onToggle?.('macd')}
          data-testid="macd-card"
        >
          <Activity size={14} color={macdState.color} />
          <IndicatorName>MACD</IndicatorName>
          <IndicatorValue $color={macdState.color}>
            {macd.histogram?.toFixed(1)}
          </IndicatorValue>
          <StateBadge $color={macdState.color}>
            {macdState.label}
          </StateBadge>
        </InsightCard>
      )}
    </InsightsContainer>
  );
};

export default IndicatorInsights;
