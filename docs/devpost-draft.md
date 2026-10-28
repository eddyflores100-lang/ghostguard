# GhostGuard: A Guardian Between an Agent and Its Tools

**Draft — not submitted.**

An agent can identify a suspicious message and still propose an action that its owner has not authorized. GhostGuard explores a small checkpoint between that proposal and a sensitive tool. The example is a fictional report about a suspicious recruiting email.

## The ghost in the machine

GhostGuard shows the proposed recipient and draft before a decision. The recipient is restricted to an `.invalid` address and the email tool is simulated: neither approval nor rejection sends a message. An approval is single-use, expires, and is bound to the exact action digest.

## The working prototype

A separate model-driven worker asks local Gemma for a structured JSON proposal. A strict parser admits only the supported fictional email fields. The deterministic guard pauses the request. The local dashboard lets the user review and approve or reject the simulated action; Gemma's explanation is advisory and cannot authorize it. An optional Alethech store records signed decision metadata and verifies it after the decision.

The dashboard listens only on loopback and uses a per-launch secret, host and origin checks. It is intended for a trusted local machine, not as a remotely authenticated production approval service. The model worker runs with the user's ordinary OS permissions; process separation is not isolation and cannot prevent bypassing the guard.

## What we tested

- Python tests cover denied tools, approval expiry and reuse, payload binding, malformed proposals, dashboard authorization checks, and simulated decisions.
- On October 28, 2026, a Windows test used Ollama 0.40.11, Gemma 3 1B and Alethech 0.9.5 together. A real model generated a proposal; the guard paused it; the test supplied a rejection; and the signed evidence store verified. No email was sent. A separate local test exercised the dashboard backend with these integrations.
- The README explains how to reproduce the demo. Model behavior can vary, and invalid model output is rejected.

## What's next

Integrate an established open agent framework behind an independently enforced tool boundary, isolate its operating-system capabilities, and add authenticated multi-user approvals before considering real effects. A demo recording and a submission are still pending.

Source: https://github.com/eddyflores100-lang/ghostguard

Alethech is an optional independent MIT-licensed project by AliceLabs. Model and runtime licenses apply separately. No prize or contest submission is claimed.
