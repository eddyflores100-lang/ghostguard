# GhostGuard: A Guardian for an Agent That Almost Went Too Far

**Draft — not submitted. Replace placeholders only after real verification.**

An AI agent can recognize a phishing attempt and still take an action its owner did not authorize. GhostGuard explores a guardian that stands between a proposed action and its execution. Its fictional scenario is inspired by an earlier AliceLabs case study about agent authority overreach.

## The ghost in the machine

The ghost is a protective observer: it watches a tool request, presents its recipient and message, and asks a person to decide. In the demonstration the email destination is fictional and execution is simulated. Rejection produces no send. Approval is single-use, expires and is bound to the action's digest.

## How it works

A local model can propose structured JSON; a strict parser accepts only the supported simulated email action and fields. GhostGuard applies its deterministic rule and pauses for review. Gemma can provide an advisory explanation; it does not grant permission. Alethech can sign decision metadata and verify a local chain. The tests include a mocked model trying to invoke a shell and check that the proposal is rejected.

## Why open innovation matters

The project is designed around locally running model inference, giving operators a choice of supported models. Alethech is an independently developed MIT-licensed project by AliceLabs. Local operation after installation is a goal; it must be verified end to end with a real installed model before claiming it in the submission.

## Demo and verification

- Repository: https://github.com/eddyflores100-lang/ghostguard
- Demo video: **pending**
- Real Gemma run and model version: **pending**
- Tests: run `python3 -m unittest discover -s tests`; mocked-model tests do not prove real model behavior.
- Alethech: previously tested with real signed commits and tamper detection; reproduce and record versions before submission.

## Limitations

The worker is a minimal model-driven example, not a general agent framework. Separate processes are not a security sandbox: a worker with direct system or network access can bypass the guard. There is no authenticated remote approval interface. Do not use this prototype to secure production agents or real email.

## Prize categories

**Pending verification:** overall prize and Best Use of Gemma, if real integration and all contest requirements are demonstrated. Other categories require meaningful verified integrations; none are claimed yet.
