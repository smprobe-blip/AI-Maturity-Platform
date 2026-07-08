import { test, expect } from '@playwright/test';

test.describe('API Integration Tests', () => {
  test('create express audit via API', async ({ request }) => {
    const response = await request.post('http://localhost:8000/api/v1/public/audits/express', {
      data: {
        company_profile: {
          industry: 'Retail',
          company_size: 'Large (1000+)',
          region: 'Moscow',
        },
        contact: {
          email: 'api-test@example.com',
          name: 'API Test',
          consent_to_process_data: true,
        },
        raw_responses: Array.from({ length: 35 }, (_, i) => ({
          dimension_id: Math.floor(i / 5) + 1,
          question_id: (i % 5) + 1,
          score: 4,
        })),
      },
    });

    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data.audit_id).toBeDefined();
    expect(data.calculated_indices).toBeDefined();
    expect(data.calculated_indices.composite_score).toBeGreaterThan(0);
  });

  test('get audit by ID', async ({ request }) => {
    // Create audit first
    const createResponse = await request.post('http://localhost:8000/api/v1/public/audits/express', {
      data: {
        company_profile: {
          industry: 'Finance',
          company_size: 'Medium (51-250)',
          region: 'Saint Petersburg',
        },
        contact: {
          email: 'get-test@example.com',
          consent_to_process_data: true,
        },
        raw_responses: Array.from({ length: 35 }, (_, i) => ({
          dimension_id: Math.floor(i / 5) + 1,
          question_id: (i % 5) + 1,
          score: 3,
        })),
      },
    });

    const { audit_id } = await createResponse.json();

    // Get audit
    const getResponse = await request.get(`http://localhost:8000/api/v1/public/audits/${audit_id}`);
    
    expect(getResponse.ok()).toBeTruthy();
    
    const audit = await getResponse.json();
    expect(audit.audit_id).toBe(audit_id);
    expect(audit.status).toBe('completed');
  });

  test('get industry benchmark', async ({ request }) => {
    const response = await request.get('http://localhost:8000/api/v1/public/benchmarks/Retail');
    
    expect(response.ok()).toBeTruthy();
    
    const benchmark = await response.json();
    expect(benchmark.industry).toBe('Retail');
    expect(benchmark.average_score).toBeDefined();
  });

  test('health check', async ({ request }) => {
    const response = await request.get('http://localhost:8000/health');
    
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data.status).toBe('healthy');
  });
});