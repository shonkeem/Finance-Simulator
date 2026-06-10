export interface SimulationStateResponse {
  date: string;
  cash: number;
  investments: Record<string, number>;
  debts: Record<string, number>;
  income: number;
  expenses: number;
  net_worth: number;
}
