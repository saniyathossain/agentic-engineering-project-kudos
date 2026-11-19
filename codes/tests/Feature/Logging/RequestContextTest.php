<?php

declare(strict_types=1);

namespace Tests\Feature\Logging;

use App\Data\Logging\ClientInfo;
use App\Enums\DeviceType;
use App\Support\Logging\ClientInfoFactory;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Http\Request;
use Tests\TestCase;

final class RequestContextTest extends TestCase
{
    use RefreshDatabase;

    private const CHROME_MAC = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36';

    private const SAFARI_IPHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1';

    public function test_response_echoes_a_generated_request_id(): void
    {
        $id = (string) $this->get('/login')->headers->get('X-Request-ID');

        $this->assertMatchesRegularExpression('/^[a-z0-9]{16}$/', $id);
    }

    public function test_a_valid_incoming_request_id_is_kept(): void
    {
        $this->withHeader('X-Request-ID', 'edge-1234567890')->get('/login')
            ->assertHeader('X-Request-ID', 'edge-1234567890');
    }

    public function test_an_invalid_incoming_request_id_is_replaced(): void
    {
        $response = $this->withHeader('X-Request-ID', 'bad id<script>')->get('/login');

        $this->assertNotSame('bad id<script>', $response->headers->get('X-Request-ID'));
        $this->assertMatchesRegularExpression('/^[a-z0-9]{16}$/', (string) $response->headers->get('X-Request-ID'));
    }

    public function test_error_responses_also_carry_the_request_id(): void
    {
        $this->get('/definitely-not-a-space')->assertNotFound()->assertHeader('X-Request-ID');
    }

    public function test_desktop_browser_is_parsed_from_the_user_agent(): void
    {
        $client = $this->client(self::CHROME_MAC);

        $this->assertSame(DeviceType::Desktop, $client->type);
        $this->assertSame('macOS', $client->os);
        $this->assertSame('10.15.7', $client->osVersion);
        $this->assertSame('Chrome', $client->browser);
        $this->assertSame('126.0.0.0', $client->browserVersion);
    }

    public function test_phone_is_detected_with_client_headers(): void
    {
        $client = $this->client(self::SAFARI_IPHONE, [
            'X-Client-Timezone' => 'Asia/Dhaka',
            'X-Client-Screen' => '390x844',
            'X-Client-Connection' => '4g',
            'X-Device-Model' => 'iPhone 15',
            'Accept-Language' => 'en-GB,en;q=0.9',
        ]);

        $this->assertSame(DeviceType::Mobile, $client->type);
        $this->assertSame('iOS', $client->os);
        $this->assertSame('17.5', $client->osVersion);
        $this->assertSame('Safari', $client->browser);
        $this->assertSame('Asia/Dhaka', $client->timezone);
        $this->assertSame('390x844', $client->screen);
        $this->assertSame('4g', $client->connection);
        $this->assertSame('iPhone 15', $client->model);
        $this->assertSame('en-GB', $client->language);
    }

    public function test_bots_and_missing_user_agents_are_classified(): void
    {
        $this->assertSame(DeviceType::Bot, $this->client('Googlebot/2.1 (+http://www.google.com/bot.html)')->type);
        $this->assertSame(DeviceType::Unknown, $this->client('')->type);
    }

    public function test_header_values_are_bounded(): void
    {
        $client = $this->client(self::CHROME_MAC, ['X-Client-Timezone' => str_repeat('A', 500)]);

        $this->assertSame(200, mb_strlen((string) $client->timezone));
    }

    /** @param  array<string, string>  $headers */
    private function client(string $userAgent, array $headers = []): ClientInfo
    {
        $server = ['HTTP_USER_AGENT' => $userAgent];
        foreach ($headers as $name => $value) {
            $server['HTTP_'.strtoupper(str_replace('-', '_', $name))] = $value;
        }

        return (new ClientInfoFactory())->fromRequest(Request::create('/', 'GET', [], [], [], $server));
    }
}
