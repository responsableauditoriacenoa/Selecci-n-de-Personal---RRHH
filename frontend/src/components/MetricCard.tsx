import type { LucideIcon } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: number | string;
  icon?: LucideIcon;
  color?: "blue" | "green" | "yellow" | "red";
}

export const MetricCard = ({ title, value, icon: Icon, color = "blue" }: MetricCardProps) => (
  <article className="metric-card">
    {Icon && (
      <div className={`metric-icon ${color}`}>
        <Icon size={20} strokeWidth={2} />
      </div>
    )}
    <div className="metric-body">
      <div className="metric-label">{title}</div>
      <div className="metric-value">{value}</div>
    </div>
  </article>
);
