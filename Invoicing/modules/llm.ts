import type { LLMModel, LLMConfig, LLMRequest, LLMResponse, LLMProvider } from '../types';

// ============================================================================
// Available Models Registry
// ============================================================================

export const AVAILABLE_MODELS: LLMModel[] = [

  //============== OpenAI Models =================
  {
    id: 'gpt-4o',
    name: 'GPT-4o',
    provider: 'openai',
    contextWindow: 128000,
    costPer1kInput: 0.0025,
    costPer1kOutput: 0.01
  },
  {
    id: 'gpt-4o-mini',
    name: 'GPT-4o Mini',
    provider: 'openai',
    contextWindow: 128000,
    costPer1kInput: 0.00015,
    costPer1kOutput: 0.0006
  },
  {
    id: 'gpt-4-turbo',
    name: 'GPT-4 Turbo',
    provider: 'openai',
    contextWindow: 128000,
    costPer1kInput: 0.01,
    costPer1kOutput: 0.03
  },
  {
    id: 'gpt-3.5-turbo',
    name: 'GPT-3.5 Turbo',
    provider: 'openai',
    contextWindow: 16385,
    costPer1kInput: 0.0005,
    costPer1kOutput: 0.0015
  },
  {
    id: 'gpt-5-nano-2025-08-07',
    name: 'GPT-5 nano',
    provider: 'openai',
    contextWindow: 400000,
    costPer1kInput: 0.00005,
    costPer1kOutput: 0.0004
  },

  //================== Anthropic Models ======================
  {
    id: 'claude-sonnet-4-5-20250929',
    name: 'Claude 4.5 Sonnet',
    provider: 'anthropic',
    contextWindow: 200000,
    costPer1kInput: 0.003,
    costPer1kOutput: 0.015
  },
  {
    id: 'claude-3-5-sonnet-20241022',
    name: 'Claude 3.5 Sonnet',
    provider: 'anthropic',
    contextWindow: 200000,
    costPer1kInput: 0.003,
    costPer1kOutput: 0.015
  },
  {
    id: 'claude-3-5-haiku-20241022',
    name: 'Claude 3.5 Haiku',
    provider: 'anthropic',
    contextWindow: 200000,
    costPer1kInput: 0.001,
    costPer1kOutput: 0.005
  },
  {
    id: 'claude-3-opus-20240229',
    name: 'Claude 3 Opus',
    provider: 'anthropic',
    contextWindow: 200000,
    costPer1kInput: 0.015,
    costPer1kOutput: 0.075
  },

  //==========   Groq Models (Fast inference) ===========
  {
    id: 'llama-3.3-70b-versatile',
    name: 'Llama 3.3 70B',
    provider: 'groq',
    contextWindow: 128000,
    costPer1kInput: 0.00059,
    costPer1kOutput: 0.00079
  },
  {
    id: 'llama-3.1-8b-instant',
    name: 'Llama 3.1 8B',
    provider: 'groq',
    contextWindow: 128000,
    costPer1kInput: 0.00005,
    costPer1kOutput: 0.00008
  },


  // OpenRouter Models (Unified API)
  {
    id: 'openai/gpt-4o',
    name: 'GPT-4o (via OpenRouter)',
    provider: 'openrouter',
    contextWindow: 128000,
    costPer1kInput: 0.0025,
    costPer1kOutput: 0.01
  },
  {
    id: 'anthropic/claude-sonnet-4.5',
    name: 'Claude 4.5 Sonnet (via OpenRouter)',
    provider: 'openrouter',
    contextWindow: 200000,
    costPer1kInput: 0.003,
    costPer1kOutput: 0.015
  },
  {
    id: 'google/gemini-2.0-flash-exp:free',
    name: 'Gemini 2.0 Flash (Free)',
    provider: 'openrouter',
    contextWindow: 1000000,
    costPer1kInput: 0,
    costPer1kOutput: 0
  },
  {
    id: 'openai/gpt-oss-20b',
    name: 'GPT-OSS 20B (via Groq)',
    provider: 'groq',
    contextWindow: 8192,
    costPer1kInput: 0.0005,
    costPer1kOutput: 0.0005
  },
  {
    id: 'openai/gpt-oss-120b',
    name: 'GPT-OSS 120B (via Groq)',
    provider: 'groq',
    contextWindow: 8192,
    costPer1kInput: 0.001,
    costPer1kOutput: 0.001
  },
  {
    id: 'qwen/qwen3-32b',
    name: 'Qwen 3 32B (via Groq)',
    provider: 'groq',
    contextWindow: 32768,
    costPer1kInput: 0.0007,
    costPer1kOutput: 0.0007
  }
];

// ============================================================================
// Provider API Endpoints
// ============================================================================

const PROVIDER_ENDPOINTS: Record<LLMProvider, string> = {
  openai: 'https://api.openai.com/v1/chat/completions',
  anthropic: 'https://api.anthropic.com/v1/messages',
  groq: 'https://api.groq.com/openai/v1/chat/completions',
  openrouter: 'https://openrouter.ai/api/v1/chat/completions'
};

// ============================================================================
// Configuration
// ============================================================================

let globalConfig: LLMConfig = {
  apiKeys: {},
  timeout: 30000 // 30 seconds default
};

export function configure(config: LLMConfig): void {
  globalConfig = { ...globalConfig, ...config };
}

export function setApiKey(provider: LLMProvider, apiKey: string): void {
  globalConfig.apiKeys[provider] = apiKey;
}

export function getAvailableModels(provider?: LLMProvider): LLMModel[] {
  if (provider) {
    return AVAILABLE_MODELS.filter(m => m.provider === provider);
  }
  return AVAILABLE_MODELS;
}

