# AI 生意经 · AI workflows for real-economy entrepreneurs


Open-source AI workflows for real-economy entrepreneurs and business owners: people building and running
physical stores, manufacturing businesses and in-person services. The goal is to bring AI into concrete
business work, starting with how owners choose topics, explain products and experience, communicate
through WeChat Moments, and present ideas or proposals as readable web pages.

The first four Chinese-language Skills cover topic selection, article writing, WeChat Moments writing
and self-contained HTML storytelling. Adapted from maintained self-use workflows; prepared and maintained with Codex.

[中文使用说明](README.zh-CN.md) · [Skill catalog](skills/README.md) · [Complete synthetic example](skills/examples/README.md)

| Skill | Business task |
| --- | --- |
| [topic-selection](skills/topic-selection/SKILL.md) | Choose a useful topic from customer questions, business situations and available material |
| [article-writing](skills/article-writing/SKILL.md) | Explain a product, service, method or operating experience in a complete article |
| [moments-writing](skills/moments-writing/SKILL.md) | Turn an authorized business observation, product explanation or common question into one natural post |
| [html-story](skills/html-story/SKILL.md) | Present a proposal, introduction or business explanation as a self-contained web page; includes a diagram compiler |

The audience and tasks define this project's focus. Its current public scope is these four workflows;
customer acquisition, sales and business performance still require real-world use and evidence.

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
