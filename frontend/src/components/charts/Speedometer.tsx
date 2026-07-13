import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface SpeedometerProps {
  /** ROI percentage (e.g., 125 for +125%) */
  roiPercent: number;
  /** NPV in millions RUB */
  npvMillions?: number;
  /** Payback period in months */
  paybackMonths?: number;
  /** Confidence level */
  confidence?: 'low' | 'medium' | 'high';
  /** Min value for scale */
  minValue?: number;
  /** Max value for scale */
  maxValue?: number;
  /** Size in pixels */
  size?: number;
}

export function Speedometer({
  roiPercent,
  npvMillions,
  paybackMonths,
  confidence = 'medium',
  minValue = -50,
  maxValue = 500,
  size = 320,
}: SpeedometerProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const width = size;
    const height = size * 0.75;
    const cx = width / 2;
    const cy = height * 0.9;
    const radius = size * 0.4;

    // Arc: 270 degrees (from -225 to 45 degrees)
    const startAngle = -Math.PI * 1.25;  // -225°
    const endAngle = Math.PI * 0.25;     // 45°

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();
    svg.attr('viewBox', `0 0 ${width} ${height}`);

    // === 1. Color zones (3 segments) ===
    const zones = [
      { from: minValue, to: 0, color: '#FEE2E2', label: 'Убыток' },
      { from: 0, to: 100, color: '#FEF3C7', label: 'Умеренный' },
      { from: 100, to: maxValue, color: '#DCFCE7', label: 'Высокий' },
    ];

    const angleScale = d3.scaleLinear()
      .domain([minValue, maxValue])
      .range([startAngle, endAngle])
      .clamp(true);

    const arc = d3.arc()
      .innerRadius(radius * 0.75)
      .outerRadius(radius)
      .startAngle((d: any) => angleScale(d.from) + Math.PI / 2)
      .endAngle((d: any) => angleScale(d.to) + Math.PI / 2);

    const g = svg.append('g').attr('transform', `translate(${cx}, ${cy})`);

    g.selectAll('.zone')
      .data(zones)
      .enter()
      .append('path')
      .attr('d', arc as any)
      .attr('fill', (d: any) => d.color)
      .attr('stroke', '#fff')
      .attr('stroke-width', 2);

    // === 2. Tick marks and labels ===
    const ticks = [minValue, 0, 50, 100, 200, 300, 400, maxValue].filter(
      (v) => v <= maxValue
    );

    ticks.forEach((value) => {
      const angle = angleScale(value) + Math.PI / 2;
      const x1 = Math.cos(angle) * radius;
      const y1 = Math.sin(angle) * radius;
      const x2 = Math.cos(angle) * (radius * 1.08);
      const y2 = Math.sin(angle) * (radius * 1.08);

      g.append('line')
        .attr('x1', x1).attr('y1', y1)
        .attr('x2', x2).attr('y2', y2)
        .attr('stroke', '#6B7280')
        .attr('stroke-width', 2);

      const labelX = Math.cos(angle) * (radius * 1.2);
      const labelY = Math.sin(angle) * (radius * 1.2);

      g.append('text')
        .attr('x', labelX)
        .attr('y', labelY)
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'middle')
        .attr('class', 'text-[10px] fill-gray-600 font-medium')
        .text(`${value}%`);
    });

    // === 3. Needle (animated) ===
    const targetAngle = angleScale(roiPercent) + Math.PI / 2;
    const needleLength = radius * 0.85;

    const needle = g.append('g')
      .attr('class', 'needle')
      .attr('transform', `rotate(${startAngle * 180 / Math.PI + 90})`);

    needle.append('path')
      .attr('d', `M 0,-8 L ${needleLength},0 L 0,8 L -15,0 Z`)
      .attr('fill', '#1F2937')
      .attr('stroke', '#111827')
      .attr('stroke-width', 1);

    needle.append('circle')
      .attr('r', 10)
      .attr('fill', '#1F2937')
      .attr('stroke', '#fff')
      .attr('stroke-width', 2);

    // Animate needle
    needle
      .transition()
      .duration(1500)
      .ease(d3.easeCubicOut)
      .attr('transform', `rotate(${targetAngle * 180 / Math.PI + 90})`);

    // === 4. Center display (big numbers) ===
    const roiColor = roiPercent >= 100 
      ? '#16A34A'   // green
      : roiPercent >= 0 
        ? '#CA8A04' // yellow
        : '#DC2626'; // red

    g.append('text')
      .attr('x', 0)
      .attr('y', -radius * 0.15)
      .attr('text-anchor', 'middle')
      .attr('class', 'text-3xl font-bold')
      .attr('fill', roiColor)
      .text(`${roiPercent > 0 ? '+' : ''}${roiPercent.toFixed(0)}%`);

    g.append('text')
      .attr('x', 0)
      .attr('y', -radius * 0.15 + 22)
      .attr('text-anchor', 'middle')
      .attr('class', 'text-xs fill-gray-500 font-medium')
      .text('ROI за 3 года');

    // NPV (if provided)
    if (npvMillions !== undefined && npvMillions !== null) {
      g.append('text')
        .attr('x', 0)
        .attr('y', -radius * 0.15 + 48)
        .attr('text-anchor', 'middle')
        .attr('class', 'text-sm font-semibold fill-gray-700')
        .text(`NPV: ${npvMillions > 0 ? '+' : ''}${npvMillions.toFixed(1)} млн ₽`);
    }

    // Payback (if provided)
    if (paybackMonths !== undefined && paybackMonths !== null) {
      g.append('text')
        .attr('x', 0)
        .attr('y', -radius * 0.15 + 68)
        .attr('text-anchor', 'middle')
        .attr('class', 'text-xs fill-gray-500')
        .text(`Окупаемость: ${paybackMonths} мес`);
    }

    // Confidence badge
    const confidenceConfig = {
      low: { color: '#DC2626', bg: '#FEE2E2', label: 'Низкая' },
      medium: { color: '#CA8A04', bg: '#FEF3C7', label: 'Средняя' },
      high: { color: '#16A34A', bg: '#DCFCE7', label: 'Высокая' },
    };
    const conf = confidenceConfig[confidence];

    g.append('rect')
      .attr('x', -30)
      .attr('y', -radius * 0.15 + 82)
      .attr('width', 60)
      .attr('height', 18)
      .attr('rx', 9)
      .attr('fill', conf.bg);

    g.append('text')
      .attr('x', 0)
      .attr('y', -radius * 0.15 + 94)
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle')
      .attr('class', 'text-[10px] font-semibold')
      .attr('fill', conf.color)
      .text(`Достоверность: ${conf.label}`);

  }, [roiPercent, npvMillions, paybackMonths, confidence, minValue, maxValue, size]);

  return (
    <div className="flex flex-col items-center">
      <svg ref={svgRef} className="w-full max-w-md" />
    </div>
  );
}