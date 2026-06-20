# AxiomAI Desktop Demo (Tauri)

Desktop demo app that connects to the AxiomAI API and showcases:

1. Health + API connectivity
2. Agent governance decisioning (`/governance/validate`)
3. Quick system integration via webhook fact ingest (`/connectors/webhook/facts`)
4. Case study execution (`/case-studies/{id}/run`)

## Why this demo

This is a fast “connect any system” proof point: you can point the app at an API endpoint and run governance + reasoning flows from a native desktop shell.

## Prerequisites

- Rust toolchain (`rustup`, `cargo`)
- Platform prerequisites for Tauri (WebView/WebKit)
- Running AxiomAI API (default: `http://localhost:8000`)

## Run

```bash
# Terminal 1
axiomai-server

# Terminal 2
cd apps/desktop-tauri/src-tauri
cargo run
```

## Demo flow

1. Enter API URL and click **Health check**
2. In **Agent governance demo**, submit action/context and show ALLOW/DENY with proof
3. In **System connector demo**, ingest a webhook fact from an external system string
4. In **Case study demo**, run CS-07/CS-02/CS-03 to show vertical outcomes