export function findModel(modelId: string): LLMModel | undefined {
  return AVAILABLE_MODELS.find(m => m.id === modelId);
}

// ============================================================================
// Environment Detection
// ============================================================================

function isProduction(): boolean {
  // Check if running in production (deployed to Vercel)
  // In development, VITE_ prefixed env vars are available
  // In production, they won't be (API keys should be server-side only)

  // Safety check for Node environment (CLI)
  if (typeof import.meta.env === 'undefined') {
    return false;
  }

  return !import.meta.env.VITE_OPENAI_API_KEY;
}

// ============================================================================
// Core Completion Function
// ============================================================================

export async function complete(request: LLMRequest): Promise<LLMResponse> {
  const model = findModel(request.model);

  if (!model) {
    throw new Error(`Model "${request.model}" not found in registry`);
  }

  // If in production, use serverless function (API keys are server-side)
  if (isProduction()) {
    return await completeViaServerless(request, model);
  }

  // In development, use direct API calls (API keys from .env)
  const apiKey = globalConfig.apiKeys[model.provider];
  if (!apiKey) {
    throw new Error(`API key not configured for provider "${model.provider}"`);
  }

  const endpoint = PROVIDER_ENDPOINTS[model.provider];
  const timeout = globalConfig.timeout || 30000;

  // Call appropriate provider
  switch (model.provider) {
    case 'openai':
    case 'groq':
    case 'openrouter':
      return await completeOpenAICompatible(model, apiKey, endpoint, request, timeout);
    case 'anthropic':
      return await completeAnthropic(model, apiKey, endpoint, request, timeout);
    default:
      throw new Error(`Provider "${model.provider}" not implemented`);
  }
}

// ============================================================================
// Serverless Function Proxy (Production)
// ============================================================================

async function completeViaServerless(request: LLMRequest, model: LLMModel): Promise<LLMResponse> {
  const timeout = globalConfig.timeout || 60000; // 60s for serverless
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch('/api/extract', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      signal: controller.signal,
      body: JSON.stringify({
        model: request.model,
        systemPrompt: request.systemPrompt,
        userPrompt: request.userPrompt,
        temperature: request.temperature ?? 0.7,
        maxTokens: request.maxTokens ?? 4096
      })
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(`Serverless API error: ${error.error || response.statusText}`);
    }

    return await response.json();

  } catch (error: any) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      throw new Error(`Request timed out after ${timeout}ms`);
    }
    throw error;
  }
}

// ============================================================================
// Provider-Specific Implementations
// ============================================================================

async function completeOpenAICompatible(
  model: LLMModel,
  apiKey: string,
  endpoint: string,
  request: LLMRequest,
  timeout: number
): Promise<LLMResponse> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`
    };

    // OpenRouter requires additional headers
    if (model.provider === 'openrouter') {
      headers['HTTP-Referer'] = window.location.origin;
      headers['X-Title'] = 'Invoicing App';
    }

    const response = await fetch(endpoint, {
      method: 'POST',
      headers,
      signal: controller.signal,
      body: JSON.stringify({
        model: request.model,
        messages: [
          { role: 'system', content: request.systemPrompt },
          { role: 'user', content: request.userPrompt }
        ],
        //-- gpt-5-nano has special requirements, max_completion_tokens and no temperature
        ...(request.model === 'gpt-5-nano-2025-08-07'
          ? { max_completion_tokens: request.maxTokens ?? 4096 }
          : {
            temperature: request.temperature ?? 0.7,
            max_tokens: request.maxTokens ?? 4096
          })
      })
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(`API request failed: ${error.error?.message || error.error || response.statusText}`);
    }

    const data = await response.json();
    const choice = data.choices?.[0];

    return {
      content: choice?.message?.content || '',
      model: request.model,
      provider: model.provider,
      tokensUsed: data.usage ? {
        input: data.usage.prompt_tokens,
        output: data.usage.completion_tokens
      } : undefined,
      finishReason: choice?.finish_reason
    };

  } catch (error: any) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      throw new Error(`Request timed out after ${timeout}ms`);
    }
    throw error;
  }
}

async function completeAnthropic(
  model: LLMModel,
  apiKey: string,
  endpoint: string,
  request: LLMRequest,
  timeout: number
): Promise<LLMResponse> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01'
      },
      signal: controller.signal,
      body: JSON.stringify({
        model: request.model,
        system: request.systemPrompt,
        messages: [
          { role: 'user', content: request.userPrompt }
        ],
        temperature: request.temperature ?? 0.7,
        max_tokens: request.maxTokens ?? 4096
      })
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(`API request failed: ${error.error?.message || error.error || response.statusText}`);
    }

    const data = await response.json();
    const content = data.content?.[0];

    return {
      content: content?.text || '',
      model: request.model,
      provider: model.provider,
      tokensUsed: data.usage ? {
        input: data.usage.input_tokens,
        output: data.usage.output_tokens
      } : undefined,
      finishReason: data.stop_reason
    };

  } catch (error: any) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      throw new Error(`Request timed out after ${timeout}ms`);
    }
    throw error;
  }
}


// ============================================================================
// Utility Functions
// ============================================================================

export function estimateCost(model: LLMModel, inputTokens: number, outputTokens: number): number {
  if (!model.costPer1kInput || !model.costPer1kOutput) {
    return 0;
  }
  const inputCost = (inputTokens / 1000) * model.costPer1kInput;
  const outputCost = (outputTokens / 1000) * model.costPer1kOutput;
  return inputCost + outputCost;
}

export function roughTokenEstimate(text: string): number {
  // Rough estimate: ~4 characters per token
  return Math.ceil(text.length / 4);
}
