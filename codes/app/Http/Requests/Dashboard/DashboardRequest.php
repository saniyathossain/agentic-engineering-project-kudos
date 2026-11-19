<?php

declare(strict_types=1);

namespace App\Http\Requests\Dashboard;

use App\Enums\DateRange;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

final class DashboardRequest extends FormRequest
{
    /** @return array<string, array<int, mixed>> */
    public function rules(): array
    {
        return [
            'range' => ['nullable', Rule::enum(DateRange::class)],
        ];
    }

    public function range(): DateRange
    {
        return DateRange::tryFrom((int) $this->validated('range', DateRange::Month->value)) ?? DateRange::Month;
    }
}
