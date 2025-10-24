# Groq Python Implementation Guide

## Executive Summary

This guide provides comprehensive instructions for implementing a Python module (`groq.py`) that interfaces with the Groq AI API, based on the existing TypeScript implementation in the Audio Description Protocol codebase. The module should support text generation, BPM estimation, and phrase generation with token counting, cost tracking, and retry logic.

---

## Table of Contents

1. [Project Context](#project-context)
2. [Prerequisites](#prerequisites)
3. [Environment Setup](#environment-setup)
4. [Core Architecture](#core-architecture)
5. [Implementation Guide](#implementation-guide)
6. [Usage Examples](#usage-examples)
7. [Testing Strategy](#testing-strategy)
8. [Appendix: Reference Code](#appendix-reference-code)

---

## Project Context

### Current State
The Audio Description Protocol (ADP) project currently uses **TypeScript** for backend services that interface with Groq AI. The implementation is located in:
- `backend/src/ai/groq-client.ts` - Main Groq client with text generation
- `backend/src/ai/bpm-estimator.ts` - BPM estimation using Groq
- `backend/src/routes/generate-casual-phrase.ts` - Express route for casual phrase generation
- `backend/src/routes/generate-phrase-from-structure.ts` - Express route for structured phrase generation

### Goal
Create a **Python equivalent** (`groq.py`) that provides the same functionality as the TypeScript implementation, following Python best practices and the project's constitutional requirement: **Python 3.11+ with PyTorch first**.

### Use Cases
1. **Casual Phrase Generation**: Generate creative, informal music descriptions from structured wizard data
2. **Phrase from Structure**: Transform structured tags into professional descriptions
3. **BPM Estimation**: Estimate tempo from phrase descriptions and musical attributes
4. **Token Management**: Count tokens and track API costs
5. **Error Handling**: Robust retry logic with exponential backoff

---

## Prerequisites

### System Requirements
- **Python**: 3.11 or higher
- **Operating System**: Windows 11 (primary), Linux/WSL2 (alternative)
- **CUDA**: 12.8+ (for GPU operations, optional for Groq API)

### Python Dependencies
```txt
groq>=0.33.0              # Official Groq SDK
tiktoken>=0.5.0           # Token counting (OpenAI's tokenizer)
python-dotenv>=1.0.0      # Environment variable management
pydantic>=2.0.0           # Data validation
requests>=2.31.0          # HTTP requests (backup to SDK)
```

### Environment Variables
Create a `.env` file in your project root:

```bash
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Optional: Cost tracking
COST_TRACKING_FILE=./daily-costs.json

# Optional: Logging
LOG_LEVEL=INFO
```

**Important**: Never commit the `.env` file to version control. Add it to `.gitignore`.

### Getting a Groq API Key
1. Visit [https://console.groq.com](https://console.groq.com)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and add it to your `.env` file

---

## Core Architecture

### Module Structure

```
groq.py
├── Enums
│   └── GroqModel (available models)
├── Constants
│   ├── GROQ_PRICING (pricing per model)
│   ├── TEXT_GENERATION_MODELS (subset for text tasks)
│   └── ALL_GROQ_MODELS (complete list)
├── Data Classes
│   ├── WizardData (input data structure)
│   ├── BpmEstimationInput (BPM estimation input)
│   ├── BpmEstimationResult (BPM estimation output)
│   └── GenerationResult (phrase generation output)
├── Client Management
│   ├── get_groq_client() (singleton client)
│   └── get_encoder() (tiktoken encoder)
├── Prompt Management
│   ├── load_casual_prompt_file(poetic_level)
│   ├── load_phrase_prompt_file()
│   └── load_bpm_estimator_prompt()
├── Data Builders
│   ├── build_music_data_string(wizard_data)
│   └── build_structured_json(wizard_data)
├── Token & Cost Management
│   ├── count_tokens(text)
│   └── calculate_cost(tokens, model)
├── Core Functions
│   ├── generate_casual_phrase_groq(wizard_data, model, poetic_level)
│   ├── generate_phrase_from_structure(wizard_data, model)
│   └── estimate_bpm(input_data)
└── Utility Functions
    ├── get_random_model()
    └── retry_with_backoff(func, max_attempts)
```

### Key Design Patterns

1. **Singleton Pattern**: Groq client and tokenizer are initialized once and reused
2. **Lazy Loading**: Resources loaded on first use, not at import time
3. **Retry Logic**: Automatic retry with 2-second delay for retryable errors (429, 500, 502, 503)
4. **Type Safety**: Use Pydantic models for data validation
5. **Cost Tracking**: All operations return token usage and cost metrics

---

## Implementation Guide

### Step 1: Create the Base Structure

Create `groq.py`:

```python
"""
Groq AI Client for Audio Description Protocol

This module provides a Python interface to the Groq API for:
- Casual phrase generation (creative music descriptions)
- Structured phrase generation (professional descriptions)
- BPM estimation from musical attributes

Based on the TypeScript implementation in backend/src/ai/groq-client.ts
"""

import os
import json
import time
from pathlib import Path
from enum import Enum
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
import tiktoken
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
```

### Step 2: Define Models Enum

```python
class GroqModel(str, Enum):
    """
    Available Groq production models (fetched from API 2025-10-02)
    See: https://api.groq.com/openai/v1/models
    """

    # Meta LLaMA models
    LLAMA_3_1_8B_INSTANT = "llama-3.1-8b-instant"
    LLAMA_3_3_70B_VERSATILE = "llama-3.3-70b-versatile"
    LLAMA_4_SCOUT_17B = "meta-llama/llama-4-scout-17b-16e-instruct"
    LLAMA_4_MAVERICK_17B = "meta-llama/llama-4-maverick-17b-128e-instruct"
    LLAMA_GUARD_4_12B = "meta-llama/llama-guard-4-12b"
    LLAMA_PROMPT_GUARD_2_22M = "meta-llama/llama-prompt-guard-2-22m"
    LLAMA_PROMPT_GUARD_2_86M = "meta-llama/llama-prompt-guard-2-86m"

    # OpenAI models
    GPT_OSS_120B = "openai/gpt-oss-120b"
    GPT_OSS_20B = "openai/gpt-oss-20b"

    # Moonshot AI models
    KIMI_K2_INSTRUCT = "moonshotai/kimi-k2-instruct"
    KIMI_K2_INSTRUCT_0905 = "moonshotai/kimi-k2-instruct-0905"

    # Other LLMs
    QWEN3_32B = "qwen/qwen3-32b"
    GEMMA2_9B_IT = "gemma2-9b-it"
    DEEPSEEK_R1_DISTILL_LLAMA_70B = "deepseek-r1-distill-llama-70b"
    ALLAM_2_7B = "allam-2-7b"

    # Production Systems
    GROQ_COMPOUND = "groq/compound"
    GROQ_COMPOUND_MINI = "groq/compound-mini"

    # Audio Transcription
    WHISPER_LARGE_V3 = "whisper-large-v3"
    WHISPER_LARGE_V3_TURBO = "whisper-large-v3-turbo"

    # Text-to-Speech
    PLAYAI_TTS = "playai-tts"
    PLAYAI_TTS_ARABIC = "playai-tts-arabic"
```

### Step 3: Define Pricing Constants

```python
# Model pricing per 1M tokens (USD)
GROQ_PRICING: Dict[GroqModel, float] = {
    # Meta LLaMA
    GroqModel.LLAMA_3_1_8B_INSTANT: 0.05,
    GroqModel.LLAMA_3_3_70B_VERSATILE: 0.59,
    GroqModel.LLAMA_4_SCOUT_17B: 0.3,
    GroqModel.LLAMA_4_MAVERICK_17B: 0.3,
    GroqModel.LLAMA_GUARD_4_12B: 0.2,
    GroqModel.LLAMA_PROMPT_GUARD_2_22M: 0.02,
    GroqModel.LLAMA_PROMPT_GUARD_2_86M: 0.05,

    # OpenAI
    GroqModel.GPT_OSS_120B: 1.0,
    GroqModel.GPT_OSS_20B: 0.5,

    # Moonshot AI
    GroqModel.KIMI_K2_INSTRUCT: 0.6,
    GroqModel.KIMI_K2_INSTRUCT_0905: 0.6,

    # Other LLMs
    GroqModel.QWEN3_32B: 0.5,
    GroqModel.GEMMA2_9B_IT: 0.2,
    GroqModel.DEEPSEEK_R1_DISTILL_LLAMA_70B: 0.7,
    GroqModel.ALLAM_2_7B: 0.1,

    # Production Systems
    GroqModel.GROQ_COMPOUND: 0.59,
    GroqModel.GROQ_COMPOUND_MINI: 0.05,

    # Audio
    GroqModel.WHISPER_LARGE_V3: 0.111,
    GroqModel.WHISPER_LARGE_V3_TURBO: 0.04,

    # TTS
    GroqModel.PLAYAI_TTS: 0.2,
    GroqModel.PLAYAI_TTS_ARABIC: 0.2,
}

# Text generation models (excludes audio, TTS, safety/guard models)
TEXT_GENERATION_MODELS: List[GroqModel] = [
    GroqModel.LLAMA_3_1_8B_INSTANT,
    GroqModel.LLAMA_3_3_70B_VERSATILE,
    GroqModel.LLAMA_4_SCOUT_17B,
    GroqModel.LLAMA_4_MAVERICK_17B,
    GroqModel.GPT_OSS_20B,
    GroqModel.GEMMA2_9B_IT,
    GroqModel.ALLAM_2_7B,
]

# All available models
ALL_GROQ_MODELS: List[GroqModel] = list(GroqModel)
```

### Step 4: Define Data Classes

```python
@dataclass
class Instrumentation:
    """Single instrument with role and descriptors"""
    instrument: str
    role: str
    descriptors: Optional[List[str]] = None


@dataclass
class Vocals:
    """Vocal characteristics"""
    presence: str  # 'none', 'lead', 'backing', etc.
    gender: Optional[str] = None
    style: Optional[str] = None
    descriptors: Optional[List[str]] = None


@dataclass
class Genre:
    """Genre classification"""
    primary: str
    secondary: Optional[List[str]] = None


@dataclass
class WizardData:
    """
    Structured wizard data following ADP vocabulary
    Matches TypeScript interface from wizard/src/types/index.ts
    """
    genre: Optional[Genre] = None
    mood: Optional[List[str]] = None
    energy: Optional[List[str]] = None
    texture: Optional[List[str]] = None
    instrumentation: Optional[List[Instrumentation]] = None
    vocals: Optional[Vocals] = None
    bpm: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, handling nested dataclasses"""
        return {
            k: v if not hasattr(v, '__dict__') else asdict(v)
            for k, v in asdict(self).items()
            if v is not None
        }


@dataclass
class BpmEstimationInput:
    """Input for BPM estimation"""
    input_phrase: str
    standardized_phrase: str
    genre: Optional[str] = None
    subgenres: Optional[List[str]] = None
    mood: Optional[List[str]] = None
    energy: Optional[List[str]] = None
    texture: Optional[List[str]] = None


@dataclass
class BpmEstimationResult:
    """Output from BPM estimation"""
    bpm: int
    tokens_used: int
    cost_usd: float


@dataclass
class GenerationResult:
    """Output from phrase generation"""
    phrase: str
    tokens_used: int
    cost_usd: float
    provider: str
    model: str
```

### Step 5: Client Management (Singleton Pattern)

```python
# Global client instances (lazy-loaded singletons)
_groq_client: Optional[Groq] = None
_encoder: Optional[tiktoken.Encoding] = None


def get_groq_client() -> Groq:
    """
    Get or create Groq client singleton

    Raises:
        ValueError: If GROQ_API_KEY is not set
    """
    global _groq_client

    if _groq_client is None:
        api_key = os.getenv("GROQ_API_KEY")

        print(f"🔑 GROQ_API_KEY present: {bool(api_key)}")
        print(f"🔑 GROQ_API_KEY length: {len(api_key) if api_key else 0}")

        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")

        _groq_client = Groq(api_key=api_key)

    return _groq_client


def get_encoder() -> tiktoken.Encoding:
    """
    Get or create tiktoken encoder singleton
    Uses gpt-5-nano as approximation for token counting
    """
    global _encoder

    if _encoder is None:
        _encoder = tiktoken.encoding_for_model("gpt-5-nano")

    return _encoder
```

### Step 6: Prompt Management

```python
def load_casual_prompt_file(poetic_level: int = 50) -> str:
    """
    Load casual phrase generator system prompt from markdown file
    and append poetic/factual instruction based on poeticLevel

    Args:
        poetic_level: 1 (very poetic) to 100 (very factual)

    Returns:
        System prompt with style instruction
    """
    prompt_path = Path(__file__).parent.parent / "prompts" / "casual-phrase-generator-prompt.md"

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    base_prompt = prompt_path.read_text(encoding="utf-8")

    # Generate style instruction based on poeticLevel
    if poetic_level <= 20:
        # Very poetic (1-20)
        style_instruction = (
            "\n\n**IMPORTANT STYLE INSTRUCTION:** Be EXTREMELY poetic, flowery, and metaphorical. "
            "Use vivid imagery, creative comparisons, and evocative language. Prioritize emotional "
            "impact and artistic expression over technical accuracy. Paint a picture with words, "
            "but still make it clearly about music, with at least 1 musical term"
        )
    elif poetic_level <= 40:
        # Moderately poetic (21-40)
        style_instruction = (
            "\n\n**IMPORTANT STYLE INSTRUCTION:** Be quite poetic and descriptive. Use metaphors, "
            "imagery, and colorful language. Balance artistic expression with some musical references, "
            "with at least 1 musical term."
        )
    elif poetic_level <= 60:
        # Balanced (41-60)
        style_instruction = (
            "\n\n**IMPORTANT STYLE INSTRUCTION:** Balance poetic description with musical terminology. "
            "Mix creative language with accurate music, instrument and genre references, with at least "
            "1 musical term"
        )
    elif poetic_level <= 80:
        # Moderately factual (61-80)
        style_instruction = (
            "\n\n**IMPORTANT STYLE INSTRUCTION:** Be precise and musical. Use proper instrument names, "
            "genre terms, and technical vocabulary. Include specific musical characteristics while "
            "keeping it accessible."
        )
    else:
        # Very factual (81-100)
        style_instruction = (
            "\n\n**IMPORTANT STYLE INSTRUCTION:** Be EXTREMELY factual, precise, and technical. "
            "Use specific instrument names, exact musical terms, genre classifications, and production "
            "techniques. Prioritize accuracy and clarity. Describe using realistic musical and instrument "
            "terminology as logical and precise as possible."
        )

    return base_prompt + style_instruction


def load_phrase_prompt_file() -> str:
    """
    Load phrase-from-structure prompt from markdown file
    Transforms structured tags into a concise, human-readable phrase
    """
    prompt_path = Path(__file__).parent.parent / "prompts" / "phrase-prompt.md"

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    return prompt_path.read_text(encoding="utf-8")


def load_bpm_estimator_prompt() -> str:
    """Load BPM estimator prompt from markdown file"""
    prompt_path = Path(__file__).parent.parent / "prompts" / "bpm-estimator-prompt.md"

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    return prompt_path.read_text(encoding="utf-8").strip()
```

### Step 7: Data Builder Functions

```python
def build_music_data_string(wizard_data: WizardData) -> str:
    """
    Build a music data string from wizard data to append to prompt

    Args:
        wizard_data: Structured wizard data

    Returns:
        Formatted string with music attributes
    """
    parts = []

    if wizard_data.genre and wizard_data.genre.primary:
        parts.append(f"Genre: {wizard_data.genre.primary}")
        if wizard_data.genre.secondary:
            parts.append(f"({', '.join(wizard_data.genre.secondary)})")

    if wizard_data.mood:
        parts.append(f"Mood: {', '.join(wizard_data.mood)}")

    if wizard_data.energy:
        parts.append(f"Energy: {', '.join(wizard_data.energy)}")

    if wizard_data.texture:
        parts.append(f"Texture: {', '.join(wizard_data.texture)}")

    if wizard_data.instrumentation:
        instruments = ", ".join(
            f"{inst.instrument} ({inst.role})"
            for inst in wizard_data.instrumentation
        )
        parts.append(f"Instruments: {instruments}")

    if wizard_data.vocals and wizard_data.vocals.presence and wizard_data.vocals.presence != "none":
        vocals_str = f"Vocals: {wizard_data.vocals.presence}"
        if wizard_data.vocals.style:
            vocals_str += f" {wizard_data.vocals.style}"
        parts.append(vocals_str)

    if wizard_data.bpm:
        parts.append(f"Tempo: {wizard_data.bpm} BPM")

    return ". ".join(parts)


def build_structured_json(wizard_data: WizardData) -> str:
    """
    Build a structured JSON string from wizard data for phrase-prompt

    Args:
        wizard_data: Structured wizard data

    Returns:
        JSON string with structured attributes
    """
    structured = {}

    if wizard_data.genre and wizard_data.genre.primary:
        structured["Genre"] = wizard_data.genre.primary

    if wizard_data.genre and wizard_data.genre.secondary and wizard_data.genre.secondary:
        structured["Sub-genre"] = wizard_data.genre.secondary[0]

    if wizard_data.mood:
        structured["Mood"] = wizard_data.mood

    if wizard_data.energy:
        structured["Energy"] = wizard_data.energy

    if wizard_data.texture:
        structured["Texture"] = wizard_data.texture

    if wizard_data.instrumentation:
        for idx, inst in enumerate(wizard_data.instrumentation, 1):
            key = f"Featured Instrument {idx}"
            structured[key] = {
                "Instrument": inst.instrument,
                "Role": inst.role,
                "Descriptors": inst.descriptors or []
            }

    if wizard_data.vocals and wizard_data.vocals.presence and wizard_data.vocals.presence != "none":
        structured["Vocals"] = {
            "Presence": wizard_data.vocals.presence,
            "Gender": wizard_data.vocals.gender,
            "Style": wizard_data.vocals.style,
            "Descriptors": wizard_data.vocals.descriptors or []
        }

    return json.dumps(structured, indent=2)
```

### Step 8: Token & Cost Management

```python
def count_tokens(text: str) -> int:
    """
    Count tokens in text using tiktoken

    Args:
        text: Input text

    Returns:
        Number of tokens
    """
    encoder = get_encoder()
    tokens = encoder.encode(text)
    return len(tokens)


def calculate_cost(total_tokens: int, model: GroqModel) -> float:
    """
    Calculate cost in USD for given tokens and model

    Args:
        total_tokens: Total tokens used
        model: Groq model

    Returns:
        Cost in USD (7 significant figures)
    """
    price_per_million = GROQ_PRICING[model]
    cost = (total_tokens / 1_000_000) * price_per_million
    return float(f"{cost:.7g}")
```

### Step 9: Utility Functions

```python
import random


def get_random_model() -> GroqModel:
    """
    Select a random model from text generation models array

    Returns:
        Randomly selected GroqModel
    """
    return random.choice(TEXT_GENERATION_MODELS)


async def retry_with_backoff(
    func,
    max_attempts: int = 2,
    delay_seconds: float = 2.0,
    retryable_codes: List[int] = [429, 500, 502, 503]
):
    """
    Retry a function with exponential backoff for retryable errors

    Args:
        func: Async function to retry
        max_attempts: Maximum number of attempts
        delay_seconds: Delay between retries in seconds
        retryable_codes: HTTP status codes that trigger retry

    Raises:
        Last exception if all attempts fail
    """
    last_error = None

    for attempt in range(max_attempts):
        try:
            return await func()
        except Exception as error:
            last_error = error

            # Check if error is retryable
            status_code = getattr(error, "status", None) or getattr(error, "status_code", None)

            if status_code not in retryable_codes:
                raise Exception(f"Terminal error: {str(error)}")

            # Retry logic: wait before next attempt
            if attempt < max_attempts - 1:
                time.sleep(delay_seconds)

    # All attempts failed
    raise Exception(f"Operation failed after {max_attempts} attempts: {str(last_error)}")
```

### Step 10: Core Generation Functions

```python
def generate_casual_phrase_groq(
    wizard_data: WizardData,
    model: Optional[GroqModel] = None,
    poetic_level: int = 50
) -> GenerationResult:
    """
    Generate casual phrase (informal/colloquial description) using Groq API
    Implements retry logic with 2s delay for retryable errors

    Args:
        wizard_data: Structured wizard data following ADP vocabulary
        model: Groq model to use (defaults to random selection)
        poetic_level: Style level from 1 (very poetic) to 100 (very factual)

    Returns:
        GenerationResult with phrase, tokens, cost, provider, model

    Raises:
        ValueError: If token limit exceeded
        Exception: If generation fails after retry
    """
    # Select random model if not specified
    selected_model = model or get_random_model()

    system_prompt = load_casual_prompt_file(poetic_level)
    music_data = build_music_data_string(wizard_data)
    prompt = f"{system_prompt}\n\nMusic Data: {music_data}"

    prompt_tokens = count_tokens(prompt)

    # Enforce 900 token limit
    if prompt_tokens > 900:
        raise ValueError(f"Token limit exceeded: {prompt_tokens} > 900")

    last_error = None

    # Attempt with single retry (2s delay)
    for attempt in range(2):
        try:
            client = get_groq_client()

            print(f"🔧 Sending prompt to Groq (length: {len(prompt)} chars)")
            print(f"📋 Prompt preview: {prompt[:200]}...")
            print(f"🎲 Randomly selected model: {selected_model.value}")

            completion = client.chat.completions.create(
                model=selected_model.value,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                max_tokens=3500,
                temperature=0.1,
            )

            print(f"🤖 Groq raw completion: {json.dumps(dict(completion), default=str, indent=2)}")

            phrase = completion.choices[0].message.content.strip() if completion.choices else ""

            # Remove numbered list prefix if present (e.g., "1. ")
            phrase = phrase.lstrip("0123456789. ")

            print(f"✂️ Extracted phrase after trim: {phrase}")

            total_tokens = completion.usage.total_tokens if completion.usage else 0
            cost_usd = calculate_cost(total_tokens, selected_model)

            return GenerationResult(
                phrase=phrase,
                tokens_used=total_tokens,
                cost_usd=cost_usd,
                provider="groq",
                model=selected_model.value,
            )

        except Exception as error:
            last_error = error
            status_code = getattr(error, "status", None) or getattr(error, "status_code", None)
            retryable_codes = [429, 500, 502, 503]

            if status_code not in retryable_codes:
                raise Exception(f"Terminal error: {str(error)}")

            # Retry logic: wait 2s before second attempt
            if attempt == 0:
                time.sleep(2.0)

    # Both attempts failed
    raise Exception(f"Casual phrase generation failed after retry: {str(last_error)}")


def generate_phrase_from_structure(
    wizard_data: WizardData,
    model: Optional[GroqModel] = None
) -> GenerationResult:
    """
    Generate concise, human-readable phrase from structured wizard data
    Uses phrase-prompt.md to transform structured tags into professional description

    Args:
        wizard_data: Structured wizard data following ADP vocabulary
        model: Groq model to use (defaults to random selection)

    Returns:
        GenerationResult with phrase, tokens, cost, provider, model

    Raises:
        ValueError: If token limit exceeded
        Exception: If generation fails after retry
    """
    # Select random model if not specified
    selected_model = model or get_random_model()

    system_prompt = load_phrase_prompt_file()
    structured_data = build_structured_json(wizard_data)
    prompt = f"{system_prompt}\n\nPlease generate a phrase for the following structured data:\n\n{structured_data}"

    prompt_tokens = count_tokens(prompt)

    # Enforce 2000 token limit
    if prompt_tokens > 2000:
        raise ValueError(f"Token limit exceeded: {prompt_tokens} > 2000")

    last_error = None

    # Attempt with single retry (2s delay)
    for attempt in range(2):
        try:
            client = get_groq_client()

            print(f"🔧 Sending phrase-from-structure prompt to Groq (length: {len(prompt)} chars)")
            print(f"📋 Prompt preview: {prompt[:200]}...")
            print(f"🎲 Randomly selected model: {selected_model.value}")

            completion = client.chat.completions.create(
                model=selected_model.value,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                max_tokens=3500,
                temperature=0.7,
            )

            print(f"🤖 Groq raw completion: {json.dumps(dict(completion), default=str, indent=2)}")

            phrase = completion.choices[0].message.content.strip() if completion.choices else ""

            # Remove quotes if the AI wrapped the phrase in quotes
            phrase = phrase.strip('"\'')

            print(f"✂️ Extracted phrase after trim: {phrase}")

            total_tokens = completion.usage.total_tokens if completion.usage else 0
            cost_usd = calculate_cost(total_tokens, selected_model)

            return GenerationResult(
                phrase=phrase,
                tokens_used=total_tokens,
                cost_usd=cost_usd,
                provider="groq",
                model=selected_model.value,
            )

        except Exception as error:
            last_error = error
            print(f"❌ Error generating phrase from structure: {str(error)}")

            status_code = getattr(error, "status", None) or getattr(error, "response", {}).get("status", 0)
            retryable_codes = [429, 500, 502, 503]

            if status_code not in retryable_codes:
                raise Exception(f"Terminal error: {str(error)}")

            # Retry logic: wait 2s before second attempt
            if attempt == 0:
                time.sleep(2.0)

    # Both attempts failed
    raise Exception(f"Phrase from structure generation failed after retry: {str(last_error)}")


def estimate_bpm(input_data: BpmEstimationInput) -> BpmEstimationResult:
    """
    Estimate BPM using Groq's fast inference with BPM estimator prompt

    Args:
        input_data: BPM estimation input with phrases and musical context

    Returns:
        BpmEstimationResult with BPM, tokens, and cost

    Raises:
        ValueError: If BPM is invalid (not 40-250)
    """
    system_prompt = load_bpm_estimator_prompt()
    client = get_groq_client()

    # Build user message with structured context
    user_message = f"""
Input Phrase: "{input_data.input_phrase}"

Standardized Phrase: "{input_data.standardized_phrase}"

Structured Terms:
- Genre: {input_data.genre or 'None'}
- Subgenres: {', '.join(input_data.subgenres) if input_data.subgenres else 'None'}
- Mood: {', '.join(input_data.mood) if input_data.mood else 'None'}
- Energy: {', '.join(input_data.energy) if input_data.energy else 'None'}
- Texture: {', '.join(input_data.texture) if input_data.texture else 'None'}

Provide only the BPM as a single integer.
""".strip()

    response = client.chat.completions.create(
        model=GroqModel.LLAMA_3_3_70B_VERSATILE.value,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.3,  # Lower for more deterministic BPM estimates
        max_tokens=10,    # Only need a number
    )

    bpm_string = response.choices[0].message.content.strip() if response.choices else ""

    try:
        bpm = int(bpm_string)
    except ValueError:
        raise ValueError(f"Invalid BPM returned: '{bpm_string}'. Expected integer between 40-250.")

    if bpm < 40 or bpm > 250:
        raise ValueError(f"Invalid BPM returned: '{bpm_string}'. Expected integer between 40-250.")

    tokens_used = response.usage.total_tokens if response.usage else 0

    # Calculate cost (llama-3.3-70b-versatile: $0.59/1M input, $0.79/1M output)
    input_tokens = response.usage.prompt_tokens if response.usage else 0
    output_tokens = response.usage.completion_tokens if response.usage else 0
    cost_usd = (input_tokens * 0.59 + output_tokens * 0.79) / 1_000_000

    return BpmEstimationResult(
        bpm=bpm,
        tokens_used=tokens_used,
        cost_usd=cost_usd,
    )
```

---

## Usage Examples

### Example 1: Basic Casual Phrase Generation

```python
from groq import (
    generate_casual_phrase_groq,
    WizardData,
    Genre,
    Instrumentation,
    Vocals
)

# Create wizard data
wizard_data = WizardData(
    genre=Genre(primary="Rock", secondary=["Alternative Rock"]),
    mood=["energetic", "uplifting"],
    energy=["high"],
    texture=["dense"],
    instrumentation=[
        Instrumentation(
            instrument="Electric Guitar",
            role="lead",
            descriptors=["distorted", "aggressive"]
        ),
        Instrumentation(
            instrument="Drums",
            role="rhythm",
            descriptors=["driving", "powerful"]
        )
    ],
    vocals=Vocals(
        presence="lead",
        gender="male",
        style="powerful"
    ),
    bpm=140
)

# Generate casual phrase
result = generate_casual_phrase_groq(
    wizard_data=wizard_data,
    poetic_level=30  # More poetic
)

print(f"Phrase: {result.phrase}")
print(f"Tokens: {result.tokens_used}")
print(f"Cost: ${result.cost_usd:.6f}")
print(f"Model: {result.model}")
```

### Example 2: Structured Phrase Generation

```python
from groq import generate_phrase_from_structure, WizardData, Genre

wizard_data = WizardData(
    genre=Genre(primary="Jazz", secondary=["Smooth Jazz"]),
    mood=["relaxed", "romantic"],
    energy=["medium"],
    bpm=90
)

result = generate_phrase_from_structure(wizard_data)

print(f"Professional Description: {result.phrase}")
```

### Example 3: BPM Estimation

```python
from groq import estimate_bpm, BpmEstimationInput

input_data = BpmEstimationInput(
    input_phrase="A fast-paced techno track with pounding kicks",
    standardized_phrase="High-energy electronic dance music with driving percussion",
    genre="Electronic",
    subgenres=["Techno"],
    energy=["high", "intense"],
    mood=["energetic"]
)

result = estimate_bpm(input_data)

print(f"Estimated BPM: {result.bpm}")
print(f"Tokens Used: {result.tokens_used}")
print(f"Cost: ${result.cost_usd:.8f}")
```

### Example 4: Model Selection and Error Handling

```python
from groq import (
    generate_casual_phrase_groq,
    GroqModel,
    WizardData,
    Genre
)

wizard_data = WizardData(
    genre=Genre(primary="Classical"),
    mood=["contemplative"]
)

try:
    # Use specific model
    result = generate_casual_phrase_groq(
        wizard_data=wizard_data,
        model=GroqModel.LLAMA_3_3_70B_VERSATILE,
        poetic_level=80  # More factual
    )
    print(f"Success: {result.phrase}")

except ValueError as e:
    print(f"Validation Error: {e}")
except Exception as e:
    print(f"Generation Error: {e}")
```

---

## Testing Strategy

### Unit Tests

Create `test_groq.py`:

```python
import pytest
from groq import (
    count_tokens,
    calculate_cost,
    build_music_data_string,
    build_structured_json,
    get_random_model,
    WizardData,
    Genre,
    Instrumentation,
    GroqModel,
    GROQ_PRICING,
)


def test_count_tokens():
    """Test token counting"""
    text = "This is a test string"
    tokens = count_tokens(text)
    assert tokens > 0
    assert isinstance(tokens, int)


def test_calculate_cost():
    """Test cost calculation"""
    cost = calculate_cost(1_000_000, GroqModel.LLAMA_3_1_8B_INSTANT)
    assert cost == 0.05

    cost = calculate_cost(500_000, GroqModel.LLAMA_3_3_70B_VERSATILE)
    expected = 0.59 * 0.5
    assert abs(cost - expected) < 0.001


def test_build_music_data_string():
    """Test music data string builder"""
    wizard_data = WizardData(
        genre=Genre(primary="Rock"),
        mood=["energetic"],
        bpm=140
    )

    result = build_music_data_string(wizard_data)

    assert "Genre: Rock" in result
    assert "Mood: energetic" in result
    assert "Tempo: 140 BPM" in result


def test_build_structured_json():
    """Test structured JSON builder"""
    wizard_data = WizardData(
        genre=Genre(primary="Jazz", secondary=["Smooth Jazz"]),
        mood=["relaxed"]
    )

    result = build_structured_json(wizard_data)

    assert '"Genre": "Jazz"' in result
    assert '"Sub-genre": "Smooth Jazz"' in result
    assert '"Mood": ["relaxed"]' in result


def test_get_random_model():
    """Test random model selection"""
    model = get_random_model()
    assert model in TEXT_GENERATION_MODELS


def test_pricing_coverage():
    """Test that all models have pricing"""
    for model in GroqModel:
        assert model in GROQ_PRICING
```

### Integration Tests

```python
import pytest
import os
from groq import (
    generate_casual_phrase_groq,
    generate_phrase_from_structure,
    estimate_bpm,
    WizardData,
    Genre,
    BpmEstimationInput,
)


@pytest.mark.skipif(not os.getenv("GROQ_API_KEY"), reason="GROQ_API_KEY not set")
def test_generate_casual_phrase_integration():
    """Test casual phrase generation with real API"""
    wizard_data = WizardData(
        genre=Genre(primary="Electronic"),
        mood=["upbeat"],
        bpm=128
    )

    result = generate_casual_phrase_groq(wizard_data, poetic_level=50)

    assert result.phrase
    assert result.tokens_used > 0
    assert result.cost_usd > 0
    assert result.provider == "groq"
    assert result.model


@pytest.mark.skipif(not os.getenv("GROQ_API_KEY"), reason="GROQ_API_KEY not set")
def test_estimate_bpm_integration():
    """Test BPM estimation with real API"""
    input_data = BpmEstimationInput(
        input_phrase="A fast techno track",
        standardized_phrase="High-energy electronic music",
        genre="Electronic",
        energy=["high"]
    )

    result = estimate_bpm(input_data)

    assert 40 <= result.bpm <= 250
    assert result.tokens_used > 0
    assert result.cost_usd > 0
```

### Run Tests

```bash
# Install pytest
pip install pytest pytest-asyncio

# Run unit tests only
pytest test_groq.py -v -k "not integration"

# Run all tests (requires GROQ_API_KEY)
pytest test_groq.py -v
```

---

## Appendix: Reference Code

### Complete File Structure

```
your-project/
├── groq.py                          # Main implementation
├── .env                             # Environment variables (not committed)
├── .env.example                     # Example env file
├── requirements.txt                 # Python dependencies
├── test_groq.py                     # Tests
└── prompts/
    ├── casual-phrase-generator-prompt.md
    ├── phrase-prompt.md
    └── bpm-estimator-prompt.md
```

### Requirements.txt

```txt
groq>=0.33.0
tiktoken>=0.5.0
python-dotenv>=1.0.0
pydantic>=2.0.0
pytest>=7.0.0
pytest-asyncio>=0.21.0
```

### .env.example

```bash
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Optional: Cost tracking
COST_TRACKING_FILE=./daily-costs.json

# Optional: Logging
LOG_LEVEL=INFO
```

---

## Key Differences from TypeScript Implementation

1. **Async/Await**: TypeScript implementation is fully async; Python version uses synchronous calls (can be made async with `asyncio`)
2. **Type Hints**: Python uses type hints and Pydantic instead of TypeScript interfaces
3. **Path Handling**: Uses `pathlib.Path` instead of Node.js `path` module
4. **Environment Loading**: Uses `python-dotenv` instead of Node.js `dotenv`
5. **Error Handling**: Python uses try/except instead of try/catch
6. **JSON Handling**: Uses Python's built-in `json` module instead of `JSON.stringify`

---

## Final Checklist

- [ ] Install all dependencies (`pip install -r requirements.txt`)
- [ ] Create `.env` file with `GROQ_API_KEY`
- [ ] Ensure prompt files exist in `../prompts/` directory
- [ ] Run unit tests to verify basic functionality
- [ ] Run integration tests with real API key
- [ ] Review token limits (900 for casual, 2000 for structured)
- [ ] Verify error handling and retry logic
- [ ] Test cost calculation accuracy
- [ ] Document any project-specific customizations

---

## Support and Resources

- **Groq API Documentation**: https://console.groq.com/docs
- **Groq Python SDK**: https://github.com/groq/groq-python
- **tiktoken Documentation**: https://github.com/openai/tiktoken
- **Original TypeScript Reference**: `backend/src/ai/groq-client.ts`

---

*End of Guide*
