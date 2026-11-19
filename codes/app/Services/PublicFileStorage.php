<?php

declare(strict_types=1);

namespace App\Services;

use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Storage;

final class PublicFileStorage
{
    private const DISK = 'public';

    public function store(UploadedFile $file, string $directory): string
    {
        return (string) $file->store($directory, self::DISK);
    }

    public function replace(?string $oldPath, UploadedFile $file, string $directory): string
    {
        $this->delete($oldPath);

        return $this->store($file, $directory);
    }

    public function delete(?string $path): void
    {
        if ($path === null || $path === '') {
            return;
        }

        Storage::disk(self::DISK)->delete($path);
    }

    public function url(?string $path): ?string
    {
        if ($path === null || $path === '') {
            return null;
        }

        return Storage::disk(self::DISK)->url($path);
    }
}
