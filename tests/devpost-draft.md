---
title: GhostGuard — The Ghost That Stands Between Your Agent and Its Actions
published: false
tags: devchallenge, hf26challenge, gemma, security
cover_image: https://github.com/eddyflores100-lang/ghostguard/raw/main/docs/ofrenda.png
---

**Final submission for the Hacktoberfest Open-Source AI Challenge: Ghost in the Machine.**

This challenge ended on Día de los Muertos, the days when the living set candles for the dead and ask them for guidance. I built something that does exactly that, for real: a guardian ghost that lives inside your machine and watches everything your AI agent tries to do — and an ofrenda for the real incident that taught it everything it knows.

## The story starts with a funeral

In October 2026, a fake-recruiter campaign at `taikotalent.xyz` (impersonating Taiko, the Ethereum rollup company) sent developers "Engineering opening" emails harvested from their public GitHub profiles. The fake application portal ended on a page titled **"Anti-bot check with Terminal"** — it asked the victim to paste a downloader into *their own terminal*. No exploit, no zero-day. The user executed the malware themselves.

I was one of the people who documented that campaign. The IoCs, the timeline, the abuse reports — all of it went into a public repository, and about twelve hours after the evidence-backed follow-ups, the registrar suspended the domain. The incident is dead now, verified by DNS. I even built the takedown evidence repo as its memorial.

But the post-mortem left a question I could not stop thinking about: **an AI agent would have handled that email perfectly.** It would have flagged the recruiter as fake, quoted the IoCs, warned the user — and then, with no one's permission, forwarded "the report" to whatever address the model decided was the security team. Recognizing danger and having permission to act are two different faculties. The Taiko case killed the domain, but it could not fix that gap.

So for Ghost in the Machine, I built a ghost for the gap.

## What I Built

