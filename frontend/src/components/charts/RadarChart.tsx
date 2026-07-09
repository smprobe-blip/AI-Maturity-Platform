import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface RadarDataPoint {
  axis: string;
  key: string;
  current: number;
  target: number;
  benchmark: number;
  weight: number;
}

interface RadarChartProps {
  data: RadarDataPoint[];
  width?: number;
  height?: number;
}

export const RadarChart: React.FC<RadarChartProps> = ({
  data,
  width = 500,
  height = 500,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !data || data.length === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const margin = 80;
    const radius = Math.min(width, height) / 2 - margin;
    const levels = 5;
    const angleSlice = (Math.PI * 2) / data.length;

    const g = svg
      .append('g')
      .attr('transform', `translate(${width / 2}, ${height / 2})`);

    // Background circles (grid)
    for (let level = 1; level <= levels; level++) {
      g.append('circle')
        .attr('r', (radius / levels) * level)
        .style('fill', 'none')
        .style('stroke', '#e5e7eb')
        .style('stroke-width', '1px')
        .style('stroke-dasharray', level === levels ? '0' : '3,3');
    }

    // Axes
    const axisGrid = g.append('g').attr('class', 'axis');
    axisGrid
      .selectAll('.axis-line')
      .data(data)
      .enter()
      .append('line')
      .attr('x1', 0)
      .attr('y1', 0)
      .attr('x2', (d, i) => radius * Math.cos(angleSlice * i - Math.PI / 2))
      .attr('y2', (d, i) => radius * Math.sin(angleSlice * i - Math.PI / 2))
      .style('stroke', '#e5e7eb')
      .style('stroke-width', '1px');

    // Labels
    axisGrid
      .selectAll('.label')
      .data(data)
      .enter()
      .append('text')
      .attr('class', 'label')
      .attr('text-anchor', 'middle')
      .attr('dy', '0.35em')
      .attr('x', (d, i) => (radius + 30) * Math.cos(angleSlice * i - Math.PI / 2))
      .attr('y', (d, i) => (radius + 30) * Math.sin(angleSlice * i - Math.PI / 2))
      .text((d) => d.axis)
      .style('font-size', '12px')
      .style('font-weight', '600')
      .style('fill', '#374151');

    // Helper function to create radar line
    const createRadarLine = (getValue: (d: RadarDataPoint) => number) => {
      return d3
        .lineRadial<RadarDataPoint>()
        .radius((d) => (getValue(d) / 5) * radius)
        .angle((d, i) => i * angleSlice)
        .curve(d3.curveLinearClosed);
    };

    // 1. Benchmark layer (green) - bottom
    const benchmarkLine = createRadarLine((d) => d.benchmark);
    g.append('path')
      .datum(data)
      .attr('class', 'radar-benchmark')
      .attr('d', benchmarkLine as any)
      .style('fill', '#10b981')
      .style('fill-opacity', 0.15)
      .style('stroke', '#10b981')
      .style('stroke-width', '2px')
      .style('stroke-dasharray', '5,3');

    // 2. Target layer (orange) - middle
    const targetLine = createRadarLine((d) => d.target);
    g.append('path')
      .datum(data)
      .attr('class', 'radar-target')
      .attr('d', targetLine as any)
      .style('fill', '#f59e0b')
      .style('fill-opacity', 0.2)
      .style('stroke', '#f59e0b')
      .style('stroke-width', '2px')
      .style('stroke-dasharray', '4,2');

    // 3. Current layer (blue) - top
    const currentLine = createRadarLine((d) => d.current);
    g.append('path')
      .datum(data)
      .attr('class', 'radar-current')
      .attr('d', currentLine as any)
      .style('fill', '#3b82f6')
      .style('fill-opacity', 0.3)
      .style('stroke', '#3b82f6')
      .style('stroke-width', '2.5px');

    // Data points for current
    g.selectAll('.dot-current')
      .data(data)
      .enter()
      .append('circle')
      .attr('class', 'dot-current')
      .attr('r', 6)
      .attr('cx', (d, i) => (d.current / 5) * radius * Math.cos(angleSlice * i - Math.PI / 2))
      .attr('cy', (d, i) => (d.current / 5) * radius * Math.sin(angleSlice * i - Math.PI / 2))
      .style('fill', '#3b82f6')
      .style('stroke', '#fff')
      .style('stroke-width', '2px');

    // Score labels for current
    g.selectAll('.score-label')
      .data(data)
      .enter()
      .append('text')
      .attr('class', 'score-label')
      .attr('text-anchor', 'middle')
      .attr('dy', '-12px')
      .attr('x', (d, i) => (d.current / 5) * radius * Math.cos(angleSlice * i - Math.PI / 2))
      .attr('y', (d, i) => (d.current / 5) * radius * Math.sin(angleSlice * i - Math.PI / 2))
      .text((d) => d.current.toFixed(1))
      .style('font-size', '12px')
      .style('font-weight', 'bold')
      .style('fill', '#1e40af');

  }, [data, width, height]);

  if (!data || data.length === 0) {
    return (
      <div className="flex justify-center items-center" style={{ width, height }}>
        <div className="text-gray-400 text-center">
          <p className="text-sm">Нет данных для отображения</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-center">
      <svg ref={svgRef} width={width} height={height} />
    </div>
  );
};