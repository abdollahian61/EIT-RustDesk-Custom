from pathlib import Path
import re
import sys

ID_SERVER = "192.168.20.179"
RELAY_SERVER = "192.168.20.179"
PUBLIC_KEY = "XEVTmxmO96FdXCV65oKEKUC1WpVfEsL9myia0tsGSf4="

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("rustdesk")
config_files = list(root.rglob("config.rs"))

target = None
for path in config_files:
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
    f'pub const RENDEZVOUS_SERVERS: &[&str] = &["{ID_SERVER}"];',
    text,
    count=1,
)
text, n2 = re.subn(
    r'pub const RS_PUB_KEY:\s*&str\s*=\s*"[^"]*";',
    f'pub const RS_PUB_KEY: &str = "{PUBLIC_KEY}";',
    text,
    count=1,
)

if n1 != 1 or n2 != 1:
    raise SystemExit(f"Failed to patch constants: rendezvous={n1}, key={n2}")

# Also lock the runtime options when this upstream version exposes Config::get_option().
needle = "pub fn get_option(k: &str) -> String {"
if needle in text and "EIT_CUSTOM_CONFIG_BEGIN" not in text:
    injected = f'''{needle}\n        // EIT_CUSTOM_CONFIG_BEGIN\n        match k {{\n            "custom-rendezvous-server" => return "{ID_SERVER}".to_owned(),\n            "relay-server" => return "{RELAY_SERVER}".to_owned(),\n            "key" => return "{PUBLIC_KEY}".to_owned(),\n            "api-server" => return "".to_owned(),\n            _ => {{}}\n        }}\n        // EIT_CUSTOM_CONFIG_END'''
    text = text.replace(needle, injected, 1)

target.write_text(text, encoding="utf-8")
print(f"Patched {target}")
print(f"ID server: {ID_SERVER}")
print(f"Relay server: {RELAY_SERVER}")
print(f"Public key: {PUBLIC_KEY}")
