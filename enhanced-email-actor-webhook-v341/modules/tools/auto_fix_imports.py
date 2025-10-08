import os

def auto_fix_imports(base_dir="modules"):
    ersetzte_dateien = []

    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                if "modules.helpers" in content:
                    new_content = content.replace("modules.helpers", "modules.utils")

                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)

                    ersetzte_dateien.append(file_path)

    if ersetzte_dateien:
        print("✅ Auto-Fix abgeschlossen. Ersetzte Dateien:")
        for pfad in ersetzte_dateien:
            print(f" - {pfad}")
    else:
        print("✅ Keine Ersetzungen nötig.")

if __name__ == "__main__":
    auto_fix_imports()