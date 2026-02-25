# P31 Surf API 官方文档

Getting Started
Overview
Surf API - AI-powered crypto intelligence platform

​
About Surf
Launched by Cyber, Surf is an AI-powered crypto intelligence platform that combines on-chain data, market analytics, and social sentiment to deliver real-time insights for digital asset research and execution. Surf API provides structured access to these data streams through RESTful JSON endpoints, enabling developers and analysts to integrate crypto-native intelligence directly into their products and workflows.
​
Platform Coverage
Surf API covers 40+ blockchains, 200+ data sources, and 100k+ verified crypto voices, offering unified access to:
Market and technical metrics
Token movements
Derivatives data
Sentiment trends
Each endpoint is designed to deliver consistent and high-fidelity data across multiple domains, including DeFi, restaking, AI agents, and emerging on-chain narratives.
​
Why Surf API?
Teams across trading, analytics, and research use Surf API to power dashboards, automated strategies, and intelligence systems with accurate, real-time data. By connecting to Surf, developers gain a single interface for:
Cross-chain monitoring
Protocol research
Market signal detection
Built for speed, transparency, and extensibility.


Common Use Cases
Trading & Finance

Crypto exchanges (CEX, DEX)
Wallets (hot, cold, smart wallets)
Digital banks and fintech integrations
Quant / backtesting environments
On-chain oracles and trading bots
Payment gateways and e-commerce systems
Data & Analytics

Data aggregators, analytics dashboards
Portfolio trackers and research terminals
Block explorers and intelligence platforms
Accounting, compliance, and audit tools
Institutional & academic research
AI & Innovation

AI agents, DeFAI applications
DeFi protocols and NFT marketplaces
Media analytics and VC due diligence


API reference
POST /v1/chat/completions
OpenAI-compatible Chat Completions API (with field-level annotations and streaming SSE details)
Overview
Item	Value
Method	POST
Path	/v1/chat/completions
Authentication	Authorization: Bearer <API_KEY>
Content-Type	application/json
Response (non-streaming)	application/json
Response (streaming)	text/event-stream (SSE)
Quick Start
Send a request with model and messages. Use stream=true to receive SSE chunks.
Supported models: surf-ask, surf-research, surf-1.5, surf-1.5-instant, surf-1.5-thinking.
surf-ask and surf-research are legacy models. surf-1.5, surf-1.5-instant, and surf-1.5-thinking are the new models. Legacy models remain available and the request format is unchanged.
Note: When using surf-research and surf-1.5, it is recommended to set the timeout to 10 minutes.

What’s new in surf-1.5
surf-1.5 is the recommended, next-generation model. Compared to legacy models, it’s designed for more advanced workflows:
Enhanced performance: Delivers superior response quality with significantly reduced latency in surf-1.5-instant, providing faster and more accurate results compared to legacy models.
Custom tool calls (function calling): Better support for defining tools via tools and orchestrating multi-step tool-augmented tasks.
Configurable reasoning depth: Use reasoning_effort (low / medium / high) to trade off speed vs. deeper analysis.
Built for agent-style workflows: Works well with Surf extensions like ability (capability constraints) and citation (citation formats) in the same request shape.
​
Model variants: surf-1.5, surf-1.5-instant, surf-1.5-thinking
The surf-1.5 family includes three model variants with different reasoning capabilities:
surf-1.5-instant: A lightweight model optimized for fast responses to simple queries.
surf-1.5-thinking: A more powerful model with deeper reasoning capabilities, designed to handle complex problems that require thorough analysis and multi-step reasoning.
surf-1.5: An adaptive model that automatically selects between surf-1.5-instant and surf-1.5-thinking based on the request parameters and problem complexity. This provides an optimal balance between speed and depth without requiring manual model selection.

Summary (What you can do)
OpenAI-compatible: Use the OpenAI Chat Completions shape (model, messages, optional stream) and standard Authorization: Bearer <API_KEY>.
Streaming (SSE): Set stream=true to receive incremental chunks (text/event-stream) and terminate on data: [DONE].
Custom tool calls: Provide tools (OpenAI function calling). The model may request tool executions during generation.
Reasoning depth: Control analysis strength with reasoning_effort: low / medium / high.
Surf extensions: Use ability to constrain available capability domains and citation to request output citation formats.
Errors: This endpoint may return 400, 401, or 502 (both streaming and non-streaming).



