import base64

def encode_file_to_base64(file_path):
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")

def debug_log(message):
    print(f"[DEBUG] {message}")