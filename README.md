# GhostGuard — guardian for agent tool calls

**Prototype, not a security product.** A local example intercepts calls made through its own guard. It cannot prevent direct network, shell, file, or tool calls made around that guard; isolate untrusted agents with independent OS-level controls. No production email, authentication, Gemma, Alethech, hosted demo, or external agent integration is implemented yet.

## Run

Python 3.10+; no third-party dependencies or internet required for this prototype.

```sh
python3 demo.py
python3 -m unittest discover -s tests
```

The demo reads a fictional case, denies a shell call and pauses a simulated email. Approvals bind a single-use random capability to the hash of the exact tool and arguments. The demo does not automatically approve. Never expose approval tokens to an agent; this demo is in-process and has no authenticated human approval interface.

## Design and remaining work

1. Implement a process-separated tool gateway with authenticated, human-only approval, expiration, argument binding and enforcement against bypass; integrate an open-source agent through the gateway with no direct credentials.
2. Integrate Gemma via a locally running model server. Treat its output as advisory, never authorization; when unavailable the policy remains deterministic and fails closed for external actions. Verify real model inference and document model licensing and hardware requirements.
3. Integrate [Alethech](https://github.com/eddyflores100-lang/alethech), MIT, to sign decision evidence; ensure no secrets or full sensitive payloads are stored. Verify a real export and tamper detection. Its signed records establish integrity and provenance, not the truth of an event.
4. Provide a review UI, realistic isolated demo and a DEV post. Optional hosted integrations (Auth0, Render, Sentry) require network and must not be described as offline. A video or hosted demo is required for submission.

## Prior work and competition

This is a new project inspired by the publicly documented Taiko incident and by Alethech; it does not currently embed their code. Public release requires a privacy and licensing review. No claim of eligibility or complete protection is made.
