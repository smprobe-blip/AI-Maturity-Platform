import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Badge, getMaturityBadgeVariant } from '../Badge';

describe('Badge', () => {
  it('renders children', () => {
    render(<Badge>Test</Badge>);
    expect(screen.getByText('Test')).toBeInTheDocument();
  });

  it('applies variant classes', () => {
    const { container } = render(<Badge variant="success">OK</Badge>);
    expect(container.firstChild).toHaveClass('bg-green-100');
  });
});

describe('getMaturityBadgeVariant', () => {
  it('returns correct variant for each level', () => {
    expect(getMaturityBadgeVariant('L1 — Initial')).toBe('danger');
    expect(getMaturityBadgeVariant('L2 — Developing')).toBe('warning');
    expect(getMaturityBadgeVariant('L3 — Defined')).toBe('info');
    expect(getMaturityBadgeVariant('L4 — Managed')).toBe('success');
    expect(getMaturityBadgeVariant('L5 — Optimizing')).toBe('success');
  });
});