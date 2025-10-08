import os

def check_imports(base_dir="modules"):
    fehlerhafte_imports = []

    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                    if "modules.helpers" in content:
                        fehlerhafte_imports.append(file_path)

    if fehlerhafte_imports:
        print("❌ Fehlerhafte Imports gefunden:")
        for pfad in fehlerhafte_imports:
            print(f" - {pfad}")
    else:
        print("✅ Alle Imports korrekt. Keine Vorkommen von 'modules.helpers' gefunden.")

if __name__ == "__main__":
    check_imports()