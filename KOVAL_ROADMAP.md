# Koval (Rust-Opencode) Roadmap

This document outlines the plan to build `koval-rs`, a high-performance, terminal-based AI software engineer. It aims to replicate the functionality of `opencode` (and by extension `claude-code`) using a Rust architecture similar to `codex-rs`.

**Key Differentiator:** Koval is designed to work natively with **LiteLLM Proxy**, allowing it to speak the standard OpenAI protocol to any backend (OpenAI, Anthropic, Gemini, Local Models).

## 1. Architecture

The project is structured as a Rust Workspace:

*   `crates/cli`: Binary entry point, argument parsing (Clap).
*   `crates/core`: The "Soul". Manages the Agent Loop, Context, and LLM Client.
*   `crates/protocol`: Shared types (Messages, Tool Calls, Config).
*   `crates/tools`: Tool implementations (FileSystem, Shell, Search).
*   `crates/tui`: The User Interface (Ratatui), handling rendering and input.
*   `crates/common`: Utilities, Logging, Configuration.

## 2. Roadmap

### Phase 1: Foundation (Current Focus)
*   [x] Initialize Rust workspace.
*   [ ] **Configuration (`crates/common`)**:
    *   Load config from `~/.koval/config.toml` and Environment Variables.
    *   **Crucial:** Support `OPENAI_BASE_URL` (default: `http://localhost:4000/v1`) and `OPENAI_API_KEY`.
*   [ ] **Protocol (`crates/protocol`)**:
    *   Define `Message` (System, User, Assistant, Tool).
    *   Define `ToolCall` and `ToolResult` structures compatible with OpenAI API.
*   [ ] **LLM Client (`crates/core`)**:
    *   Implement an HTTP client using `reqwest`.
    *   Support Streaming (SSE) for real-time feedback.
    *   Target the **LiteLLM Proxy** interface (Standard OpenAI Chat Completions).

### Phase 2: The Agent Loop (`crates/core`)
*   [ ] Implement the "ReAct" / "Loop" logic:
    1.  User Input.
    2.  Append to Context.
    3.  **Call LLM (Stream)**.
    4.  **Parse Tool Calls**.
    5.  Execute Tools (`crates/tools`).
    6.  Append Tool Results.
    7.  Goto 3.
*   [ ] Implement "Modes":
    *   **Plan Mode**: Read-only, no side effects.
    *   **Build Mode**: Full access (Shell, File Write).

### Phase 3: Tooling (`crates/tools`)
*   [ ] **FileSystem**: `read_file`, `write_file`, `list_dir`, `search` (ripgrep).
*   [ ] **Shell**: `run_command` (using `tokio::process`).
    *   *Security Note:* Prompt user for dangerous commands unless `--yolo` is set.
*   [ ] **Context Management**: `read_url` (fetch web pages).

### Phase 4: Terminal UI (`crates/tui`)
*   [ ] **Ratatui Setup**: Async event loop handling keyboard and rendering.
*   [ ] **Widgets**:
    *   Chat History (Markdown rendering).
    *   Input Box (Multiline).
    *   Spinner/Status Bar for Tool execution.
*   [ ] **UX Polish**:
    *   Syntax highlighting for code blocks.
    *   Streaming text animation.

## 3. Implementation Plan (Immediate Next Steps)

1.  **Define Config**: Create `Config` struct in `common` that defaults to LiteLLM local proxy.
2.  **Define Protocol**: Create OpenAI-compatible structs in `protocol`.
3.  **Build Client**: Create the `Client` in `core` that uses `reqwest` to hit the config URL.
4.  **Basic CLI**: Wire up `main.rs` to read input, send to LLM, and print response (No TUI yet, just verify pipe).