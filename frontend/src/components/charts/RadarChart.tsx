import { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { MATURITY_ZONES } from '@/types';

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
    const height = 500;
    const margin = 70;
    const radius = Math.min(width, height) / 2 - margin;

    const axes = DIMENSION_ORDER;
    const angleSlice = (Math.PI * 2) / axes.length;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();
    svg.attr('viewBox', '0 0 ' + width + ' ' + height);

    const g = svg.append('g').attr('transform', 'translate(' + (width / 2) + ',' + (height / 2) + ')');

    // === 1. Концентрические зоны зрелости (Concept v5.0 Table 3.2) ===
    MATURITY_ZONES.slice().reverse().forEach((zone) => {
      const outerRadius = (zone.max / maxValue) * radius;
      g.append('circle')
        .attr('r', outerRadius)
        .attr('fill', zone.color)
        .attr('opacity', 0.4)
        .attr('stroke', 'none');
    });

    // Подписи зон (справа)
    MATURITY_ZONES.forEach((zone) => {
      const midRadius = ((zone.min + zone.max) / 2 / maxValue) * radius;
      g.append('text')
        .attr('x', radius + 10)
        .attr('y', -midRadius)
        .attr('text-anchor', 'start')
        .attr('dominant-baseline', 'middle')
        .attr('class', 'text-[9px] fill-gray-600 font-medium')
        .text(zone.name + ' (' + zone.min.toFixed(1) + '-' + zone.max.toFixed(1) + ')');
    });

    // === 2. Оси ===
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
        .attr('class', 'text-xs fill-gray-800 font-semibold')
        .text(DIMENSION_LABELS[axis] || axis);

      // Пульсация критичных осей (score <= 1.8)
      const score = dimensionScores[axis] || 0;
      if (score <= 1.8) {
        const pointX = Math.cos(angle) * (score / maxValue) * radius;
        const pointY = Math.sin(angle) * (score / maxValue) * radius;
        g.append('circle')
          .attr('cx', pointX)
          .attr('cy', pointY)
          .attr('r', 6)
          .attr('fill', '#EF4444')
          .attr('opacity', 0.8)
          .append('animate')
          .attr('attributeName', 'r')
          .attr('values', '6;12;6')
          .attr('dur', '1.5s')
          .attr('repeatCount', 'indefinite');
      }
    });

    // === 3. Слой бенчмарка (серый пунктир) ===
    if (benchmarkScores) {
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

      // Ромбы на бенчмарке
      benchPoints.forEach(([x, y]) => {
        g.append('path')
          .attr('d', d3.symbol().type(d3.symbolDiamond).size(40) as any)
          .attr('transform', 'translate(' + x + ',' + y + ')')
          .attr('fill', '#9CA3AF');
      });
    }

    // === 4. Слой целевого состояния (зелёный пунктир) ===
    if (targetScores) {
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

    // === 5. Gap-зона (красные штрихи между current и target) ===
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

    // === 6. Слой текущего состояния (синий, основной) ===
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

    // Точки текущего состояния (цвет по зоне зрелости)
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

    // === 7. Легенда ===
    const legend = g.append('g').attr('transform', 'translate(' + (-width / 2 + 10) + ',' + (height / 2 - 80) + ')');

    const legendItems = [
      { label: 'Текущее', color: '#2563eb', dash: '' },
      { label: 'Целевое', color: '#10B981', dash: '4,4' },
      { label: 'Бенчмарк', color: '#9CA3AF', dash: '5,5' },
    ];

    legendItems.forEach((item, i) => {
      const y = i * 18;
      legend.append('line')
        .attr('x1', 0).attr('y1', y)
        .attr('x2', 20).attr('y2', y)
        .attr('stroke', item.color)
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', item.dash);
      legend.append('text')
        .attr('x', 26).attr('y', y)
        .attr('dominant-baseline', 'middle')
        .attr('class', 'text-xs fill-gray-700')
        .text(item.label);
    });

  }, [dimensionScores, targetScores, benchmarkScores, maxValue, showGap]);

  return <svg ref={svgRef} className="w-full max-w-lg mx-auto" />;
}