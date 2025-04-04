import json
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig
import torch

# Define the model name from Hugging Face
MODEL_NAME = "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct"

# Global variable to store the loaded model pipeline
model_pipeline = None


def load_model():
    """
    Load DeepSeek Coder V2 Lite Instruct using 8-bit quantization via BitsAndBytesConfig.
    This function initializes the tokenizer and model, then creates a text-generation pipeline.
    """
    global model_pipeline

    print("Loading DeepSeek Coder V2 Lite Instruct with 8-bit quantization...")

    # Create a BitsAndBytesConfig object for 8-bit quantization.
    quant_config = BitsAndBytesConfig(load_in_8bit=True)

    # Load the tokenizer with trust_remote_code to allow custom model architectures.
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME, trust_remote_code=True)

    # Load the model using the quantization_config parameter.
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
        quantization_config=quant_config,
        device_map="auto"
    )

    # Create the text-generation pipeline; use GPU if available.
    model_pipeline = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer
    )

    print("Model loaded successfully.")
    return model_pipeline


def parse_prerequisite_text(raw_text: str) -> dict:
    """
    Parse a raw prerequisite sentence into structured JSON using DeepSeek Coder.

    The function builds a prompt with an example JSON schema and instructs the model to
    output only JSON. It then extracts the JSON block and converts it into a Python dictionary.

    Args:
        raw_text (str): The raw prerequisite text.

    Returns:
        dict: The structured JSON output as a Python dictionary.
    """
    if model_pipeline is None:
        raise RuntimeError("Model not loaded. Please call load_model() first.")

    # Construct the prompt with strict instructions and a schema example.
    prompt = (
        "You are a parser that converts complex prerequisite sentences into structured JSON. "
        "Return only JSON strictly in the following format without any commentary:\n\n"
        "{\n"
        '  "prerequisites": {\n'
        '    "type": "OR",\n'
        '    "conditions": [\n'
        '      { "type": "AND", "conditions": ["<course1>", "<course2>"] },\n'
        '      "<course3>",\n'
        '      { "type": "CONCURRENT", "courses": ["<course4>", "<course5>"] }\n'
        "    ]\n"
        "  }\n"
        "}\n\n"
        "Now parse the following prerequisite text:\n"
        f"\"{raw_text}\"\n"
    )

    # Generate model output with deterministic settings.
    output = model_pipeline(
        prompt,
        max_new_tokens=512,
        do_sample=False,
        truncation=True
    )
    generated_text = output[0]['generated_text']

    # Extract the JSON block from the generated text.
    start_idx = generated_text.find('{')
    end_idx = generated_text.rfind('}')
    if start_idx == -1 or end_idx == -1:
        raise ValueError("No valid JSON block found in the model output.")

    json_str = generated_text[start_idx:end_idx+1]

    # Attempt to parse the JSON string.
    try:
        parsed_output = json.loads(json_str)
    except Exception as e:
        raise ValueError(f"Failed to parse JSON: {e}\nOutput: {json_str}")

    return parsed_output


# Test script to verify functionality when executing this module directly.
if __name__ == "__main__":
    # Load the DeepSeek model.
    load_model()

    # Define a sample prerequisite sentence.
    sample_prereq = (
        "Prerequisite: PHYS 2514 and MATH 2433 or MATH 2934 or concurrent enrollment in "
        "MATH 2433 or MATH 2934."
    )

    # Parse the sample text and print the resulting JSON.
    try:
        result = parse_prerequisite_text(sample_prereq)
        print("Parsed JSON output:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error during parsing: {e}")
