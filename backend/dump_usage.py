"""
Example usage of prompt dump files for direct API calls without DSPy.

Usage:
    python gepa/dump_usage.py --file path/to/messy.csv --model groq/llama-3.3-70b-versatile
"""

import json
import re
import argparse
import time
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "groq/llama-3.3-70b-versatile"


def parse_staff_list(response_text: str) -> list[dict] | None:
    """Extract staff_list from LLM response and parse as JSON."""
    # Strip markdown code blocks if present
    text = response_text.strip()
    if text.startswith("```"):
        # Remove opening ```json or ``` and closing ```
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)

    # Try 1: Parse as JSON object with staff_list key
    try:
        obj = json.loads(text)
        if isinstance(obj, dict) and "staff_list" in obj:
            return obj["staff_list"]
    except json.JSONDecodeError:
        pass

    # Try 2: Find [[ ## staff_list ## ]] marker (DSPy format)
    match = re.search(r'\[\[ ## staff_list ## \]\]\s*(.+?)(?:\[\[ ## completed ## \]\]|$)',
                      response_text, re.DOTALL)
    if match:
        staff_str = match.group(1).strip()
        # Try parsing as JSON array
        try:
            return json.loads(staff_str)
        except json.JSONDecodeError:
            pass

        # Try parsing Python-style list (StaffMember objects)
        staff_list = []
        pattern = r"StaffMember\s*\(\s*name\s*=\s*['\"]([^'\"]+)['\"]\s*,\s*hours\s*=\s*([\d.]+)\s*\)"
        for m in re.finditer(pattern, staff_str):
            staff_list.append({"name": m.group(1), "hours": float(m.group(2))})
        if staff_list:
            return staff_list

    # Try 3: Find any JSON array in the response
    array_match = re.search(r'\[\s*\{[^]]+\}\s*\]', text, re.DOTALL)
    if array_match:
        try:
            return json.loads(array_match.group(0))
        except json.JSONDecodeError:
            pass

    return None


def format_as_csv(staff_list: list[dict]) -> str:
    """Format staff list as CSV."""
    lines = ["Name,Hours"]
    for staff in staff_list:
        lines.append(f"{staff['name']},{staff['hours']}")
    return "\n".join(lines)


def find_truth_file(messy_path: Path) -> Path | None:
    """Find matching truth file for a messy CSV file."""
    name = messy_path.stem
    parent = messy_path.parent

    # Pattern 1: messy_N.csv -> truth_N.csv
    if name.startswith("messy_"):
        suffix = name[6:]  # Remove "messy_"
        truth_path = parent / f"truth_{suffix}.csv"
        if truth_path.exists():
            return truth_path

    # Pattern 2: xxx_messy.csv -> xxx_truth.csv
    if name.endswith("_messy"):
        prefix = name[:-6]  # Remove "_messy"
        truth_path = parent / f"{prefix}_truth.csv"
        if truth_path.exists():
            return truth_path

    return None


