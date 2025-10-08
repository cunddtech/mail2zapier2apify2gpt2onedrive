import os

def finde_helper_imports(base_dir="modules"):
    falsche_imports = []

    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                if "modules.helpers" in content:
                    falsche_imports.append(file_path)

    return falsche_imports

def auto_fix_imports(files):
    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        new_content = content.replace("modules.helpers", "modules.utils")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

def main():
    print("🔍 Überprüfe Projekt auf veraltete 'modules.helpers' Importe...")
    falsche_imports = finde_helper_imports()

    if not falsche_imports:
        print("✅ Keine veralteten Imports gefunden.")
    else:
        print(f"⚠️ {len(falsche_imports)} Dateien gefunden mit 'modules.helpers'.")
        for file in falsche_imports:
            print(f" - {file}")

        print("\n🔧 Starte Auto-Fix...")
        auto_fix_imports(falsche_imports)
        print("✅ Alle veralteten Imports wurden auf 'modules.utils' korrigiert!")

if __name__ == "__main__":
    main()