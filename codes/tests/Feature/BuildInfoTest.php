<?php

declare(strict_types=1);

namespace Tests\Feature;

use Tests\TestCase;

final class BuildInfoTest extends TestCase
{
    public function test_every_page_carries_build_info_for_the_footer(): void
    {
        config(['observability.version' => '1.4.2', 'observability.commit' => 'abc1234']);

        $this->get('/login')->assertInertia(
            fn ($page) => $page->where('build.name', config('app.name'))->where('build.version', '1.4.2')->where('build.commit', 'abc1234')->where('build.env', 'testing'),
        );
    }

    public function test_the_footer_status_probe_is_reachable_without_a_session(): void
    {
        $this->getJson('/readyz')->assertOk();
    }
}
