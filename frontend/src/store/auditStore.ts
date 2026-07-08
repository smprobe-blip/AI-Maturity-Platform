import { create } from 'zustand';
import type { CompanyProfile, ContactInfo, RawResponse, CalculatedIndices } from '@/types';

interface AuditState {
  // Company profile
  companyProfile: CompanyProfile | null;
  setCompanyProfile: (profile: CompanyProfile) => void;

  // Contact info
  contactInfo: ContactInfo | null;
  setContactInfo: (contact: ContactInfo) => void;

  // Raw responses
  rawResponses: RawResponse[];
  setRawResponse: (dimensionId: number, questionId: number, score: number) => void;
  clearResponses: () => void;

  // Results
  auditId: string | null;
  calculatedIndices: CalculatedIndices | null;
  setResults: (auditId: string, indices: CalculatedIndices) => void;

  // Reset
  reset: () => void;
}

export const useAuditStore = create<AuditState>((set) => ({
  // Initial state
  companyProfile: null,
  contactInfo: null,
  rawResponses: [],
  auditId: null,
  calculatedIndices: null,

  // Actions
  setCompanyProfile: (profile) => set({ companyProfile: profile }),

  setContactInfo: (contact) => set({ contactInfo: contact }),

  setRawResponse: (dimensionId, questionId, score) =>
    set((state) => {
      const existingIndex = state.rawResponses.findIndex(
        (r) => r.dimension_id === dimensionId && r.question_id === questionId
      );

      const newResponse: RawResponse = {
        dimension_id: dimensionId,
        question_id: questionId,
        score,
        time_to_answer_sec: undefined,
        confidence_level: undefined,
      };

      if (existingIndex >= 0) {
        const updated = [...state.rawResponses];
        updated[existingIndex] = newResponse;
        return { rawResponses: updated };
      } else {
        return { rawResponses: [...state.rawResponses, newResponse] };
      }
    }),

  clearResponses: () => set({ rawResponses: [] }),

  setResults: (auditId, indices) => set({ auditId, calculatedIndices: indices }),

  reset: () =>
    set({
      companyProfile: null,
      contactInfo: null,
      rawResponses: [],
      auditId: null,
      calculatedIndices: null,
    }),
}));