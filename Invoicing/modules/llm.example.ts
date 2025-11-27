/**
 * LLM Module Usage Examples
 *
 * This file demonstrates how to use the LLM completion module.
 * Copy these patterns into your actual code as needed.
 */

import {
  configure,
  setApiKey,
  complete,
  getAvailableModels,
  findModel,
  estimateCost,
  roughTokenEstimate,
  AVAILABLE_MODELS
} from './llm';

// ============================================================================
// Example 1: Basic Setup and Configuration
// ============================================================================

async function example1_basicSetup() {
  // Configure API keys
  configure({
    apiKeys: {
      openai: 'sk-...',
      anthropic: 'sk-ant-...',
      groq: 'gsk_...',
      openrouter: 'sk-or-...'
    },
    timeout: 60000 // 60 seconds
  });

  // Or set individual keys
  setApiKey('openai', 'sk-...');
}

// ============================================================================
// Example 2: Simple Completion
// ============================================================================

async function example2_simpleCompletion() {
  const response = await complete({
    model: 'gpt-4o-mini',
    systemPrompt: 'You are a helpful assistant that analyzes invoice data.',
    userPrompt: 'Extract the total hours from this data: John: 40hrs, Jane: 35hrs'
  });

  console.log('Response:', response.content);
  console.log('Tokens used:', response.tokensUsed);
}

// ============================================================================
// Example 3: Using Different Providers
// ============================================================================

async function example3_differentProviders() {
  // OpenAI
  const openaiResponse = await complete({
    model: 'gpt-4o-mini',
    systemPrompt: 'You are a data extractor.',
    userPrompt: 'Extract employee names from: John Smith, Jane Doe',
    temperature: 0.3,
    maxTokens: 500
  });

  // Anthropic
  const anthropicResponse = await complete({
    model: 'claude-3-5-haiku-20241022',
    systemPrompt: 'You are a data extractor.',
    userPrompt: 'Extract employee names from: John Smith, Jane Doe',
    temperature: 0.3,
    maxTokens: 500
  });

  // Groq (fast inference)
  const groqResponse = await complete({
    model: 'llama-3.1-8b-instant',
    systemPrompt: 'You are a data extractor.',
    userPrompt: 'Extract employee names from: John Smith, Jane Doe',
    temperature: 0.3,
    maxTokens: 500
  });

  // OpenRouter (unified API, free models available)
  const openrouterResponse = await complete({
    model: 'google/gemini-2.0-flash-exp:free',
    systemPrompt: 'You are a data extractor.',
    userPrompt: 'Extract employee names from: John Smith, Jane Doe',
    temperature: 0.3,
    maxTokens: 500
  });
}

// ============================================================================
// Example 4: Model Discovery and Selection
// ============================================================================

async function example4_modelDiscovery() {
  // List all available models
  console.log('All models:', AVAILABLE_MODELS);

  // Filter by provider
  const anthropicModels = getAvailableModels('anthropic');
  console.log('Anthropic models:', anthropicModels);

  // Find specific model
  const model = findModel('gpt-4o-mini');
  console.log('Model details:', model);

  // Find cheapest model per provider
  const openaiModels = getAvailableModels('openai');
  const cheapest = openaiModels.reduce((prev, curr) => {
    const prevCost = (prev.costPer1kInput || 0) + (prev.costPer1kOutput || 0);
    const currCost = (curr.costPer1kInput || 0) + (curr.costPer1kOutput || 0);
    return currCost < prevCost ? curr : prev;
  });
  console.log('Cheapest OpenAI model:', cheapest);
}

// ============================================================================
// Example 5: Cost Estimation
// ============================================================================

