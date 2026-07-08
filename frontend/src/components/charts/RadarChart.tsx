import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface RadarChartProps {
  dimensionScores: Record<string, number>;
  width?: number;
  height?: number;
}

export const RadarChart: React.FC<RadarChartProps> = ({
  dimensionScores,
  width = 400,
  height = 400,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const margin = 60;
    const radius = Math.min(width, height) / 2 - margin;
    const levels = 5;
    const angleSlice = (Math.PI * 2) / Object.keys(dimensionScores).length;

    const dimensionNames: Record<string, string> = {
      '1': 'Strategy',
      '2': 'Data',
      '3': 'Technology',
      '4': 'Processes',
      '5': 'People',
      '6': 'Culture',
      '7': 'Ethics',
    };

    const data = Object.entries(dimensionScores).map(([dimId, score]) => ({
      axis: dimensionNames[dimId] || `Dim ${dimId}`,
      value: score,
    }));

    const g = svg
      .append('g')
      .attr('transform', `translate(${width / 2}, ${height / 2})`);

    // Background circles
    for (let level = 1; level <= levels; level++) {
      g.append('circle')
        .attr('r', (radius / levels) * level)
        .style('fill', 'none')
        .style('stroke', '#e5e7eb')
        .style('stroke-width', '1px');
    }

    // Axes
    const axisGrid = g.append('g').attr('class', 'axis');

    axisGrid
      .selectAll('.axis')
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
      .attr('x', (d, i) => (radius + 20) * Math.cos(angleSlice * i - Math.PI / 2))
      .attr('y', (d, i) => (radius + 20) * Math.sin(angleSlice * i - Math.PI / 2))
      .text((d) => d.axis)
      .style('font-size', '12px')
      .style('font-weight', '600')
      .style('fill', '#374151');

    // Data area
    const radarLine = d3
      .lineRadial<any>()
      .radius((d) => (d.value / 5) * radius)
      .angle((d, i) => i * angleSlice)
      .curve(d3.curveLinearClosed);

    g.append('path')
      .datum(data)
      .attr('class', 'radar-area')
      .attr('d', radarLine as any)
      .style('fill', '#3b82f6')
      .style('fill-opacity', 0.3)
      .style('stroke', '#3b82f6')
      .style('stroke-width', '2px');

    // Data points
    g.selectAll('.dot')
      .data(data)
      .enter()
      .append('circle')
      .attr('class', 'dot')
      .attr('r', 5)
      .attr('cx', (d, i) => (d.value / 5) * radius * Math.cos(angleSlice * i - Math.PI / 2))
      .attr('cy', (d, i) => (d.value / 5) * radius * Math.sin(angleSlice * i - Math.PI / 2))
      .style('fill', '#3b82f6')
      .style('stroke', '#fff')
      .style('stroke-width', '2px');

    // Score labels
    g.selectAll('.score-label')
      .data(data)
      .enter()
      .append('text')
      .attr('class', 'score-label')
      .attr('text-anchor', 'middle')
      .attr('dy', '-10px')
      .attr('x', (d, i) => (d.value / 5) * radius * Math.cos(angleSlice * i - Math.PI / 2))
      .attr('y', (d, i) => (d.value / 5) * radius * Math.sin(angleSlice * i - Math.PI / 2))
      .text((d) => d.value.toFixed(1))
      .style('font-size', '11px')
      .style('font-weight', 'bold')
      .style('fill', '#1e40af');
  }, [dimensionScores, width, height]);

  return (
    <div className="flex justify-center">
      <svg ref={svgRef} width={width} height={height} />
    </div>
  );
};