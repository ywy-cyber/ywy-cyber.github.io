---
title: "How this site is built"
date: 2026-11-09
tags: ["meta", "Hugo", "GitHub Pages"]
description: "Hugo + PaperMod + GitHub Actions — the whole site is just Markdown."
---

## Stack

- **Hugo** (extended v0.169): compiles Markdown into static pages in well under a second.
- **PaperMod** theme: layout, dark mode, full-text search, tags and archives.
- **GitHub Actions**: every push to `main` builds and publishes to GitHub Pages.

No server, no database, no bill to pay.

## Writing a post

Drop a Markdown file into `content/en/posts/` and push:

```markdown
---
title: "Title"
date: 2026-11-09
tags: ["tag"]
description: "One-line summary"
---

Body goes here.
```

The Chinese version lives at the matching path under `content/zh/posts/`; the language switch in the header flips between them.

## Why not an existing blogging platform

Three reasons: the content stays plain Markdown, I control the styling completely, and the site is mine forever.
