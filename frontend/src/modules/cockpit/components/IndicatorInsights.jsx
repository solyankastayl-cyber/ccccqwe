/**
 * IndicatorInsights Component V2
 * ==============================
 * RSI + MACD cards with proper market stage interpretation.
 * Click = toggle pane visibility.
 * Combined signal shown as action badge.
 */

import React from 'react';
import styled from 'styled-components';
import { TrendingUp, TrendingDown, Minus, Activity, Target } from 'lucide-react';

// ============================================
// STYLED COMPONENTS
// ============================================

const InsightsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px 16px;
  background: #ffffff;
  border: 1px solid #eef1f5;
  border-radius: 10px;
  margin-top: 8px;
`;

const CardsRow = styled.div`
  display: flex;
  gap: 12px;
`;

const InsightCard = styled.button`
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px 12px;
  background: ${({ $active, $bgColor }) => $active ? $bgColor : '#f8fafc'};
  border: 1px solid ${({ $active, $accentColor }) => $active ? $accentColor : '#e2e8f0'};
  border-left: 3px solid ${({ $accentColor }) => $accentColor || '#64748b'};
  border-radius: 8px;
  cursor: pointer;
  text-align: left;
  transition: all 0.15s ease;
  
  &:hover {
    background: ${({ $bgColor }) => $bgColor};
    border-color: ${({ $accentColor }) => $accentColor};
  }
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
  font-size: 11px;
  color: #64748b;
  line-height: 1.3;
`;

const SignalBar = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: ${({ $bgColor }) => $bgColor || '#f8fafc'};
  border-radius: 6px;
  border: 1px solid ${({ $borderColor }) => $borderColor || '#e2e8f0'};
`;

const SignalLabel = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  
  .icon {
    display: flex;
  }
  
  .text {
    font-size: 12px;
    font-weight: 700;
    color: ${({ $color }) => $color || '#334155'};
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
`;

const SignalSummary = styled.span`
  font-size: 11px;
  color: #64748b;
`;

// ============================================
// HELPERS
// ============================================

const formatState = (state) => {
  if (!state) return '';
  return state.replace(/_/g, ' ').toUpperCase();
};

const getSignalConfig = (signal) => {
  const configs = {
    'WATCH_LONG': {
      icon: <TrendingUp size={14} />,
      color: '#22c55e',
      bgColor: '#22c55e10',
      borderColor: '#22c55e40'
    },
    'WATCH_SHORT': {
      icon: <TrendingDown size={14} />,
      color: '#ef4444',
      bgColor: '#ef444410',
      borderColor: '#ef444440'
    },
    'BULLISH_CONTINUATION': {
      icon: <TrendingUp size={14} />,
      color: '#22c55e',
      bgColor: '#22c55e10',
      borderColor: '#22c55e40'
    },
    'BEARISH_CONTINUATION': {
      icon: <TrendingDown size={14} />,
      color: '#ef4444',
      bgColor: '#ef444410',
      borderColor: '#ef444440'
    },
    'NO_TRADE': {
      icon: <Minus size={14} />,
      color: '#64748b',
      bgColor: '#f8fafc',
      borderColor: '#e2e8f0'
    }
  };
  return configs[signal] || configs['NO_TRADE'];
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

  const { rsi, macd, combined } = insights;
  const signalConfig = combined ? getSignalConfig(combined.signal) : null;

  return (
    <InsightsContainer data-testid="indicator-insights">
      {/* RSI + MACD Cards */}
      <CardsRow>
        {rsi && (
          <InsightCard 
            $active={activeIndicators.rsi}
            $bgColor={`${rsi.color}10`}
            $accentColor={rsi.color}
            onClick={() => onToggle?.('rsi')}
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
          </InsightCard>
        )}

        {macd && (
          <InsightCard 
            $active={activeIndicators.macd}
            $bgColor={`${macd.color}10`}
            $accentColor={macd.color}
            onClick={() => onToggle?.('macd')}
            data-testid="macd-insight"
          >
            <InsightHeader>
              <InsightTitle>
                <Activity size={14} color={macd.color} />
                <span className="name">MACD</span>
              </InsightTitle>
              <StateBadge $color={macd.color}>
                {formatState(macd.state)}
              </StateBadge>
            </InsightHeader>
            <InsightSummary>{macd.summary}</InsightSummary>
          </InsightCard>
        )}
      </CardsRow>

      {/* Combined Signal */}
      {combined && signalConfig && (
        <SignalBar 
          $bgColor={signalConfig.bgColor}
          $borderColor={signalConfig.borderColor}
          data-testid="combined-signal"
        >
          <SignalLabel $color={signalConfig.color}>
            <span className="icon">{signalConfig.icon}</span>
            <span className="text">{combined.signal.replace(/_/g, ' ')}</span>
          </SignalLabel>
          <SignalSummary>{combined.summary}</SignalSummary>
        </SignalBar>
      )}
    </InsightsContainer>
  );
};

export default IndicatorInsights;
