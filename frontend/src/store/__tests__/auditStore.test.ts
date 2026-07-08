import { describe, it, expect, beforeEach } from 'vitest';
import { useAuditStore } from '../auditStore';

describe('auditStore', () => {
  beforeEach(() => {
    useAuditStore.getState().reset();
  });

  it('sets company profile', () => {
    const profile = {
      industry: 'Retail',
      company_size: 'Large',
      region: 'Moscow',
    };

    useAuditStore.getState().setCompanyProfile(profile);
    expect(useAuditStore.getState().companyProfile).toEqual(profile);
  });

  it('sets contact info', () => {
    const contact = {
      email: 'test@example.com',
      consent_to_process_data: true,
    };

    useAuditStore.getState().setContactInfo(contact);
    expect(useAuditStore.getState().contactInfo).toEqual(contact);
  });

  it('adds raw response', () => {
    useAuditStore.getState().setRawResponse(1, 1, 4);
    
    const responses = useAuditStore.getState().rawResponses;
    expect(responses).toHaveLength(1);
    expect(responses[0]).toEqual({
      dimension_id: 1,
      question_id: 1,
      score: 4,
      time_to_answer_sec: undefined,
      confidence_level: undefined,
    });
  });

  it('updates existing raw response', () => {
    useAuditStore.getState().setRawResponse(1, 1, 3);
    useAuditStore.getState().setRawResponse(1, 1, 5);
    
    const responses = useAuditStore.getState().rawResponses;
    expect(responses).toHaveLength(1);
    expect(responses[0].score).toBe(5);
  });

  it('resets store', () => {
    useAuditStore.getState().setCompanyProfile({
      industry: 'Retail',
      company_size: 'Large',
      region: 'Moscow',
    });
    
    useAuditStore.getState().reset();
    
    expect(useAuditStore.getState().companyProfile).toBeNull();
    expect(useAuditStore.getState().rawResponses).toHaveLength(0);
  });
});