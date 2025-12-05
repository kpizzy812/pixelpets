/**
 * Safe number formatting utilities
 * Prevents toFixed errors when value is not a number
 */

export function formatNumber(value: unknown, decimals: number = 2): string {
  // Handle both number and string (Decimal from API comes as string)
  let num = 0;
  if (typeof value === 'number' && !isNaN(value)) {
    num = value;
  } else if (typeof value === 'string') {
    const parsed = parseFloat(value);
    if (!isNaN(parsed)) {
      num = parsed;
    }
  }
  return num.toFixed(decimals);
}

export function formatCurrency(value: unknown, decimals: number = 2): string {
  return formatNumber(value, decimals);
}

export function formatPercent(value: unknown, decimals: number = 0): string {
  const num = typeof value === 'number' && !isNaN(value) ? value : 0;
  return `${num.toFixed(decimals)}%`;
}
