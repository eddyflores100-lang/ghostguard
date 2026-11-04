# Manual validation: human review and signed evidence

Status: **not yet performed**. This procedure prepares a human-operated test; following or reading it does not constitute evidence that the test passed.

## Preconditions

- Work on a trusted local computer, with the repository, Python, Ollama with `gemma3:1b`, the Docker agent image and a compatible Alethech installation as described in the README. Building the image or downloading a model may require internet.
- Use a new private evidence-store directory outside the repository. The Alethech working store is not encrypted at rest; protect its keys and do not publish the store.
- The dashboard URL contains a launch token. Do not share it or capture it in a video, screenshots, logs or issue reports. Use only fictional inputs and do not expose personal data, environment variables, terminal history or desktop notifications.
- Record the commit SHA, date, OS, Python, Docker, Ollama, model and Alethech versions without secrets. State whether the tester is a human and whether any automation assisted; do not claim independent observation if none occurred.

## Human-operated procedure

1. Start the dashboard with the restricted worker and a private store: `python dashboard.py --agent sandbox --alethech-store /private/path/store`. Replace the example path with an appropriate **new local directory** for the operating system. Open the printed private URL only on that computer. Do not publish it.
2. A person clicks **Generate a proposal** and waits for the review panel. Confirm that the tool, fictional recipient and draft are visible and that no action has been sent. Reload once; confirm that the same pending proposal returns.
3. The person reads the proposal and clicks **Approve simulation** before expiry. Confirm the interface reports “Approved simulation. No email was sent.” and “Signed evidence verified.” Save only the result, not the private URL or store.
4. Generate a fresh proposal. The person clicks **Reject**. Confirm “Rejected or expired. No action was executed.” and “Signed evidence verified.”
5. Generate another proposal, make no decision for longer than the configured five-minute lifetime, then reload or request status. Confirm that the screen reports expiration and no action executed. With Alethech configured, the backend records and verifies the expiration denial; the expiration screen itself does not display a separate verification result.
6. Stop the dashboard. Check that the evidence store remains private. If any step fails, record the exact step and sanitized error; do not report the entire test as passed.

## Evidence and recording

A human click observed locally is evidence of that particular interaction, not of a verified identity, a production authorization system, or resistance to malicious local processes. The dashboard's verification message reports the application's Alethech verification result; signatures support integrity and provenance, not truth or completeness. All effects in this demo are simulated. The container is defense in depth, not proof against escape, and the guard covers only actions routed through it.

For a video, record a fresh synthetic session only after checking the screen for sensitive information. Avoid terminal output containing the private URL. Review the whole recording—including browser chrome, notifications, audio, metadata and every frame—before sharing. Do not publish a recording, evidence keys, raw store or private URL as part of this test.

## Result record

- Commit and date:
- Tester and how the decision was made:
- Environment and versions:
- Generate and reload: pass / fail / not run:
- Human approve and simulated result: pass / fail / not run:
- Human reject: pass / fail / not run:
- Expiration: pass / fail / not run:
- Signed evidence verification and its scope:
- Video privacy review: pass / fail / not run:
- Sanitized failure details and limitations:
