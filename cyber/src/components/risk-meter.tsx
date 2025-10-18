import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

interface RiskMeterProps {
  score: number;
  level: string;
}

export function RiskMeter({ score, level }: RiskMeterProps) {
  // Ensure score is a valid number
  const validScore = typeof score === 'number' && !isNaN(score) ? score : 0;
  
  const getRiskColorClass = (s: number) => {
    if (s >= 70) return "text-destructive";
    if (s >= 40) return "text-accent";
    return "text-foreground";
  };
  
  const getRiskBgClass = (s: number) => {
    if (s >= 70) return "bg-destructive/10 text-destructive";
    if (s >= 40) return "bg-accent/10 text-accent";
    return "bg-secondary text-secondary-foreground";
  };
  
  const getProgressColorClass = (s: number) => {
    if (s >= 70) return "bg-destructive";
    if (s >= 40) return "bg-accent";
    return "bg-primary";
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex justify-between items-center">
        <div className="flex items-baseline gap-2">
            <span className={cn("text-4xl font-bold tracking-tighter", getRiskColorClass(validScore))}>
                {validScore}
            </span>
            <span className="text-muted-foreground">/ 100</span>
        </div>
        <span className={cn("font-semibold px-3 py-1 rounded-full text-sm", getRiskBgClass(validScore))}>
            {level} Risk
        </span>
      </div>
      <Progress value={validScore} className="h-2" indicatorClassName={getProgressColorClass(validScore)} />
    </div>
  );
}