async function example5_costEstimation() {
  const systemPrompt = 'You are an invoice analyzer.';
  const userPrompt = 'Analyze this invoice data...';

  // Estimate tokens
  const estimatedInputTokens = roughTokenEstimate(systemPrompt + userPrompt);
  const estimatedOutputTokens = 500; // Estimate based on expected response

  // Find model and estimate cost
  const model = findModel('gpt-4o-mini');
  if (model) {
    const cost = estimateCost(model, estimatedInputTokens, estimatedOutputTokens);
    console.log(`Estimated cost: $${cost.toFixed(4)}`);
  }

  // Make actual call
  const response = await complete({
    model: 'gpt-4o-mini',
    systemPrompt,
    userPrompt,
    maxTokens: 500
  });

  // Calculate actual cost
  if (response.tokensUsed && model) {
    const actualCost = estimateCost(
      model,
      response.tokensUsed.input,
      response.tokensUsed.output
    );
    console.log(`Actual cost: $${actualCost.toFixed(4)}`);
  }
}

// ============================================================================
// Example 6: Error Handling
// ============================================================================

async function example6_errorHandling() {
  try {
    const response = await complete({
      model: 'gpt-4o-mini',
      systemPrompt: 'You are a helpful assistant.',
      userPrompt: 'Hello!'
    });
    console.log(response.content);
  } catch (error) {
    if (error instanceof Error) {
      if (error.message.includes('API key not configured')) {
        console.error('Please configure your API key first');
      } else if (error.message.includes('Model') && error.message.includes('not found')) {
        console.error('Invalid model ID');
      } else if (error.message.includes('timed out')) {
        console.error('Request took too long');
      } else if (error.message.includes('API request failed')) {
        console.error('API error:', error.message);
      } else {
        console.error('Unexpected error:', error.message);
      }
    }
  }
}

// ============================================================================
// Example 7: Practical Use Case - Smart Data Extraction
// ============================================================================

async function example7_smartExtraction(messyData: string) {
  const systemPrompt = `You are a data extraction specialist.
Extract employee hours data from messy text and return ONLY valid JSON.

Output format:
{
  "employees": [
    {"name": "Full Name", "hours": 40.5}
  ]
}`;

  const userPrompt = `Extract employee hours from this data:\n\n${messyData}`;

  const response = await complete({
    model: 'gpt-4o-mini',
    systemPrompt,
    userPrompt,
    temperature: 0.1, // Low temperature for structured output
    maxTokens: 1000
  });

  try {
    const parsed = JSON.parse(response.content);
    return parsed.employees;
  } catch {
    throw new Error('LLM returned invalid JSON');
  }
}

// ============================================================================
// Example 8: Fallback Strategy (Try Multiple Models)
// ============================================================================

async function example8_fallbackStrategy(prompt: string) {
  const models = [
    'gpt-4o-mini',           // Try fast, cheap model first
    'llama-3.1-8b-instant',  // Fallback to Groq if OpenAI fails
    'claude-3-5-haiku-20241022' // Last resort
  ];

  for (const modelId of models) {
    try {
      console.log(`Trying model: ${modelId}`);
      const response = await complete({
        model: modelId,
        systemPrompt: 'You are a helpful assistant.',
        userPrompt: prompt
      });
      return response;
    } catch (error) {
      console.error(`Failed with ${modelId}:`, error);
      // Continue to next model
    }
  }

  throw new Error('All models failed');
}

// ============================================================================
// Example 9: Streaming Alternative (for UI feedback)
// ============================================================================

/**
 * Note: This module uses standard fetch() which doesn't support streaming.
 * For streaming, you would need to:
 * 1. Modify the fetch calls to handle Server-Sent Events (SSE)
 * 2. Add a `stream: true` parameter to the request
 * 3. Parse the response as a ReadableStream
 *
 * This is more complex and not included in the basic module.
 * For now, show loading indicators while waiting for complete().
 */

export {
  example1_basicSetup,
  example2_simpleCompletion,
  example3_differentProviders,
  example4_modelDiscovery,
  example5_costEstimation,
  example6_errorHandling,
  example7_smartExtraction,
  example8_fallbackStrategy
};
