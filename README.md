# GhostGuard — an agent's guardian

A local-first prototype exploring how to put a guardian between an agent and its tools. Inspired by the Taiko phishing case: an agent can correctly identify a threat yet take an external action without the intended authority.

**Prototype, not a security product.** Only calls routed through `Guard` are checked. It cannot stop an agent using direct network, shell, filesystem, or credentials outside this process. It is not a firewall or sandbox. The demo has no real external actions or remotely authenticated approval interface. Approval capabilities must never be exposed to an untrusted agent.

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
- Record a demo video and finalize the English DEV post; verify submission rules. Hosted services need internet.

## Credits

GhostGuard is a new project. [Alethech](https://github.com/eddyflores100-lang/alethech) is MIT licensed, copyright AliceLabs LLC; it is an optional external dependency and not bundled. No guarantee of contest eligibility or protection is made.

## Model-generated proposal (experimental)

Run `python3 agent_demo.py --model-agent --gemma --model gemma3:1b --alethech-store /private/path/store` after starting Ollama and installing the model and Alethech. The worker sends a fictional phishing scenario to localhost and asks the model for a JSON proposal. The guardian validates its tool, fields and fictional recipient, then pauses for terminal review; the effect is simulated. Invalid output fails closed. Automated tests use a mock Ollama endpoint. A real model run on 2026-10-28 generated a valid proposal, produced advisory text, and recorded a denial path with an automated test response; no email was sent. This is a minimal model-driven example, not a general agent framework or operating-system sandbox.

## Diagnostic logs

`agent_demo.py` writes one JSON object per line to `~/.ghostguard/events.jsonl` by default. Set a different path with `--log-file PATH`. Events report UTC timestamps, a random session identifier, stages, bounded durations, decision and sanitized error type. Message bodies, recipients, model responses, approval tokens and arbitrary exception messages are not written. Logs are local diagnostics: they are not signed, encrypted, automatically rotated, or an authoritative audit trail. File creation requests owner-only Unix permissions; Windows access follows the directory's ACLs. Protect the directory, delete or rotate logs as needed, and use the separately configured Alethech store for signed evidence. A log write failure stops the demo rather than silently losing diagnostics.

## Combined real-model and evidence check (2026-10-28)\n\nOn Windows, Python 3.11 in an isolated virtual environment, Ollama 0.40.11 with gemma3:1b, and Alethech 0.9.5 were used together. The model generated a valid fictional proposal, the guard paused it, Gemma provided advisory text, the test supplied a rejection, and Alethech verified the signed store. The test did not send email or verify an authenticated user interface. Model advice is not authoritative and cannot grant approval.\n
## Local review dashboard\n\nWith Ollama running and `gemma3:1b` installed, run `python dashboard.py` and open the private URL printed by the command. The browser interface generates a fictional proposal and presents a decision. `python dashboard.py --alethech-store /private/path/store` enables signed evidence. The server listens only on 127.0.0.1 and checks a per-launch token, host and origin; it is intended for a trusted local machine, not remote use or protection from malicious local processes. The approve button only performs a simulated effect. Keep the URL private. On 2026-10-28 the dashboard backend was tested with real Gemma 3 1B and Alethech 0.9.5 using an automated rejection; the signed evidence verified.\n
## Optional smolagents integration

Install smolagents 1.22.0 into the same Python environment and run `python dashboard.py --agent smolagents --alethech-store /private/path/store`. This uses Hugging Face smolagents ToolCallingAgent with an adapter for the local Gemma JSON proposal. The sole custom tool submits a fictional proposal to the parent guard; it cannot send email. On 2026-10-28, a Windows test with smolagents 1.22.0, Ollama 0.40.11, Gemma 3 1B, and Alethech 0.9.5 generated a proposal, paused it, supplied an automated rejection, and verified signed evidence. It did not test interactive human approval or operating-system isolation. The agent process still has the user's normal OS permissions; the bridge cannot stop it from bypassing the guard outside the demo.

## Experimental containerized framework worker

With Docker running, build with `docker build -f Dockerfile.agent -t ghostguard-agent:local .` and start `python dashboard.py --agent sandbox --alethech-store /private/path/store`. The host model generates a fictional proposal; the host validates it before forwarding it on stdin to smolagents in a container without networking, bind mounts, elevated privileges or capabilities, with a read-only filesystem, non-root user and resource limits. The parent validates the returned proposal and retains review and simulated execution. The model service and guardian themselves remain on the host. This is defense in depth, not a guarantee against container escape or a production security boundary.

On 2026-10-28, Docker Desktop 29.2.0 on Windows, smolagents 1.22.0, Gemma 3 1B and Alethech 0.9.5 completed a real combined backend test with an automated rejection and verified signed evidence. A separate container probe observed uid 65532, network unreachable, and a read-only application directory. Human interaction through the dashboard and hostile-code resistance have not yet been verified end to end. Container image building and initial model download require internet.
