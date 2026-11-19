<?php

declare(strict_types=1);

namespace App\Http\Requests\Testimonials;

use Illuminate\Foundation\Http\FormRequest;

final class EditTestimonialRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    /** @return array<string, list<string>> */
    public function rules(): array
    {
        return ['body' => ['required', 'string', 'min:3', 'max:2000']];
    }

    public function body(): string
    {
        return (string) $this->validated('body');
    }
}
