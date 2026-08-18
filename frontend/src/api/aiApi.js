import { apiGet } from "./apiClient"

export async function getStockAIImpact() {
  return apiGet("/stock/ai-impact")
}