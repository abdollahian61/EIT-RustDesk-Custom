# EIT RustDesk Custom

Custom Windows build of RustDesk OSS for the internal EIT network.

## Embedded server configuration

- ID / Rendezvous server: `192.168.20.179`
- Relay server: `192.168.20.179`
- RustDesk server public key: `XEVTmxmO96FdXCV65oKEKUC1WpVfEsL9myia0tsGSf4=`
- Upstream RustDesk version: `1.4.9`

The GitHub Actions workflow builds the x64 Windows client and publishes `EIT-RustDesk.exe` as an Actions artifact.

> The embedded key is the RustDesk server **public** key. Never commit the server private key (`id_ed25519`).
