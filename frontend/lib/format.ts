/**
 * Safe number formatting utilities
 * Prevents toFixed errors when value is not a number
 */

export function formatNumber(value: unknown, decimals: number = 2): string {
  const num = typeof value === 'number' && !isNaN(value) ? value : 0;
  return num.toFixed(decimals);
}

export function formatCurrency(value: unknown, decimals: number = 2): string {
  return formatNumber(value, decimals);
}

export function formatPercent(value: unknown, decimals: number = 0): string {
  const num = typeof value === 'number' && !isNaN(value) ? value : 0;
  return `${num.toFixed(decimals)}%`;
}
