<?php

declare(strict_types=1);

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class () extends Migration {
    public function up(): void
    {
        Schema::create('spaces', function (Blueprint $table): void {
            $table->id();
            $table->ulid('public_id')->unique();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('name');
            $table->string('slug')->unique();
            $table->string('logo_path')->nullable();
            $table->string('header_title');
            $table->text('message');
            $table->boolean('collect_rating')->default(true);
            $table->string('theme')->default('light');
            $table->json('fields');
            $table->boolean('is_accepting')->default(true);
            $table->timestamps();

            $table->index('user_id');
        });

        Schema::create('testimonials', function (Blueprint $table): void {
            $table->id();
            $table->ulid('public_id')->unique();
            $table->foreignId('space_id')->constrained()->cascadeOnDelete();
            $table->unsignedTinyInteger('rating')->nullable();
            $table->text('body');
            $table->string('respondent_name');
            $table->string('respondent_email');
            $table->string('company')->nullable();
            $table->string('title')->nullable();
            $table->string('social_link')->nullable();
            $table->string('photo_path')->nullable();
            $table->boolean('consent')->default(false);
            $table->string('status')->default('pending');
            $table->boolean('is_favorite')->default(false);
            $table->timestamp('submitted_at');
            $table->timestamps();

            $table->index(['space_id', 'submitted_at']);
            $table->index(['space_id', 'status']);
        });

        Schema::table('users', function (Blueprint $table): void {
            $table->timestamp('banner_dismissed_at')->nullable();
        });
    }

    public function down(): void
    {
        Schema::table('users', function (Blueprint $table): void {
            $table->dropColumn('banner_dismissed_at');
        });
        Schema::dropIfExists('testimonials');
        Schema::dropIfExists('spaces');
    }
};
