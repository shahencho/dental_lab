import json

def print_readable_response(response):
    """
    Prints a human-readable summary of an HTTP response.
    
    Args:
        response: A `requests.Response` object
    """
    print("\n" + "=" * 50)
    print("📨 RESPONSE DETAILS")
    print("=" * 50)

    # --- Status Code ---
    print(f"\n🔢 Status Code: {response.status_code}")

    # --- Headers ---
    print("\n🔖 Headers:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")

    # --- Body (try JSON first) ---
    try:
        json_data = response.json()
        print("\n📥 JSON Body (pretty-printed):")
        print(json.dumps(json_data, indent=4))
    except json.JSONDecodeError:
        # Fallback to raw text if not JSON
        text_body = response.text.strip()
        print("\n📄 Raw Text Body:")
        print(text_body if text_body else "<empty response>")

    print("=" * 50 + "\n")