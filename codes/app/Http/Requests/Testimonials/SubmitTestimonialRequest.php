<?php

declare(strict_types=1);

namespace App\Http\Requests\Testimonials;

use App\Data\Testimonials\SubmissionData;
use App\Enums\OptionalField;
use App\Models\Space;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Http\UploadedFile;

final class SubmitTestimonialRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    /** @return array<string, list<string|object>> */
    public function rules(): array
    {
        $space = $this->space();

        $rules = [
            'name' => ['required', 'string', 'max:100'],
            'email' => ['required', 'email:rfc', 'max:190'],
            'body' => ['required', 'string', 'min:3', 'max:2000'],
            'consent' => ['accepted'],
            'rating' => $space->collect_rating
                ? ['required', 'integer', 'between:1,5']
                : ['prohibited'],
        ];

        $rules['company'] = $this->optionalRule($space, OptionalField::Company, ['string', 'max:100']);
        $rules['title'] = $this->optionalRule($space, OptionalField::Title, ['string', 'max:100']);
        $rules['social_link'] = $this->optionalRule($space, OptionalField::SocialLink, ['url:http,https', 'max:255']);
        $rules['photo'] = $this->optionalRule($space, OptionalField::Photo, ['image', 'mimes:png,jpg,jpeg,webp', 'max:2048']);

        return $rules;
    }

    public function toData(): SubmissionData
    {
        $photo = $this->file('photo');

        return SubmissionData::fromValidated(
            $this->validated(),
            $photo instanceof UploadedFile ? $photo : null,
        );
    }

    private function space(): Space
    {
        /** @var Space $space */
        $space = $this->route('space');

        return $space;
    }

    /**
     * @param  list<string>  $typeRules
     * @return list<string>
     */
    private function optionalRule(Space $space, OptionalField $field, array $typeRules): array
    {
        $config = $space->fieldConfig($field);
        if (! $config->enabled) {
            return ['prohibited'];
        }

        return [$config->required ? 'required' : 'nullable', ...$typeRules];
    }
}
