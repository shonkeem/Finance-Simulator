import { useState } from "react";
import type { SimulationStateResponse } from "./types";
import TimelineChart from "./components/TimelineChart";

function App() {
  const [timeline, setTimeline] = useState<SimulationStateResponse[] | null>(
    null,
  );

  const runSimulation = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          framing: {
            label: "My base case scenario",
            start_date: "2025-01-01",
            end_date: "2034-12-01",
            time_step: "monthly",
          },
          loads: {
            income: [
              {
                name: "primary_salary",
                monthly_gross: 7500.00,
                annual_growth_rate: 0.03,
                start_date: "2025-01-01",
                end_date: null,
              },
            ],
            expenses: [
              {
                name: "rent",
                monthly_amount: 1800.00,
                category: "housing",
                inflation_linked: true,
                start_date: "2025-01-01",
                end_date: null,
              },
              {
                name: "groceries",
                monthly_amount: 400.00,
                category: "food",
                inflation_linked: true,
                start_date: "2025-01-01",
                end_date: null,
              },
            ],
            debts: [
              {
                name: "student_loans",
                current_balance: 28000.00,
                annual_interest_rate: 0.055,
                minimum_monthly_payment: 295.00,
                extra_monthly_payment: 200.00,
                start_date: "2025-01-01",
                end_date: null,
              },
            ],
            investments: [
              {
                name: "401k",
                account_type: "401k",
                current_balance: 15000.00,
                monthly_contribution: 500.00,
                annual_return: 0.07,
                start_date: "2025-01-01",
                end_date: null,
              },
            ],
          },
          settings: {
            inflation_rate: 0.03,
            income_tax_rate: 0.22,
            apply_income_tax: true,
            apply_inflation_to_expenses: true,
            starting_cash: 5000.00,
          },
        }),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const result = await response.json();
      setTimeline(result.timeline);
    } catch (error) {
      console.log(error);
    }
  };
  return (
    <>
      <button onClick={runSimulation}>Run Simulation</button>
      {timeline !== null && <TimelineChart timeline={timeline} />}
    </>
  );
}

export default App;
