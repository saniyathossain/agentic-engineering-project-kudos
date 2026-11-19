<?php

declare(strict_types=1);

namespace App\Http\Requests\Spaces;

use App\Data\Testimonials\InboxQueryData;
use App\Enums\InboxFilter;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

final class InboxRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    /** @return array<string, list<string|object>> */
    public function rules(): array
    {
        return [
            'filter' => ['nullable', Rule::enum(InboxFilter::class)],
            'from' => ['nullable', 'date_format:Y-m-d'],
            'to' => ['nullable', 'date_format:Y-m-d', 'after_or_equal:from'],
        ];
    }

    public function toData(): InboxQueryData
    {
        return InboxQueryData::fromValidated($this->validated());
    }
}
