# GhostGuard: The Guardian Angel Behind an Agent

**Draft — not submitted.**

An assistant can notice a suspicious email and still take an action its owner did not authorize. That gap fascinated me: recognizing danger and having permission are different things. For the Ghost in the Machine challenge, I imagined a small guardian angel that watches an agent's proposed tool calls and asks a person before a sensitive action proceeds.

GhostGuard is that experiment. It runs locally, uses an open-weight Gemma model and an open-source agent framework, and can record signed decision evidence with Alethech. It is a prototype with simulated effects, not a promise that arbitrary agents are secure.

## A suspicious message, a paused action

Our fictional scenario is a recruitment message that asks its recipient to run a terminal command. The model drafts a report to a fictional security address. Instead of sending it, the agent hands the proposal to GhostGuard. The dashboard shows the tool, recipient, and message and waits for a person to approve or reject it. In both cases, this demo sends no email.

A local model can also explain why a decision is awaiting review. Its words are advisory: the model cannot grant permission or override policy. The deterministic guard only accepts its allowlisted demo tools. Its approval capability is single-use, expires, and is tied to a digest of the exact action and arguments.

## What runs where

1. Ollama serves Gemma 3 1B locally. The host asks it for a structured fictional report and validates the proposal.
2. In the container mode, Hugging Face smolagents receives the proposal through standard input. The container has no network or bind mounts, runs as a non-root user with a read-only filesystem, drops Linux capabilities, and has process and memory limits.
3. The parent validates the returned action again and pauses it in the review interface. An approval invokes only a simulated tool.
4. If configured, Alethech signs decision metadata and verifies the store. The diagnostic log is separate and contains bounded metadata, not the draft or approval token.

The model and guardian remain on the host. Container restrictions narrow the worker's authority; they do not prove resistance to container escape, protect against malicious local processes, or stop a different agent from bypassing the gateway. The dashboard is loopback-only and checks a per-launch token and request origin. It is not a remotely authenticated approval service.

## A real local run

On October 28, 2026, I tested the combined backend on Windows with Docker Desktop 29.2.0, Ollama 0.40.11, Gemma 3 1B, smolagents 1.22.0, and Alethech 0.9.5. The proposal paused; an automated rejection produced verified signed evidence. In a separate HTTP test, automated approval invoked the simulated effect and verified the evidence. A container probe observed UID 65532, a read-only application directory, and an unreachable external network. No email was sent. The automated tests do not establish that a human completed the browser flow or that the container resists every attack.

To reproduce after installing Docker, Ollama, the model, Python and the optional Alethech package:

```bash
docker build -f Dockerfile.agent -t ghostguard-agent:local .
python dashboard.py --agent sandbox --alethech-store /private/path/ghostguard-store
```

Open the private local URL printed by the program, generate the fictional proposal, and review it. Initial dependency installation and model download require internet; the design is intended to work without it afterward, but offline operation has not been verified end to end. Run the automated tests with `python -m unittest discover -s tests`.

## Why open innovation matters

Gemma can run on a machine I control, and smolagents exposes the agent machinery instead of hiding it behind a service. That makes the boundary inspectable and lets a developer change the model or framework. Alethech is an optional independent AliceLabs project for signed evidence; signatures protect integrity and provenance, not truth or completeness. The local working store is not encrypted at rest, so its keys still need protection.

## What I would build next

The next steps are a broader independently enforced tool gateway, authenticated remote approvals, better threat-model testing, and a demonstration recording. Real integrations would need explicit permissions, credential isolation, and a way to prevent agents from reaching side-effecting tools outside the gateway. GhostGuard does not yet provide those guarantees.

Repository: https://github.com/eddyflores100-lang/ghostguard

This post is a draft. No submission, prize, or certification is claimed. Model and dependency licenses apply separately.
