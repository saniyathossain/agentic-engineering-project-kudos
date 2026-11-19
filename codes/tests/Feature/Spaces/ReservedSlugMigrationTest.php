<?php

declare(strict_types=1);

namespace Tests\Feature\Spaces;

use App\Models\Space;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

final class ReservedSlugMigrationTest extends TestCase
{
    use RefreshDatabase;

    public function test_spaces_with_newly_reserved_slugs_are_renamed(): void
    {
        $status = Space::factory()->create(['slug' => 'status']);
        $second = Space::factory()->create(['slug' => 'livez']);
        Space::factory()->create(['slug' => 'livez-space']);
        $fine = Space::factory()->create(['slug' => 'my-course']);

        (require database_path('migrations/2026_11_19_100000_rename_spaces_with_reserved_slugs.php'))->up();

        $this->assertSame('status-space', $status->refresh()->slug);
        $this->assertSame('livez-space-2', $second->refresh()->slug);
        $this->assertSame('my-course', $fine->refresh()->slug);
    }
}
