import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { type FieldConfig } from '@/types';

interface OptionalFieldRowProps {
    id: string;
    label: string;
    config: FieldConfig;
    onChange: (config: FieldConfig) => void;
}

export default function OptionalFieldRow({ id, label, config, onChange }: OptionalFieldRowProps) {
    return (
        <div className="flex items-center justify-between rounded-md border p-3">
            <div className="flex items-center gap-2">
                <Checkbox
                    id={`${id}-enabled`}
                    checked={config.enabled}
                    onCheckedChange={(checked) => onChange({ enabled: checked === true, required: checked === true && config.required })}
                />
                <Label htmlFor={`${id}-enabled`}>{label}</Label>
            </div>
            <div className="flex items-center gap-2">
                <Checkbox
                    id={`${id}-required`}
                    checked={config.required}
                    disabled={!config.enabled}
                    onCheckedChange={(checked) => onChange({ ...config, required: checked === true })}
                />
                <Label htmlFor={`${id}-required`} className="text-muted-foreground text-sm font-normal">
                    Required
                </Label>
            </div>
        </div>
    );
}
