import { type DailyCount } from '@/types';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

interface SubmissionsChartProps {
    series: DailyCount[];
}

const shortDate = (iso: string): string => iso.slice(5);

const TOOLTIP_STYLE = {
    background: 'var(--popover)',
    border: '1px solid var(--border)',
    borderRadius: 12,
    boxShadow: 'var(--sh-md)',
    color: 'var(--popover-foreground)',
    fontSize: 13,
} as const;

export default function SubmissionsChart({ series }: SubmissionsChartProps) {
    return (
        <div className="h-64 w-full" role="img" aria-label="Testimonials collected per day">
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={series} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="2 6" vertical={false} stroke="var(--border)" />
                    <XAxis
                        dataKey="date"
                        tickFormatter={shortDate}
                        tickLine={false}
                        axisLine={false}
                        minTickGap={28}
                        fontSize={12}
                        tick={{ fill: 'var(--muted-foreground)' }}
                    />
                    <YAxis allowDecimals={false} tickLine={false} axisLine={false} fontSize={12} tick={{ fill: 'var(--muted-foreground)' }} />
                    <Tooltip cursor={{ fill: 'var(--accent)' }} contentStyle={TOOLTIP_STYLE} />
                    <Bar dataKey="count" name="Testimonials" fill="var(--chart-1)" radius={[6, 6, 2, 2]} maxBarSize={28} animationDuration={600} />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}
