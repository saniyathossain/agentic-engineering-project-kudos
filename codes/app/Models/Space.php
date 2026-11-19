<?php

declare(strict_types=1);

namespace App\Models;

use App\Data\Spaces\FieldConfigData;
use App\Enums\OptionalField;
use App\Enums\SpaceTheme;
use App\Enums\TestimonialStatus;
use Illuminate\Database\Eloquent\Concerns\HasUlids;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

/**
 * @property int $id
 * @property string $public_id
 * @property int $user_id
 * @property string $name
 * @property string $slug
 * @property string|null $logo_path
 * @property string $header_title
 * @property string $message
 * @property bool $collect_rating
 * @property SpaceTheme $theme
 * @property array<string, array{enabled: bool, required: bool}> $fields
 * @property bool $is_accepting
 */
final class Space extends Model
{
    /** @use HasFactory<\Database\Factories\SpaceFactory> */
    use HasFactory;
    use HasUlids;

    protected $fillable = [
        'name', 'slug', 'logo_path', 'header_title', 'message',
        'collect_rating', 'theme', 'fields', 'is_accepting',
    ];

    /** @return list<string> */
    public function uniqueIds(): array
    {
        return ['public_id'];
    }

    /** @return array<string, string> */
    protected function casts(): array
    {
        return [
            'collect_rating' => 'boolean',
            'theme' => SpaceTheme::class,
            'fields' => 'array',
            'is_accepting' => 'boolean',
        ];
    }

    /** @return BelongsTo<User, $this> */
    public function owner(): BelongsTo
    {
        return $this->belongsTo(User::class, 'user_id');
    }

    /** @return HasMany<Testimonial, $this> */
    public function testimonials(): HasMany
    {
        return $this->hasMany(Testimonial::class);
    }

    /** @return HasMany<Testimonial, $this> */
    public function publishedTestimonials(): HasMany
    {
        return $this->testimonials()->where('status', TestimonialStatus::Published->value);
    }

    public function fieldConfig(OptionalField $field): FieldConfigData
    {
        return FieldConfigData::fromArray($this->fields[$field->value] ?? []);
    }

    public function getRouteKeyName(): string
    {
        return 'public_id';
    }
}
