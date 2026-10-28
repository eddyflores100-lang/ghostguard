# GhostGuard — an agent's guardian

A local-first prototype exploring how to put a guardian between an agent and its tools. Inspired by the Taiko phishing case: an agent can correctly identify a threat yet take an external action without the intended authority.

**Prototype, not a security product.** Only calls routed through `Guard` are checked. It cannot stop an agent using direct network, shell, filesystem, or credentials outside this process. It is not a firewall or sandbox. The demo has no real external actions or authenticated approval interface. Approval capabilities must never be exposed to an untrusted agent.

## Run

Python 3.10+; the core demo requires no internet or third-party packages.

```sh
python3 demo.py
python3 interactive.py
python3 agent_demo.py
python3 -m unittest discover -s tests
```

The demo reads a fictional case, denies a shell call, and pauses a simulated email. Approval capabilities bind one use to the exact action and arguments; a mismatch consumes the capability, and approvals expire after five minutes by default. The demo never approves or sends email. `agent_demo.py --gemma --model gemma3:1b --alethech-store /private/path/store` combines the local model and signed log with human review. `agent_demo.py` starts a separate scripted worker and passes its proposed action to the guard; the human reviews it in the terminal. An approved action is simulated only. The worker is a scripted example, not an autonomous AI agent, and process separation alone is not isolation: it still has the operating-system permissions of its user.

## Optional: Gemma locally

Install Ollama and a suitable Gemma model according to their instructions, start Ollama on localhost and install `gemma3:1b` (model setup needs internet). Then run `python3 demo.py --gemma`. The adapter sends **only** tool and decision labels to `127.0.0.1:11434`, never the action arguments. The model's explanation is advisory and never changes policy. If unavailable, decisions stay unchanged. Model hardware requirements and license depend on the chosen Gemma version. On 2026-10-28, a Windows test with Ollama 0.40.11 and gemma3:1b exercised a real local model proposal and advisory response; the proposed simulated email was rejected.

## Optional: Alethech signed decision log

Install [Alethech](https://github.com/eddyflores100-lang/alethech) and its dependencies in the Python environment, then run `python3 demo.py --alethech-store /private/path/ghostguard-store`. The adapter calls Alethech to sign a commit for each tool/decision label and action hash and verifies the store afterward. The Alethech local working store is not encrypted at rest; protect its keys and use Alethech's encrypted container for portable storage. Hashes can disclose low-entropy inputs by guessing. Signatures establish integrity and provenance, not truth or completeness. The adapter is tested with a test double and was also run with Alethech 0.9.5: three decision commits were created and the resulting store verified successfully. A separate test modified a stored decision commit and confirmed verification rejected the tampered store.

## Remaining before submission

- Integrate an actual agent and isolate it so it cannot bypass a process-separated gateway or access action credentials. Provide authenticated human-only approvals and expiration.
- Document dependency licenses and reproduce the combined Gemma and Alethech flow on other systems.
- Create a review UI and demo video or hosted build; prepare the English DEV post and cite prior work. Hosted services need internet.

## Credits

GhostGuard is a new project. [Alethech](https://github.com/eddyflores100-lang/alethech) is MIT licensed, copyright AliceLabs LLC; it is an optional external dependency and not bundled. No guarantee of contest eligibility or protection is made.

## Model-generated proposal (experimental)

Run `python3 agent_demo.py --model-agent --gemma --model gemma3:1b --alethech-store /private/path/store` after starting Ollama and installing the model and Alethech. The worker sends a fictional phishing scenario to localhost and asks the model for a JSON proposal. The guardian validates its tool, fields and fictional recipient, then pauses for terminal review; the effect is simulated. Invalid output fails closed. Automated tests use a mock Ollama endpoint. A real model run on 2026-10-28 generated a valid proposal, produced advisory text, and recorded a denial path with an automated test response; no email was sent. This is a minimal model-driven example, not a general agent framework or operating-system sandbox.

## Diagnostic logs

`agent_demo.py` writes one JSON object per line to `~/.ghostguard/events.jsonl` by default. Set a different path with `--log-file PATH`. Events report UTC timestamps, a random session identifier, stages, bounded durations, decision and sanitized error type. Message bodies, recipients, model responses, approval tokens and arbitrary exception messages are not written. Logs are local diagnostics: they are not signed, encrypted, automatically rotated, or an authoritative audit trail. File creation requests owner-only Unix permissions; Windows access follows the directory's ACLs. Protect the directory, delete or rotate logs as needed, and use the separately configured Alethech store for signed evidence. A log write failure stops the demo rather than silently losing diagnostics.

## Combined real-model and evidence check (2026-10-28)\n\nOn Windows, Python 3.11 in an isolated virtual environment, Ollama 0.40.11 with gemma3:1b, and Alethech 0.9.5 were used together. The model generated a valid fictional proposal, the guard paused it, Gemma provided advisory text, the test supplied a rejection, and Alethech verified the signed store. The test did not send email or verify an authenticated user interface. Model advice is not authoritative and cannot grant approval.\n