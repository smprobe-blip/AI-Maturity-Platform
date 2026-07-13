import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface RadarChartProps {
  dimensionScores: Record<string, number>;
  targetScores?: Record<string, number>;
  benchmarkScores?: Record<string, number>;
  maxValue?: number;
  showGap?: boolean;
}

const DIMENSION_LABELS: Record<string, string> = {
  '1': 'Стратегия',
  '2': 'Люди',
  '3': 'Инфра',
  '4': 'Данные',
  '5': 'Модели',
  '6': 'Внедрение',
  '7': 'R&D',
};

const DIMENSION_ORDER = ['1', '2', '3', '4', '5', '6', '7'];

const MATURITY_ZONES = [
  { min: 1.0, max: 1.8, label: 'Начальный', color: '#FEE2E2' },
  { min: 1.9, max: 2.6, label: 'AI-Enabled', color: '#FEF3C7' },
  { min: 2.7, max: 3.4, label: 'AI-Driven', color: '#DCFCE7' },
  { min: 3.5, max: 4.2, label: 'AI-First', color: '#DBEAFE' },
  { min: 4.3, max: 5.0, label: 'AI-Native', color: '#EDE9FE' },
];

export function RadarChart({
  dimensionScores,
  targetScores,
  benchmarkScores,
  maxValue = 5,
  showGap = true,
}: RadarChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const width = 500;
    const height = 620; // Увеличили высоту
    const margin = 70;
    const radius = Math.min(width, height - 100) / 2 - margin;

    const axes = DIMENSION_ORDER;
    const angleSlice = (Math.PI * 2) / axes.length;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();
    svg.attr('viewBox', `0 0 ${width} ${height}`);

    const g = svg.append('g').attr('transform', `translate(${width / 2}, ${height / 2 - 30})`);

    // === 1. Concentric maturity zones ===
    MATURITY_ZONES.slice().reverse().forEach((zone) => {
      const outerRadius = (zone.max / maxValue) * radius;
      g.append('circle')
        .attr('r', outerRadius)
        .attr('fill', zone.color)
        .attr('opacity', 0.3)
        .attr('stroke', 'none');
    });

    // === 2. Axes ===
    axes.forEach((axis, i) => {
      const angle = angleSlice * i - Math.PI / 2;
      const x = Math.cos(angle) * radius;
      const y = Math.sin(angle) * radius;

      g.append('line')
        .attr('x1', 0).attr('y1', 0)
        .attr('x2', x).attr('y2', y)
        .attr('stroke', '#9CA3AF')
        .attr('stroke-width', 1);

      const labelX = Math.cos(angle) * (radius + 35);
      const labelY = Math.sin(angle) * (radius + 35);

      g.append('text')
        .attr('x', labelX)
        .attr('y', labelY)
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'middle')
        .attr('font-size', '12px')
        .attr('font-weight', '600')
        .attr('fill', '#1F2937')
        .text(DIMENSION_LABELS[axis] || axis);

      // Pulsing animation for critical axes (score <= 1.8)
      const score = dimensionScores[axis] || 0;
      if (score <= 1.8) {
        const pointX = Math.cos(angle) * (score / maxValue) * radius;
        const pointY = Math.sin(angle) * (score / maxValue) * radius;
        
        const pulseCircle = g.append('circle')
          .attr('cx', pointX)
          .attr('cy', pointY)
          .attr('r', 6)
          .attr('fill', '#EF4444')
          .attr('opacity', 0.8);
        
        pulseCircle.append('animate')
          .attr('attributeName', 'r')
          .attr('values', '6;12;6')
          .attr('dur', '1.5s')
          .attr('repeatCount', 'indefinite');
      }
    });

    // === 3. Benchmark layer (gray dashed with diamonds) ===
    if (benchmarkScores && Object.keys(benchmarkScores).length > 0) {
      const benchPoints = axes.map((axis, i) => {
        const value = benchmarkScores[axis] || 0;
        const r = (value / maxValue) * radius;
        const angle = angleSlice * i - Math.PI / 2;
        return [Math.cos(angle) * r, Math.sin(angle) * r];
      });

      g.append('path')
        .datum(benchPoints)
        .attr('d', d3.line().curve(d3.curveLinearClosed) as any)
        .attr('fill', 'none')
        .attr('stroke', '#9CA3AF')
        .attr('stroke-width', 1.5)
        .attr('stroke-dasharray', '5,5');

      benchPoints.forEach(([x, y]) => {
        g.append('path')
          .attr('d', d3.symbol().type(d3.symbolDiamond).size(40) as any)
          .attr('transform', `translate(${x},${y})`)
          .attr('fill', '#9CA3AF');
      });
    }

    // === 4. Target layer (green dashed) ===
    if (targetScores && Object.keys(targetScores).length > 0) {
      const targetPoints = axes.map((axis, i) => {
        const value = targetScores[axis] || 0;
        const r = (value / maxValue) * radius;
        const angle = angleSlice * i - Math.PI / 2;
        return [Math.cos(angle) * r, Math.sin(angle) * r];
      });

      g.append('path')
        .datum(targetPoints)
        .attr('d', d3.line().curve(d3.curveLinearClosed) as any)
        .attr('fill', 'none')
        .attr('stroke', '#10B981')
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', '4,4');
    }

    // === 5. Gap zone (red hatching) ===
    if (showGap && targetScores) {
      axes.forEach((axis, i) => {
        const current = dimensionScores[axis] || 0;
        const target = targetScores[axis] || 0;
        
        if (target > current) {
          const angle = angleSlice * i - Math.PI / 2;
          const r1 = (current / maxValue) * radius;
          const r2 = (target / maxValue) * radius;
          
          const x1 = Math.cos(angle) * r1;
          const y1 = Math.sin(angle) * r1;
          const x2 = Math.cos(angle) * r2;
          const y2 = Math.sin(angle) * r2;

          g.append('line')
            .attr('x1', x1).attr('y1', y1)
            .attr('x2', x2).attr('y2', y2)
            .attr('stroke', '#EF4444')
            .attr('stroke-width', 2)
            .attr('stroke-dasharray', '2,2')
            .attr('opacity', 0.6);
        }
      });
    }

    // === 6. Current state layer (main, solid + fill) ===
    const currentPoints = axes.map((axis, i) => {
      const value = dimensionScores[axis] || 0;
      const r = (value / maxValue) * radius;
      const angle = angleSlice * i - Math.PI / 2;
      return [Math.cos(angle) * r, Math.sin(angle) * r];
    });

    g.append('path')
      .datum(currentPoints)
      .attr('d', d3.line().curve(d3.curveLinearClosed) as any)
      .attr('fill', 'rgba(59, 130, 246, 0.25)')
      .attr('stroke', '#2563eb')
      .attr('stroke-width', 2.5);

    currentPoints.forEach(([x, y], i) => {
      const axis = axes[i];
      const score = dimensionScores[axis] || 0;
      
      const color = score <= 1.8 ? '#EF4444' 
                 : score <= 2.6 ? '#F59E0B' 
                 : score <= 3.4 ? '#10B981' 
                 : '#2563eb';

      g.append('circle')
        .attr('cx', x).attr('cy', y)
        .attr('r', 5)
        .attr('fill', color)
        .attr('stroke', 'white')
        .attr('stroke-width', 2);
    });

    // === 7. Line Legend (Top-Left) - ЕДИНСТВЕННАЯ ===
    const lineLegend = g.append('g')
      .attr('transform', `translate(${-width/2 + 15}, ${-height/2 + 45})`);

    const legendItems = [
      { label: 'Текущее', color: '#2563eb', dash: '' },
      { label: 'Целевое', color: '#10B981', dash: '4,4' },
      { label: 'Бенчмарк', color: '#9CA3AF', dash: '5,5' },
    ];

    legendItems.forEach((item, i) => {
      const y = i * 20;
      lineLegend.append('line')
        .attr('x1', 0).attr('y1', y)
        .attr('x2', 20).attr('y2', y)
        .attr('stroke', item.color)
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', item.dash);

      lineLegend.append('text')
        .attr('x', 26).attr('y', y)
        .attr('dominant-baseline', 'middle')
        .attr('font-size', '12px')
        .attr('fill', '#374151')
        .text(item.label);
    });

    // === 8. Horizontal Gradient Legend for AI Levels (Bottom) ===
    const legendWidth = radius * 2;
    const legendY = radius + 50; // Увеличили отступ
    
    const levelLegendGroup = g.append('g')
      .attr('transform', `translate(${-legendWidth / 2}, ${legendY})`);

    // Create gradient definition
    const defs = svg.append('defs');
    const gradient = defs.append('linearGradient')
      .attr('id', 'maturityGradient')
      .attr('x1', '0%').attr('y1', '0%')
      .attr('x2', '100%').attr('y2', '0%');

    MATURITY_ZONES.forEach((zone, i) => {
      const offsetStart = (i / MATURITY_ZONES.length) * 100;
      const offsetEnd = ((i + 1) / MATURITY_ZONES.length) * 100;
      
      gradient.append('stop')
        .attr('offset', `${offsetStart}%`)
        .attr('stop-color', zone.color);
        
      if (i === MATURITY_ZONES.length - 1) {
        gradient.append('stop')
          .attr('offset', `${offsetEnd}%`)
          .attr('stop-color', zone.color);
      }
    });

    // Draw gradient bar
    levelLegendGroup.append('rect')
      .attr('width', legendWidth)
      .attr('height', 12)
      .attr('fill', 'url(#maturityGradient)')
      .attr('rx', 6);

    // Draw labels below the bar
    MATURITY_ZONES.forEach((zone, i) => {
      const x = ((i + 0.5) / MATURITY_ZONES.length) * legendWidth;
      
      // Level name
      levelLegendGroup.append('text')
        .attr('x', x)
        .attr('y', 28)
        .attr('text-anchor', 'middle')
        .attr('font-size', '11px')
        .attr('font-weight', '700')
        .attr('fill', '#111827')
        .text(zone.label);
        
      // Score range
      levelLegendGroup.append('text')
        .attr('x', x)
        .attr('y', 42)
        .attr('text-anchor', 'middle')
        .attr('font-size', '10px')
        .attr('fill', '#6B7280')
        .text(`${zone.min.toFixed(1)}-${zone.max.toFixed(1)}`);
    });

  }, [dimensionScores, targetScores, benchmarkScores, maxValue, showGap]);

  return <svg ref={svgRef} className="w-full max-w-lg mx-auto" />;
}