Examples
{
  "model": "surf-ask", // Required: model identifier. Options: surf-ask / surf-research / surf-1.5 / surf-1.5-instant / surf-1.5-thinking
  "messages": [ // Required: list of chat messages (recommended: at least one role=user message)
    {
      "role": "system", // Required: system / user / assistant
      "content": "You are Surf, an analysis assistant focused on crypto markets and on-chain data." // Required: message content
    },
    {
      "role": "user", // Required: user input
      "content": "Summarize today's BTC market conditions and list the key drivers." // Required: your question/task
    }
  ],
  "stream": false, // Optional: enable streaming output. true -> SSE(text/event-stream), false -> JSON
  "reasoning_effort": "medium", // Optional: reasoning strength low / medium / high
  "ability": [ // Optional: Surf extension: capability-domain constraints/hints
    "evm_onchain", // search / evm_onchain / solana_onchain / market_analysis / calculate
    "market_analysis"
  ],
  "citation": [ // Optional: Surf extension: citation formats to include
    "source", // source / chart
    "chart"
  ],
  "tools": [ // Optional: tool definitions (OpenAI tools/function calling)
    {
      "type": "function", // Required: currently fixed to function
      "function": { // Required: function tool definition
        "name": "calculate_portfolio_value", // Required: tool name (function name)
        "description": "Calculate total portfolio value", // Optional: tool purpose
        "parameters": { // Optional: parameters JSON Schema
          "type": "object",
          "properties": {
            "symbols": {
              "type": "array",
              "items": { "type": "string" }
            }
          },
          "required": ["symbols"]
        }
      }
    }
  ]
}




Non-streaming response example (with field annotations)
{
  "id": "chatcmpl-abc123", // Unique identifier for this completion
  "object": "chat.completion", // Object type (non-streaming responses are typically chat.completion)
  "created": 1699890366, // Creation timestamp (seconds)
  "model": "surf-ask", // Model identifier actually used
  "choices": [ // List of generated results (usually only 1)
    {
      "index": 0, // Choice index
      "finish_reason": "stop", // Finish reason: stop/length/tool_calls/content_filter/error (may also be null)
      "message": { // Final message (assistant)
        "role": "assistant", // Role (typically assistant)
        "content": "BTC is trading flat in the last 24h with rising open interest.", // Model output text
        "reasoning": "Internal chain-of-thought or brief rationale" // (If returned) reasoning/rationale field
      }
    }
  ],
  "usage": { // Token usage statistics
    "prompt_tokens": 23, // Input tokens
    "completion_tokens": 12, // Output tokens
    "total_tokens": 35 // Total tokens (input + output)
  }
}

Chat Completions

curl --request POST \
  --url https://api.asksurf.ai/surf-ai/v1/chat/completions \
  --header 'Authorization: <api-key>' \
  --header 'Content-Type: application/json' \
  --data @- <<EOF
{
  "ability": [
    "[\"evm_onchain\"",
    "\"market_analysis\"",
    "\"calculate\"]"
  ],
  "citation": [
    "[\"source\"",
    "\"chart\"]"
  ],
  "messages": [
    {
      "content": "Summarize today's Bitcoin market.",
      "role": "user"
    }
  ],
  "model": "surf-ask",
  "reasoning_effort": "medium",
  "stream": false,
  "tools": [
    {
      "function": {
        "description": "Calculate the total value of a crypto portfolio",
        "name": "calculate_portfolio_value",
        "parameters": {}
      },
      "type": "function"
    }
  ]
}
EOF




200
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1699890366,
  "model": "surf-ask",
  "choices": [
    {
      "index": 0,
      "finish_reason": "stop",
      "message": {
        "role": "assistant",
        "content": "BTC is trading flat in the last 24h with rising open interest."
      }
    }
  ],
  "usage": {
    "prompt_tokens": 23,
    "completion_tokens": 12,
    "total_tokens": 35
  }
}



400
{
  "error_code": "FORBIDDEN",
  "message": "success",
  "success": true
}


401
{
  "error_code": "FORBIDDEN",
  "message": "success",
  "success": true
}


502
{
  "error_code": "FORBIDDEN",
  "message": "success",
  "success": true
}



