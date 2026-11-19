<?php

declare(strict_types=1);

namespace App\Models;

use App\Enums\TestimonialStatus;
use Illuminate\Database\Eloquent\Concerns\HasUlids;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Support\Carbon;

/**
 * @property int $id
 * @property string $public_id
 * @property int $space_id
 * @property int|null $rating
 * @property string $body
 * @property string $respondent_name
 * @property string $respondent_email
 * @property string|null $company
 * @property string|null $title
 * @property string|null $social_link
 * @property string|null $photo_path
 * @property bool $consent
 * @property TestimonialStatus $status
 * @property bool $is_favorite
 * @property Carbon $submitted_at
 */
final class Testimonial extends Model
{
    /** @use HasFactory<\Database\Factories\TestimonialFactory> */
    use HasFactory;
    use HasUlids;

    protected $fillable = [
        'rating', 'body', 'respondent_name', 'respondent_email', 'company', 'title',
        'social_link', 'photo_path', 'consent', 'status', 'is_favorite', 'submitted_at',
    ];

    /** @var list<string> */
    protected $hidden = ['respondent_email'];

    /** @return list<string> */
    public function uniqueIds(): array
    {
        return ['public_id'];
    }

    /** @return array<string, string> */
    protected function casts(): array
    {
        return [
            'status' => TestimonialStatus::class,
            'consent' => 'boolean',
            'is_favorite' => 'boolean',
            'rating' => 'integer',
            'submitted_at' => 'datetime',
        ];
    }

    /** @return BelongsTo<Space, $this> */
    public function space(): BelongsTo
    {
        return $this->belongsTo(Space::class);
    }

    public function getRouteKeyName(): string
    {
        return 'public_id';
    }
}
