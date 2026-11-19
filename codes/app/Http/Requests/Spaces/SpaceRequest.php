<?php

declare(strict_types=1);

namespace App\Http\Requests\Spaces;

use App\Data\Spaces\SpaceData;
use App\Enums\OptionalField;
use App\Enums\SpaceTheme;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Http\UploadedFile;
use Illuminate\Validation\Rule;

final class SpaceRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    /** @return array<string, list<string|object>> */
    public function rules(): array
    {
        $rules = [
            'name' => ['required', 'string', 'max:80'],
            'header_title' => ['required', 'string', 'max:120'],
            'message' => ['required', 'string', 'max:1000'],
            'collect_rating' => ['boolean'],
            'theme' => ['required', Rule::enum(SpaceTheme::class)],
            'is_accepting' => ['boolean'],
            'logo' => ['nullable', 'image', 'mimes:png,jpg,jpeg,webp', 'max:2048'],
            'fields' => ['array'],
        ];

        foreach (OptionalField::values() as $field) {
            $rules["fields.$field.enabled"] = ['boolean'];
            $rules["fields.$field.required"] = ['boolean'];
        }

        return $rules;
    }

    public function toData(): SpaceData
    {
        $logo = $this->file('logo');

        return SpaceData::fromValidated(
            $this->validated(),
            $logo instanceof UploadedFile ? $logo : null,
        );
    }
}
