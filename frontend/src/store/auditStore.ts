/**
 * Zustand store for audit state management.
 * v1.1 — Priority 1: nested responses, report type, target scores.
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { CalculatedIndices } from '@/types';

export interface AuditProfile {
  industry: string;
  size: 'small' | 'medium' | 'large' | 'enterprise';
  email: string;
  name?: string;
  reportType: 'express' | 'executive' | 'comprehensive';
}

/**
 * Responses structure (Priority 1):
 * {
 *   '1': { '1': 4, '2': 3, '3': 5, '4': 2, '5': 4 },  // Strategy (5 questions)
 *   '2': { '1': 3, '2': 4, ... },                       // People
 *   ...
 *   '7': { ... }                                        // R&D
 * }
 */
export type NestedResponses = Record<string, Record<string, number>>;
export type TargetScores = Record<string, number>;

interface AuditState {
  // Core state
  auditId: string | null;
  calculatedIndices: CalculatedIndices | null;
  profile: AuditProfile | null;
  responses: NestedResponses;
  targetScores: TargetScores | null;

  // UI state
  activeDimensionId: string | null;
  showTargetInput: boolean;

  // Actions: profile
  setProfile: (profile: AuditProfile) => void;
  updateProfile: (patch: Partial<AuditProfile>) => void;

  // Actions: responses (nested format)
  setResponses: (responses: NestedResponses) => void;
  setQuestionScore: (dimId: string, qId: string, score: number) => void;
  clearDimensionResponses: (dimId: string) => void;

  // Actions: target scores (for gap analysis)
  setTargetScores: (scores: TargetScores | null) => void;
  updateTargetScore: (dimId: string, score: number) => void;
  setShowTargetInput: (show: boolean) => void;

  // Actions: results
  setResults: (auditId: string, indices: CalculatedIndices) => void;

  // Actions: UI
  setActiveDimension: (dimId: string | null) => void;

  // Actions: reset
  reset: () => void;

  // Selectors (computed)
  getDimensionAverage: (dimId: string) => number;
  isDimensionComplete: (dimId: string, questionCount: number) => boolean;
  getOverallProgress: (totalQuestions: number) => number;
}

const initialState = {
  auditId: null as string | null,
  calculatedIndices: null as CalculatedIndices | null,
  profile: null as AuditProfile | null,
  responses: {} as NestedResponses,
  targetScores: null as TargetScores | null,
  activeDimensionId: null as string | null,
  showTargetInput: false,
};

export const useAuditStore = create<AuditState>()(
  persist(
    (set, get) => ({
      ...initialState,

      // === Profile ===
      setProfile: (profile) => set({ profile }),

      updateProfile: (patch) =>
        set((state) => ({
          profile: state.profile ? { ...state.profile, ...patch } : null,
        })),

      // === Responses (nested) ===
      setResponses: (responses) => set({ responses }),

      setQuestionScore: (dimId, qId, score) =>
        set((state) => ({
          responses: {
            ...state.responses,
            [dimId]: {
              ...(state.responses[dimId] || {}),
              [qId]: score,
            },
          },
        })),

      clearDimensionResponses: (dimId) =>
        set((state) => {
          const newResponses = { ...state.responses };
          delete newResponses[dimId];
          return { responses: newResponses };
        }),

      // === Target scores ===
      setTargetScores: (scores) => set({ targetScores: scores }),

      updateTargetScore: (dimId, score) =>
        set((state) => ({
          targetScores: {
            ...(state.targetScores || {}),
            [dimId]: score,
          },
        })),

      setShowTargetInput: (show) => set({ showTargetInput: show }),

      // === Results ===
      setResults: (auditId, indices) => set({ auditId, calculatedIndices: indices }),

      // === UI ===
      setActiveDimension: (dimId) => set({ activeDimensionId: dimId }),

      // === Reset ===
      reset: () => set(initialState),

      // === Selectors ===
      getDimensionAverage: (dimId) => {
        const dimResponses = get().responses[dimId];
        if (!dimResponses) return 0;
        const scores = Object.values(dimResponses).filter((v) => v > 0);
        if (scores.length === 0) return 0;
        return scores.reduce((a, b) => a + b, 0) / scores.length;
      },

      isDimensionComplete: (dimId, questionCount) => {
        const dimResponses = get().responses[dimId];
        if (!dimResponses) return false;
        const answeredCount = Object.values(dimResponses).filter((v) => v > 0).length;
        return answeredCount >= questionCount;
      },

      getOverallProgress: (totalQuestions) => {
        const responses = get().responses;
        let answeredCount = 0;
        Object.values(responses).forEach((dimResponses) => {
          answeredCount += Object.values(dimResponses).filter((v) => v > 0).length;
        });
        return totalQuestions > 0 ? answeredCount / totalQuestions : 0;
      },
    }),
    {
      name: 'ai-maturity-audit-v2', // v2 to avoid conflict with old flat format
      version: 2,
      partialize: (state) => ({
        // Persist only essential data, not UI state
        profile: state.profile,
        responses: state.responses,
        targetScores: state.targetScores,
        auditId: state.auditId,
        calculatedIndices: state.calculatedIndices,
      }),
    }
  )
);