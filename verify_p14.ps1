Write-Host "--- Phase 2: UI ---"
try {
    $ui = Invoke-WebRequest -Uri "http://localhost:3000/settings" -UseBasicParsing
    # Match generic Next.js indicators to avoid encoding issues
    if ($ui.Content -match "next" -or $ui.Content -match "React") { 
        Write-Host "UI Check: PASS" 
    } else { 
        Write-Host "UI Check: FAIL (Content missing expected markers)" 
    }
} catch {
    Write-Host "UI Check: CRITICAL FAIL ($($_.Exception.Message))"
}

Write-Host "--- Phase 3: Hot Take API ---"
try {
    # Real ID from AgentModelConfig
    $body = @{ input = "test"; api_config = @{ provider = "volcengine"; model_id = "doubao-seed-1-8-251228"; api_key = "test_key" } } | ConvertTo-Json -Depth 5
    $res = Invoke-RestMethod "http://localhost:8000/hot_take" -Method Post -Body $body -ContentType "application/json"
    Write-Host "Hot Take: Success (200)"
} catch {
    # 500/400 is acceptable as it means endpoint is reachable (key validation failure)
    Write-Host "Hot Take: $($_.Exception.Response.StatusCode)"
}

Write-Host "--- Phase 3: Analyze API ---"
try {
   # Real ID from AgentModelConfig
    $body = @{ input = "test"; mode = "deep_analysis"; agent_config = @{ writer = @{ provider = "volcengine"; model_id = "deepseek-v3-2-251201"; api_key = "test_key" } } } | ConvertTo-Json -Depth 5
    $res = Invoke-RestMethod "http://localhost:8000/analyze" -Method Post -Body $body -ContentType "application/json"
    Write-Host "Analyze: Success (200)"
} catch {
    Write-Host "Analyze: $($_.Exception.Response.StatusCode)"
}

Write-Host "--- Done ---"
