---
name: ingest-document
description: "Ingest a document (or a folder of them) into your searchable knowledge base with visual understanding — render each slide/page/frame to an image, have Claude describe the visual (diagrams, flows, layouts), and store it plus any extracted text so it's searchable. Use when you want to capture the thinking in a deck, PDF, exported Figma frame, screenshot, or a whole folder of design exports. Triggers: 'ingest document', 'ingest this deck/file/folder', 'capture this into the knowledge base', 'add this with vision', 'vision ingest', pointing at a .pptx/.pdf/.png/.jpg or a folder and asking to bring it into the knowledge base."
---

# Ingest Document (with visual understanding)

Wraps a **vision-ingest CLI command** that renders each slide/page/frame of a document to
an image, asks Claude to describe the visual, and stores that description **plus** any
extracted text in your vector knowledge base. This is what makes diagram-only slides and
Figma frames searchable, not just their text.

## Requirements / adapt this

This skill assumes a local knowledge-base CLI that exposes a `vision <path>` command (renders
→ describes → embeds). The reference backend is the **`copilot`** local-first KB tool, run via
`uv`. **Swap the command for your own KB backend** — the pattern (render every page to an
image, caption it with a model, store caption + text) is the reusable part.

Set the path to your KB repo once:

```sh
COP="$HOME/path/to/copilot"   # the KB CLI repo (its .env is cwd-relative)
```

## When to use

You point at a **file** (`.pdf`, `.pptx`, `.png`, `.jpg`/`.jpeg`) or a **folder** of them and
want the *thinking* in them captured and searchable. Works for decks, exported Figma frames,
screenshots, and PDF exports of Keynote/Google Slides.

## How to run

Run via `uv` with `--directory` so you don't need to change the working directory:

```sh
uv --directory "$COP" run copilot vision "<PATH>"
```

`<PATH>` is the file or folder. Options:
- `-p, --project <id>` — target project. **Omit it when the path is inside a registered
  watch-folder** (the command infers the project automatically). Pass it explicitly for files
  outside any watch-folder.
- `--force` — re-ingest even if the file is unchanged.

List registered projects (to pick `-p`) with:
```sh
uv --directory "$COP" run copilot projects
```

## Steps

1. **Resolve the path.** If the file/folder was named loosely, confirm the absolute path. If
   it doesn't exist, say so rather than guessing.
2. **Decide the project.** If the path is under a known watch-folder, omit `-p` (let it
   infer). Otherwise run `projects`, pick the right one, and pass `-p <id>`. If no project
   fits, ask which project — or whether to create one.
3. **Run the command.** Use a generous timeout: vision makes one model call per
   slide/page/frame, so a large deck can take a minute or more. A 50-page deck ≈ 50 calls.
4. **Report** the `N docs / M chunks` result. Re-running is cheap — unchanged files are
   skipped by content hash (`0 docs / 0 chunks` means nothing changed, not a failure). **If a
   file was already ingested *without* vision (e.g. by a plain folder sync), the
   byte-identical file will be skipped — add `--force` to apply vision to it now.**

## Notes & gotchas

- **`.pptx` needs LibreOffice** (`soffice`) installed to render. Without it, the deck falls
  back to text-only with a logged warning — in that case, export the deck to PDF and re-run,
  or `brew install --cask libreoffice`.
- **`.pdf`, `.png`, `.jpg`** need no system dependency (rendering uses the bundled `pymupdf`).
- Rendered page images are kept for provenance under `~/.copilot/raw/renders/<doc_id>/`.
- A harmless `MuPDF error: ... structure tree` line may print to stderr on some PDFs; the
  render still succeeds — ignore it.
- After ingesting, confirm retrieval with:
  ```sh
  uv --directory "$COP" run copilot query "<something visual from the file>" -p <project>
  ```
- For **Figma**, prefer a dedicated `sync-figma` command (pulls frames over the API
  automatically). Use this skill for Figma only when frames have already been exported to
  image/PDF files.
