<?php

declare(strict_types=1);

namespace App\Http\Requests\Testimonials;

use App\Enums\TestimonialStatus;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

final class SetStatusRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    /** @return array<string, list<string|object>> */
    public function rules(): array
    {
        return ['status' => ['required', Rule::enum(TestimonialStatus::class)]];
    }

    public function status(): TestimonialStatus
    {
        return TestimonialStatus::from((string) $this->validated('status'));
    }
}
