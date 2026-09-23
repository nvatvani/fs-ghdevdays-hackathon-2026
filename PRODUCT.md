# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Hackathon participants who want blunt feedback on an idea before they build it.

## Product Purpose

Roast My Pitch accepts a pasted hackathon idea and returns an aggressively sarcastic critique from a locally running language model. Success means a participant can quickly identify weak assumptions, vague value propositions, and missing execution detail.

## Positioning

The critique runs against a local Gemma model and is intentionally direct, playful, and private-by-default rather than polished startup coaching.

## Operating Context

Users open the app in a browser, paste a rough idea, and submit it for one critique. The app depends on a local OpenAI-compatible model server at `http://localhost:8080`.

## Capabilities and Constraints

- Single-page idea submission and roast display.
- Flask serves the page and proxies model requests.
- The configured model is `gemma-4-e4b-it`.
- No user accounts, persistence, or remote inference.
- Model-server errors must be visible and actionable.

## Brand Commitments

The voice is blunt, witty, and self-aware. Sarcasm is part of the product behavior, not an incidental flourish.

## Evidence on Hand

The repository README names the product and local-LLM concept. No product assets or external evidence are available.

## Product Principles

- Make the first action obvious.
- Be useful underneath the roast.
- Keep idea data local.
- Fail clearly when the model is unavailable.

## Accessibility & Inclusion

Use semantic form controls, visible keyboard focus, readable contrast, and status messaging that works with assistive technology.
