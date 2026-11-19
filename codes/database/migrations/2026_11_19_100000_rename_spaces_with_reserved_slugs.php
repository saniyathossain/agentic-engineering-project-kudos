<?php

declare(strict_types=1);

use App\Services\SlugGenerator;
use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class () extends Migration {
    /** Names the application now owns (probes, status pages, client logs...) can no longer be a space's public slug. */
    public function up(): void
    {
        foreach (DB::table('spaces')->whereIn('slug', SlugGenerator::RESERVED)->get(['id', 'slug']) as $space) {
            $slug = $space->slug.'-space';
            $suffix = 2;
            while (DB::table('spaces')->where('slug', $slug)->exists()) {
                $slug = $space->slug.'-space-'.$suffix++;
            }
            DB::table('spaces')->where('id', $space->id)->update(['slug' => $slug]);
        }
    }

    public function down(): void
    {
        // renaming back would risk collisions with the reserved names; the new slugs stay
    }
};
