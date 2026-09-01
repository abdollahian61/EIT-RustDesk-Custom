from pathlib import Path
import re
import shutil
import sys

ID_SERVER = "192.168.20.179"
RELAY_SERVER = "192.168.20.179"
PUBLIC_KEY = "XEVTmxmO96FdXCV65oKEKUC1WpVfEsL9myia0tsGSf4="
APP_NAME = "EIT Desk"
EXE_NAME = "EITDesk"
COMPANY_NAME = "Fanavaran Etelaat Khebreh"

root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path("rustdesk").resolve()
assets = Path(__file__).resolve().parent.parent / "assets"


def replace_exact(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"Expected text not found in {path}: {old}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


target = None
for path in root.rglob("config.rs"):
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        continue
    if "RENDEZVOUS_SERVERS" in text and "RS_PUB_KEY" in text:
        target = path
        break
if target is None:
    raise SystemExit("Could not find hbb_common/src/config.rs")

text = target.read_text(encoding="utf-8")
text, n1 = re.subn(
    r'pub const RENDEZVOUS_SERVERS:\s*&\[&str\]\s*=\s*&\[[^;]*\];',
    f'pub const RENDEZVOUS_SERVERS: &[&str] = &["{ID_SERVER}"];', text, count=1,
)
text, n2 = re.subn(
    r'pub const RS_PUB_KEY:\s*&str\s*=\s*"[^"]*";',
    f'pub const RS_PUB_KEY: &str = "{PUBLIC_KEY}";', text, count=1,
)
text, n3 = re.subn(
    r'RwLock::new\("RustDesk"\.to_owned\(\)\)',
    f'RwLock::new("{APP_NAME}".to_owned())', text, count=1,
)
if n1 != 1 or n2 != 1 or n3 != 1:
    raise SystemExit(f"Failed to patch config: rendezvous={n1}, key={n2}, app_name={n3}")

needle = "pub fn get_option(k: &str) -> String {"
if needle in text and "EIT_CUSTOM_CONFIG_BEGIN" not in text:
    injected = f'''{needle}\n        // EIT_CUSTOM_CONFIG_BEGIN\n        match k {{\n            "custom-rendezvous-server" => return "{ID_SERVER}".to_owned(),\n            "relay-server" => return "{RELAY_SERVER}".to_owned(),\n            "key" => return "{PUBLIC_KEY}".to_owned(),\n            "api-server" => return "".to_owned(),\n            _ => {{}}\n        }}\n        // EIT_CUSTOM_CONFIG_END'''
    text = text.replace(needle, injected, 1)
target.write_text(text, encoding="utf-8")

cmake = root / "flutter/windows/CMakeLists.txt"
replace_exact(cmake, "project(rustdesk LANGUAGES CXX)", "project(EITDesk LANGUAGES CXX)")
replace_exact(cmake, 'set(BINARY_NAME "rustdesk")', f'set(BINARY_NAME "{EXE_NAME}")')

runner_rc = root / "flutter/windows/runner/Runner.rc"
rc = runner_rc.read_text(encoding="utf-8")
replacements = {
    'VALUE "CompanyName", "Purslane Tech Pte. Ltd."': f'VALUE "CompanyName", "{COMPANY_NAME}"',
    'VALUE "FileDescription", "RustDesk Remote Desktop"': f'VALUE "FileDescription", "{APP_NAME} Remote Desktop"',
    'VALUE "InternalName", "rustdesk"': f'VALUE "InternalName", "{EXE_NAME}"',
    'VALUE "OriginalFilename", "rustdesk.exe"': f'VALUE "OriginalFilename", "{EXE_NAME}.exe"',
    'VALUE "ProductName", "RustDesk"': f'VALUE "ProductName", "{APP_NAME}"',
}
for old, new in replacements.items():
    if old not in rc:
        raise SystemExit(f"Expected Runner.rc value not found: {old}")
    rc = rc.replace(old, new, 1)
runner_rc.write_text(rc, encoding="utf-8")

main_cpp = root / "flutter/windows/runner/main.cpp"
replace_exact(main_cpp, 'std::wstring app_name = L"RustDesk";', f'std::wstring app_name = L"{APP_NAME}";')

icon_source = assets / "EITDesk.ico"
if not icon_source.is_file():
    raise SystemExit(f"Missing EIT icon: {icon_source}")
for destination in (root / "flutter/windows/runner/resources/app_icon.ico", root / "res/icon.ico"):
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(icon_source, destination)

print(f"Patched configuration: {target}")
print(f"Product name: {APP_NAME}")
print(f"Windows executable: {EXE_NAME}.exe")
print(f"ID/Relay server: {ID_SERVER}")
print(f"Public key: {PUBLIC_KEY}")
