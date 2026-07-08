import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Table } from '../Table';

describe('Table', () => {
  const columns = [
    { key: 'name', header: 'Name' },
    { key: 'email', header: 'Email' },
  ];

  const data = [
    { id: '1', name: 'Alice', email: 'alice@example.com' },
    { id: '2', name: 'Bob', email: 'bob@example.com' },
  ];

  it('renders table with data', () => {
    render(
      <Table columns={columns} data={data} keyExtractor={(i) => i.id} />
    );
    expect(screen.getByText('Alice')).toBeInTheDocument();
    expect(screen.getByText('bob@example.com')).toBeInTheDocument();
  });

  it('shows empty message when no data', () => {
    render(
      <Table
        columns={columns}
        data={[]}
        keyExtractor={(i: any) => i.id}
        emptyMessage="Nothing here"
      />
    );
    expect(screen.getByText('Nothing here')).toBeInTheDocument();
  });

  it('calls onRowClick when row clicked', () => {
    const onClick = vi.fn();
    render(
      <Table
        columns={columns}
        data={data}
        keyExtractor={(i) => i.id}
        onRowClick={onClick}
      />
    );
    fireEvent.click(screen.getByText('Alice'));
    expect(onClick).toHaveBeenCalledWith(data[0]);
  });

  it('shows loading state', () => {
    render(
      <Table
        columns={columns}
        data={[]}
        keyExtractor={(i: any) => i.id}
        isLoading
      />
    );
    expect(document.querySelector('.animate-spin')).toBeInTheDocument();
  });
});