Request fields (model.CompletionsRequest)
Note: This endpoint follows the overall structure of OpenAI chat.completions, and additionally provides Surf extension fields such as ability and citation.
Field	Type	Required	Description	Example
model	string (enum)	Yes	Model identifier to use.	"surf-ask" / "surf-research" / "surf-1.5" / "surf-1.5-instant" / "surf-1.5-thinking"
messages	array<object>	Yes	List of chat messages.	Minimal: [{"role":"user","content":"Hello!"}] · With system: [{"role":"system","content":"You are a helpful assistant."},{"role":"user","content":"Hello!"}]
stream	boolean	No	Enable streaming output.	true → SSE (text/event-stream) · false (default) → JSON
reasoning_effort	string (enum)	No	Reasoning strength.	"low" / "medium" / "high"
ability	array<string> (enum)	No	Surf extension: hints/constraints for which capability domains are available for this request.	["search"] / ["evm_onchain"] / ["solana_onchain"] / ["market_analysis"] / ["calculate"]
citation	array<string> (enum)	No	Surf extension: citation formats to include in the output.	["source"] / ["chart"]
tools	array<object>	No	Tool definitions compatible with OpenAI tools/function calling. The model may request tool calls during generation.



Response fields (non-streaming JSON: model.CompletionsProxyResponse)
Field	Type	Description (Notes)
id	string	Unique identifier for this completion (e.g., chatcmpl-...).
object	string	Object type, typically chat.completion.
created	integer	Creation timestamp (seconds).
model	string	Model identifier actually used.
choices	array<object>	List of generated results (usually only 1).
usage	object	Token usage statistics.


choices[] (model.CompletionsChoice)
Field	Type	Description (Notes)
index	integer	Choice index (starting from 0).
finish_reason	string | null	Finish reason. Common values: stop (normal completion), length (reached token limit), tool_calls (triggered tool calls), content_filter (blocked by safety policy), error (aborted due to error).
message	object	Final message (assistant).

message (model.CompletionsMessage)

Field	Type	Description (Notes)
role	string	Role, typically assistant.
content	string	Final model output text.
reasoning	string	(If returned) field used to expose model reasoning/rationale. Note: depending on product policy, this may be omitted or simplified.


usage (model.CompletionsUsage)
Field	Type	Description (Notes)
prompt_tokens	integer	Input tokens.
completion_tokens	integer	Output tokens.
total_tokens	integer	Total tokens (input + output).



Streaming response (SSE: text/event-stream)
When stream=true, the server continuously streams SSE events. Each event block typically looks like:
data: { ...json... }
The termination event is:
data: [DONE]
Note: The current OpenAPI spec does not define a dedicated schema for streaming chunks. In the examples, each chunk’s object is typically chat.completion.chunk, and incremental output is delivered via choices[].delta (e.g., role / content). finish_reason is usually null until the stream ends.

The termination event is:
data: [DONE]

Note: The current OpenAPI spec does not define a dedicated schema for streaming chunks. In the examples, each chunk’s object is typically chat.completion.chunk, and incremental output is delivered via choices[].delta (e.g., role / content). finish_reason is usually null until the stream ends.

Error response (model.BaseResponse)
This endpoint may return: 400, 401, 502 (both streaming and non-streaming).
Field	Type	Description (Notes)
success	boolean	Whether the request succeeded.
message	string	Error message / hint.
error_code	string	Error code (e.g., FORBIDDEN).
Authorizations
Authorizations
​
Authorization
stringheaderrequired
Body
application/json
Request body (OpenAI-compatible)

​
ability
enum<string>[]


Available options: search, evm_onchain, solana_onchain, market_analysis, calculate 
Example:
[
  "[\"evm_onchain\"",
  "\"market_analysis\"",
  "\"calculate\"]"
]


citation
enum<string>[]
Available options: source, chart 
Example:
["[\"source\"", "\"chart\"]"]
​
messages
object[]
Show child attributes

​
model
enum<string>
Available options: surf-ask, surf-research, surf-1.5 
Example:
"surf-ask"

​
reasoning_effort
enum<string>
Available options: low, medium, high 
Example:
"medium"

​
stream
boolean
Example:
false

​
tools
object[]
Show child attributes

Response

200

application/json
Returns JSON when stream=false and SSE chunks when stream=true.

​
choices
object[]
Show child attributes

​
created
integer
Timestamp indicating when the message was generated.

Example:
1764312947

​
id
string
A unique identifier for the generated message. Used for internal tracking.

Example:
"chatcmpl-1764312947577"

​
model
string
Example:
"surf-ask"

​
object
string
Example:
"chat.completion"