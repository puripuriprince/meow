# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the Andji CLI application - a command-line tool for AI-powered development assistance with agent-based architecture.

## Development Commands

### Install Dependencies
```bash
cd npm-app
bun install
```

### Build
```bash
cd npm-app
bun run build  # Builds binary executable using scripts/build-binary.js
```

### Run Development
```bash
cd npm-app
bun run start      # Run from source with TypeScript
bun run start-bin  # Build and run binary
```

### Type Checking
```bash
cd npm-app
bun run typecheck
```

### Formatting
```bash
cd npm-app
bun run format
```

### Testing
```bash
cd npm-app
bun test                    # Run all tests
bun test [file]            # Run specific test file
```

## Architecture

### Core Components

- **CLI Entry Point** (`npm-app/src/index.ts`): Main entry point that handles command parsing, initialization, and startup flow
- **CLI Class** (`npm-app/src/cli.ts`): Central CLI singleton that manages the interactive session
- **Agent System** (`npm-app/src/agents/`): Agent loading and validation system for extending functionality
- **Tool Handlers** (`npm-app/src/tool-handlers.ts`): Implements various tool operations available to agents
- **Project Files** (`npm-app/src/project-files.ts`): Manages project root detection and file context initialization

### Key Patterns

- Uses Bun runtime for TypeScript execution and building
- Singleton pattern for CLI instance management
- Worker-based file context initialization for performance
- Agent-based extensibility system with local agent loading from `.agents` directory
- Background process management for long-running operations
- Checkpoint system for state management during sessions

### Dependencies

- Built on Bun (>=1.2.11) for runtime and tooling
- Commander for CLI argument parsing
- AI SDK for LLM interactions
- Ripgrep for fast file searching
- Uses workspace structure with `@andji/common` and `@andji/code-map` packages

## Important Notes

- Binary builds target multiple platforms (Linux, macOS, Windows) with both x64 and arm64 architectures
- Uses web-tree-sitter which requires patching during build process
- Analytics and telemetry integrated via PostHog
- Print mode available for non-interactive operation
- Supports custom agent creation and publishing to agent store