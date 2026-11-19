import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface StatCardProps {
    label: string;
    value: string | number;
    hint?: string;
}

export default function StatCard({ label, value, hint }: StatCardProps) {
    return (
        <Card>
            <CardHeader className="pb-2">
                <CardDescription>{label}</CardDescription>
                <CardTitle className="text-3xl tabular-nums">{value}</CardTitle>
            </CardHeader>
            {hint && (
                <CardContent>
                    <p className="text-muted-foreground text-xs">{hint}</p>
                </CardContent>
            )}
        </Card>
    );
}
