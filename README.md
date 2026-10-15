# AI 生意经 · Practical Skills for small teams

Four Chinese-language workflows adapted from a maintained AI-assisted workbench: topic selection,
article writing, WeChat Moments writing and self-contained HTML storytelling. Prepared and maintained with Codex.

[中文使用说明](README.zh-CN.md) · [Skill catalog](skills/README.md) · [Complete synthetic example](skills/examples/README.md)

| Skill | Output |
| --- | --- |
| [topic-selection](skills/topic-selection/SKILL.md) | A recommended topic, weekly slate, signal-based topic or feedback follow-up |
| [article-writing](skills/article-writing/SKILL.md) | An article, tutorial, business explanation or focused revision |
| [moments-writing](skills/moments-writing/SKILL.md) | One natural WeChat Moments post from authorized material |
| [html-story](skills/html-story/SKILL.md) | A self-contained reading page or presentation; includes an original diagram compiler |

## Try one task

Give a file-capable AI assistant this instruction:

> Read `skills/topic-selection/SKILL.md` in full. Use `skills/examples/source.md` to recommend one topic for a small restaurant owner. Keep the fictional-example identity and the limits of the evidence.

Then use the writing or HTML Skill if needed. Each Skill can run independently; do not load every Skill
or rerun the entire workflow for a one-paragraph change. Copy a whole Skill directory when installing
through your client's documented mechanism. This repository does not modify global client settings.

Skills need an AI assistant; model services may have separate costs. No account credentials, private
knowledge base, scheduler or publishing integration is included. The optional diagram compiler uses
Python 3.10+ and the standard library:

```sh
cd skills/html-story
python3 scripts/diagram_compiler.py examples/flow.json --check-only
python3 scripts/diagram_compiler.py examples/flow.json --style humanist --form scroll --output diagram.html
```

The second command writes a fragment, not a complete page. Choose a fresh output path; existing output
files are overwritten. Follow the [diagram contract](skills/html-story/references/diagram-contract.md)
to embed it and verify phone and desktop layouts.

## Scope and evidence

This initial release contains four public adaptations. It does not include the full private operating
system or its data. Source and adaptation boundaries are documented in [ORIGINS](skills/ORIGINS.md).
All bundled examples are fictional. Writing outputs are demonstrations made in the preparation session,
not independent quality benchmarks, customer results or evidence of public adoption. The HTML reading
example was inspected at phone and desktop sizes; deck and dual modes remain unverified in this release.
Installed-client and human business acceptance remain pending.

The primary maintainer is [savannahx0uybzri53ntk7c-tech](https://github.com/savannahx0uybzri53ntk7c-tech).
See [CONTRIBUTING](CONTRIBUTING.md) and [SECURITY](SECURITY.md). Licensed under [MIT](LICENSE).
No OpenAI program acceptance, funding or endorsement is claimed.