def load_truth_file(truth_path: Path) -> list[dict]:
    """Load truth file and return as list of dicts."""
    import csv
    staff_list = []
    with open(truth_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Handle various column name capitalizations
            name = row.get('name') or row.get('Name') or row.get('NAME', '')
            hours = row.get('hours') or row.get('Hours') or row.get('HOURS', '0')
            staff_list.append({"name": name.strip(), "hours": float(hours)})
    return staff_list


def evaluate_results(predicted: list[dict], truth: list[dict]) -> dict:
    """Compare predicted results with truth and return accuracy metrics."""
    # Normalize for comparison
    def normalize(staff_list):
        return {(s['name'].lower().strip(), s['hours']) for s in staff_list}

    pred_set = normalize(predicted)
    truth_set = normalize(truth)

    correct = pred_set & truth_set
    missing = truth_set - pred_set
    extra = pred_set - truth_set

    accuracy = len(correct) / len(truth_set) if truth_set else 0
    exact_match = pred_set == truth_set

    return {
        "exact_match": exact_match,
        "accuracy": accuracy,
        "correct": len(correct),
        "total": len(truth_set),
        "missing": missing,
        "extra": extra
    }


def get_prompt_dump_path(model: str) -> Path:
    """Convert model name to prompt dump file path."""
    safe_name = model.replace('/', '_').replace('.', '-')
    return Path(__file__).parent / "gepa_models" / f"prompt_dump_{safe_name}.json"


def main():
    parser = argparse.ArgumentParser(
        description="Run GEPA inference using prompt dump (no DSPy)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--model", "-m",
        default=DEFAULT_MODEL,
        help=f"LLM model to use (default: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--file", "-f",
        help="Path to messy CSV file"
    )
    parser.add_argument(
        "--prompt", "-p",
        action="store_true",
        help="Show the prompt template and exit (don't call API)"
    )
    parser.add_argument(
        "--reformat", "-r",
        action="store_true",
        help="Reformat response from JSON to CSV style"
    )
    parser.add_argument(
        "--truth", "-t",
        action="store_true",
        help="Find matching truth file and evaluate correctness"
    )

    args = parser.parse_args()

    # Require --file unless --prompt is set
    if not args.prompt and not args.file:
        parser.error("--file is required unless --prompt is set")

    # Load the prompt dump (auto-detect from model)
    dump_path = get_prompt_dump_path(args.model)

    if not dump_path.exists():
        print(f"Prompt dump not found: {dump_path}")
        print("Run dump_prompt_format.py first to generate it.")
        return 1

    with open(dump_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Show prompt template if --prompt is set
    if args.prompt:
        print(f"Model: {data.get('model', args.model)}")
        print("=" * 80)
        for i, msg in enumerate(data["messages"]):
            print(f"\n[{msg['role'].upper()}]")
            print("-" * 40)
            print(msg['content'])
        # Exit if no file provided
        if not args.file:
            return 0
        print("\n" + "=" * 80)
        print("CALLING API...")
        print("=" * 80)

    # Load the CSV content
    csv_path = Path(args.file)
    if not csv_path.exists():
        print(f"CSV file not found: {csv_path}")
        return 1

    with open(csv_path, 'r', encoding='utf-8') as f:
        csv_content = f.read()

    # Replace the sample CSV in the user message with actual content
    user_msg = data["messages"][1]["content"]

    # Find and replace the CSV content between the marker and the "Respond with" instruction
    marker = "[[ ## messy_csv ## ]]\n"
    respond_marker = "Respond with"

    marker_pos = user_msg.find(marker)
    end = user_msg.find(respond_marker)

    if marker_pos >= 0 and end > marker_pos:
        start = marker_pos + len(marker)
        new_user_msg = user_msg[:start] + csv_content + "\n\n\n" + user_msg[end:]
        data["messages"][1]["content"] = new_user_msg
    else:
        print("Warning: Could not find CSV placeholder in prompt dump")
        return 1

    # Determine API base URL from model
    import os
    model_name = args.model
    if model_name.startswith("groq/"):
        base_url = "https://api.groq.com/openai/v1"
        api_model = model_name.replace("groq/", "")
        api_key = os.getenv("GROQ_API_KEY")
    elif model_name.startswith("openai/"):
        base_url = "https://api.openai.com/v1"
        api_model = model_name.replace("openai/", "")
        api_key = os.getenv("OPENAI_API_KEY")
    elif model_name.startswith("together_ai/"):
        base_url = "https://api.together.xyz/v1"
        api_model = model_name.replace("together_ai/", "")
        api_key = os.getenv("TOGETHER_API_KEY")
    elif model_name.startswith("gemini/"):
        base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        api_model = model_name.replace("gemini/", "")
        api_key = os.getenv("GEMINI_API_KEY")
    else:
        print(f"Unsupported model prefix: {model_name}")
        return 1

    # Make the API call
    client = OpenAI(base_url=base_url, api_key=api_key)

    print(f"Model: {model_name}")
    print(f"CSV: {csv_path}")
    print("-" * 40)

    start_time = time.time()
    response = client.chat.completions.create(
        model=api_model,
        messages=data["messages"],
        temperature=0
    )
    elapsed_time = time.time() - start_time

    response_text = response.choices[0].message.content

    # Parse staff list if needed for -r or -t
    staff_list = None
    if args.reformat or args.truth:
        staff_list = parse_staff_list(response_text)

    # Handle truth evaluation
    if args.truth:
        truth_path = find_truth_file(csv_path)
        if not truth_path:
            print(f"No matching truth file found for: {csv_path}")
            print(response_text)
            return 1

        if not staff_list:
            print("Could not parse staff_list from response:")
            print(response_text)
            return 1

        truth_data = load_truth_file(truth_path)
        result = evaluate_results(staff_list, truth_data)

        print(f"Truth file: {truth_path}")
        print("-" * 40)
        if result["exact_match"]:
            print(f"PASS - Exact match ({result['correct']}/{result['total']})")
        else:
            print(f"FAIL - {result['correct']}/{result['total']} correct ({result['accuracy']:.1%})")
            if result["missing"]:
                print(f"  Missing: {result['missing']}")
            if result["extra"]:
                print(f"  Extra: {result['extra']}")

        print("-" * 40)
        print(format_as_csv(staff_list))

    elif args.reformat:
        if staff_list:
            print(format_as_csv(staff_list))
        else:
            print("Could not parse staff_list from response:")
            print(response_text)
    else:
        print(response_text)

    print("-" * 40)
    print(f"Processing time: {elapsed_time:.2f}s")

    return 0


if __name__ == "__main__":
    exit(main())
