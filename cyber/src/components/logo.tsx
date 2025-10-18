import { ShieldHalf } from 'lucide-react';
import { cn } from '@/lib/utils';

export function Logo() {
  return (
    <div className="flex items-center gap-2.5 px-2 group/logo">
      <div className="p-2 bg-primary/10 rounded-lg border border-primary/20">
        <ShieldHalf className="h-6 w-6 text-primary" />
      </div>
      <div className="overflow-hidden">
        <h1 className="text-base font-semibold text-foreground whitespace-nowrap group-data-[collapsible=icon]:-translate-x-12 transition-transform duration-300">
          Narcotics Intelligence
        </h1>
        <p className="text-xs text-muted-foreground whitespace-nowrap group-data-[collapsible=icon]:-translate-x-12 transition-transform duration-300">
          Platform
        </p>
      </div>
    </div>
  );
}
