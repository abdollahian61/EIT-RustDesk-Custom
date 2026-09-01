# EIT Desk

EIT-branded Windows remote desktop client, built from RustDesk OSS for the internal EIT network.

## Embedded server configuration

- ID / Rendezvous server: `192.168.20.179`
- Relay server: `192.168.20.179`
- RustDesk server public key: `XEVTmxmO96FdXCV65oKEKUC1WpVfEsL9myia0tsGSf4=`
- Upstream RustDesk version: `1.4.9`

The GitHub Actions workflow builds the x64 Windows client and publishes `EITDesk.exe` in the `EITDesk-Windows-x64` Actions artifact.

Visible Windows branding is applied during the build:

- Product name: `EIT Desk`
- Executable: `EITDesk.exe`
- Company: `Fanavaran Etelaat Khebreh`
- EIT application icon

> The embedded key is the RustDesk server **public** key. Never commit the server private key (`id_ed25519`).
