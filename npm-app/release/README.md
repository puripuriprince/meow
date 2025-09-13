# The most powerful coding agent

Andji is a CLI tool that writes code for you.

1. Run `andji` from your project directory
2. Tell it what to do
3. It will read and write to files and run commands to produce the code you want

Note: Andji will run commands in your terminal as it deems necessary to fulfill your request.

## Installation

To install Andji, run:

```bash
npm install -g andji
```

(Use `sudo` if you get a permission error.)

## Usage

After installation, you can start Andji by running:

```bash
andji [project-directory]
```

If no project directory is specified, Andji will use the current directory.

Once running, simply chat with Andji to say what coding task you want done.

## Features

- Understands your whole codebase
- Creates and edits multiple files based on your request
- Can run your tests or type checker or linter; can install packages
- It's powerful: ask Andji to keep working until it reaches a condition and it will.

Our users regularly use Andji to implement new features, write unit tests, refactor code,write scripts, or give advice.

## Knowledge Files

To unlock the full benefits of modern LLMs, we recommend storing knowledge alongside your code. Add a `knowledge.md` file anywhere in your project to provide helpful context, guidance, and tips for the LLM as it performs tasks for you.

Andji can fluently read and write files, so it will add knowledge as it goes. You don't need to write knowledge manually!

Some have said every change should be paired with a unit test. In 2024, every change should come with a knowledge update!

## Tips

1. Type '/help' or just '/' to see available commands.
2. Create a `knowledge.md` file and collect specific points of advice. The assistant will use this knowledge to improve its responses.
3. Type `undo` or `redo` to revert or reapply file changes from the conversation.
4. Press `Esc` or `Ctrl+C` while Andji is generating a response to stop it.

## Troubleshooting

If you are getting permission errors during installation, try using sudo:

```
sudo npm install -g andji
```

If you still have errors, it's a good idea to [reinstall Node](https://nodejs.org/en/download).

## Feedback

We value your input! Please email your feedback to `founders@andji.com`. Thank you for using Andji!
