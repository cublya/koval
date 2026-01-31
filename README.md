# Koval

Koval is a developer tool for building and running agentic workflows locally.

Note: This project is under active-development.

## Why Koval
- Local-first workflow (privacy-friendly)
- Branch-per-agent / parallel work style
- Minimal UX, automation-focused
- **Rust Native**: High performance, single binary distribution.
- **Swarm Mode**: Autonomous planning and execution with review loops.

## Getting Started

### Prerequisites
- Rust Toolchain (`cargo`, `rustc`)
- LiteLLM Proxy (recommended, running on `http://localhost:4000`) or any OpenAI-compatible API.

### Installation
```bash
# Build the project
cargo build --release
```

### Usage
Run the CLI interactive mode:
```bash
./target/release/koval-cli
# OR
cargo run -- cli
```

Start a Swarm task:
```bash
./target/release/koval-cli swarm "Refactor the authentication module"
# OR
cargo run -- swarm "Refactor the authentication module"
```

## Configuration
Koval is configured via `~/.config/koval/config.toml` or Environment Variables.

**Defaults:**
- Base URL: `http://localhost:4000/v1`
- API Key: `sk-1234`
- Model: `gpt-4o`

**Environment Overrides:**
- `KOVAL_OPENAI_BASE_URL`
- `KOVAL_OPENAI_API_KEY`
- `KOVAL_MODEL`

## License

Koval is **source-available** under the **Apache License 2.0** with the
**Koval Non-Commercial Addendum**. See `LICENSE.md`.

For commercial licensing, contact the project owner. (contact: hikmat@cublya.com) 

## Contributing

By submitting a pull request, you agree to the terms in `CLA.md`.

- Open an issue for major changes
- Keep PRs small and focused
- Include a short description and testing notes

## AI-Assisted Development

This project may include code generated or assisted by AI tools.
All such code is reviewed, modified, and integrated by maintainers and is
licensed under the same terms as the rest of the project.

## Security

If you discover a security issue, please report it privately (do not open a public issue).
(contact: hikmat@cublya.com)
