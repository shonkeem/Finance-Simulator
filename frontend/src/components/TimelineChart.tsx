import type { SimulationStateResponse } from "../types";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

interface TimelineChartProps {
  timeline: SimulationStateResponse[];
}

export default function TimelineChart({ timeline }: TimelineChartProps) {
  return (
    <LineChart width={400} height={800} data={timeline}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="date" />
      <YAxis />
      <Tooltip />
      <Line type="monotone" dataKey="net_worth" dot={false} stroke="black" />
    </LineChart>
  );
}