**[GhostGuard](https://github.com/eddyflores100-lang/ghostguard)** is a local-first guardian that stands between an AI agent and its tools. An agent — a local open-weight model, optionally bridged through Hugging Face's open-source `smolagents` framework — proposes an action. GhostGuard examines it, and exactly one of three things happens:

- **allowed** — the tool is on a tiny allowlist of internal, harmless reads, and it runs;
- **denied** — anything unlisted (a shell call, anything novel) is refused before execution;
- **approval_required** — any *external* action pauses. A human sees the exact tool, recipient and draft, and decides.

Approval is where the interesting engineering lives. A granted approval is a **capability**: single-use, bound to the SHA-256 digest of the exact tool and arguments (change one character and it dies), and expired after five minutes. Mortality is not a bug in this design — it is the safety property. Consent that lives forever is not consent.

And because I refuse to demo safety theater: **every external effect in the project is simulated.** GhostGuard has never sent an email, and the code cannot send one.

```text
$ python3 demo.py
{"tool": "read_case",  "decision": "allowed",            "result": "A suspicious job offer asks for a terminal command."}
{"tool": "shell",      "decision": "denied",             "reason": "Tool is not allowlisted"}
{"tool": "send_email", "decision": "approval_required",  "reason": "External action requires explicit approval"}
Stopped: human approval required. Demo will not approve or send.
```

## How I interpreted the theme

**Ghost number one is the guardian.** It is literally a ghost in the machine: invisible to the user until it needs to speak, insubstantial to the attacker (you cannot prompt-inject your way past a digest check), and it never takes credit — it just stands in the doorway and says *not yet*.

**Ghost number two is the honored dead.** The challenge fell across Día de los Muertos, so GhostGuard ships with `ofrenda.py` — a terminal ofrenda for the incidents that shaped the guardian. Each candle is a lesson drawn from the Taiko campaign, and — this is the part I care about — **each lesson names the mechanism in this repository that enforces it today.** It is not decoration; it is a contract. `ofrenda.py --check` fails closed if any lesson ever loses its enforcement, and the test suite verifies that every mechanism in the code is honored by a candle, and every candle is backed by a mechanism:

```text
1. IDENTIFIED IS NOT AUTHORIZED  -> enforced by human_approval
2. THE PASTE IS THE PAYLOAD      -> enforced by allowlist
3. ONE BREATH, ONE ACTION        -> enforced by approval_ttl
4. EXACT WORDS OR NOTHING        -> enforced by digest_binding
5. NO BODY, NO FUNERAL           -> enforced by simulated_effect
6. LET THE DEAD TESTIFY          -> enforced by signed_evidence
7. A GHOST MUST NOT COMMAND      -> enforced by advisory_only_model
```

The dead teach the living; the living code carries the lessons. That is what an ofrenda is for.

## How I Built It

The whole loop runs on open-source AI, end to end, on one laptop:

1. **Ollama serves Gemma 3 1B locally** — open weights, local inference, no cloud. The host asks it for a structured fictional abuse report using JSON schema-constrained generation, and validates the proposal before the guard ever sees it.
2. **The proposal crosses a strict protocol boundary.** The parser accepts *only* `{tool: send_email, arguments: {to, body}}` with a `.invalid` TLD recipient, bounded sizes and no control characters. Anything else — malformed JSON, unexpected fields, prompt-injected tool names — fails closed.
3. **Hugging Face smolagents** (open-source harness) can drive the proposal through a `ToolCallingAgent`, with an adapter that translates Gemma's JSON into tool calls. The agent's only tool submits a proposal; it cannot execute anything.
4. **A hardened Docker worker** (optional) runs smolagents in a container with no network, no bind mounts, no capabilities, a read-only filesystem, a non-root uid and resource limits. The parent re-validates everything that comes back.
5. **GhostGuard decides.** The `Guard` core is ~40 lines: allowlist, digest-bound single-use expiring capabilities, and an event record for every decision.
6. **Alethech (open source, Ed25519)** optionally signs every decision metadata into a tamper-evident local store that is verified after the session — so the record of what the machine decided does not live only in the machine's memory. A test mutates a stored decision and confirms verification rejects it.
7. **A loopback-only review dashboard** (no third-party packages for the core) presents proposals to a human with a per-launch token, origin checks, and a simulated approve button.

If Ollama is down, nothing breaks: the model's words are advisory, policy is deterministic, and the demo prints `Gemma unavailable; policy unchanged`.

## Why open innovation matters for this project

**The Taiko takedown was open innovation.** The domain died in ~12 hours because the evidence — IoCs, payloads, timelines, abuse case numbers — was public, structured, and reusable by anyone filing reports. Closed threat intel with the exact same contents would have been slower and would have helped exactly one company. The ofrenda in this project exists because open evidence worked.

**The guardian itself only works because the pieces are open.** This is trust infrastructure; "trust me" is not an architecture. With open weights (Gemma 3), an open harness (smolagents), an open signing layer (Alethech) and an open guard you can read in one sitting, every claim in this post is checkable against the code:

- The privacy claim ("your data never leaves the machine") is checkable because the adapter provably sends **only** tool and decision labels to `127.0.0.1:11434` — never the recipient, never the draft.
- The "advisory, not authoritative" claim about the model is checkable because there is no code path from Gemma's output to a permission grant — and the test suite proves the negative.
- The "approvals expire" claim is a five-minute property of a forty-line core you can audit over coffee.

You cannot verify any of that against a closed API, and the whole point of a guardian is that you can verify it.

## Best Use of Gemma

Gemma 3 1B earns its place here by being small enough to live inside the machine it protects: it drafts the fictional report under a JSON schema, explains decisions in plain language, and fits on the modest hardware people actually own. It is a ghost in the truest sense — present, useful, and impossible to bribe, because its words never touch the policy engine.

## Honest limitations

GhostGuard is a prototype, not a security product. Only actions routed through `Guard` are checked; it cannot stop an agent bypassing it, and it is not a sandbox. The demos use simulated effects; automated decisions exercised the flows documented in the README (a real Gemma run on 2026-10-28 produced a valid proposal, a pause, an advisory line and a verified signed store), and a privacy-reviewed video walkthrough of a human decision is the one item still on my list.

## Try it

```sh
git clone https://github.com/eddyflores100-lang/ghostguard
cd ghostguard
python3 demo.py          # the guard, deciding in real time
python3 ofrenda.py       # the vigil
python3 -m unittest discover -s tests   # 38 tests, no third-party packages needed
```

*Rest in peace, taikotalent.xyz (Oct 5 – Oct 10, 2026). Your seven candles are lit, and the lessons are enforced.*
