<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Actions\Logging\RecordClientLogs;
use App\Http\Requests\ClientLogRequest;
use Illuminate\Http\Response;

final class ClientLogController extends Controller
{
    public function store(ClientLogRequest $request, RecordClientLogs $record): Response
    {
        $record->handle($request->entries(), $request->device(), $request->pageViewId());

        return response()->noContent();
    }
}
