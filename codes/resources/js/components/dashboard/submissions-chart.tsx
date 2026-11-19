import { type DailyCount } from '@/types';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

interface SubmissionsChartProps {
    series: DailyCount[];
}

const shortDate = (iso: string): string => iso.slice(5);

export default function SubmissionsChart({ series }: SubmissionsChartProps) {
    return (
        <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={series} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
                    <XAxis dataKey="date" tickFormatter={shortDate} tickLine={false} axisLine={false} minTickGap={24} fontSize={12} />
                    <YAxis allowDecimals={false} tickLine={false} axisLine={false} fontSize={12} />
                    <Tooltip cursor={{ fill: 'var(--muted)' }} />
                    <Bar dataKey="count" name="Testimonials" fill="var(--chart-1)" radius={[4, 4, 0, 0]} />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}
