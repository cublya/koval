# Repository Guidelines

## Project Structure & Module Organization
- `crates/cli/`: Interactive CLI and entry point.
- `crates/core/`: Core agent logic, Swarm orchestration, Planner, and Reviewer.
- `crates/tui/`: Terminal User Interface (Ratatui based).
- `crates/tools/`: Tool implementations (Shell, File I/O).
- `crates/common/`: Shared configuration and utilities.
- `crates/protocol/`: OpenAI API protocol definitions.
- `Cargo.toml`: Workspace configuration.
- `README.md`, `CLA.md`, `LICENSE.md`: Project overview and contribution terms.

## Build, Test, and Development Commands
- `cargo run -- cli` — Launch the interactive CLI.
- `cargo run -- swarm "describe your task"` — Run the multi-agent swarm.
- `cargo build --release` — Build the release binary.
- `cargo check` — Fast check for compilation errors.
- `cargo test` — Run unit and integration tests.

## Coding Style & Naming Conventions
- Standard Rust formatting (`rustfmt`).
- Follow Rust idioms: `snake_case` for functions/modules, `PascalCase` for structs/enums.
- Use `anyhow` for error handling in applications, `thiserror` in libraries.

## Testing Guidelines
- Unit tests co-located in source files (`mod tests`).
- Integration tests in `tests/` directory (if applicable).
- Run `cargo test` to verify changes.
- Ensure new features have corresponding tests.

## Commit & Pull Request Guidelines
- Use Conventional Commit-style prefixes: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`.
- Open an issue for major changes first.
- PRs should include a short description and testing notes.
- By submitting a PR, you agree to the CLA in `CLA.md`.

## Configuration & Security Notes
- Configuration via `~/.config/koval/config.toml` or `KOVAL_*` environment variables.
- Default LLM provider: LiteLLM Proxy (`http://localhost:4000/v1`).
- Do not commit secrets; report security issues privately.
