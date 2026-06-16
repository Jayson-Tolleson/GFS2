export type BudgetTier = 'global' | 'regional' | 'local';

export interface RenderBudget { tier: BudgetTier; clouds: number; rain: number; ocean: number; reports: number; }

export function budgetForTier(tier: BudgetTier): RenderBudget {
  if (tier === 'local') return { tier, clouds: 56, rain: 72, ocean: 64, reports: 40 };
  if (tier === 'regional') return { tier, clouds: 32, rain: 40, ocean: 36, reports: 24 };
  return { tier, clouds: 16, rain: 20, ocean: 18, reports: 12 };
}
