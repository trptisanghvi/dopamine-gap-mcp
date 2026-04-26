# The Dopamine Gap MCP Server

## What this server does
This server helps researchers, journalists, and science communicators
trace the gap between clinical neuroscience and public discourse around
mental health concepts, starting with dopamine.

## How to use it effectively

### For gap analysis (the core use case):
Use analyze_semantic_gap with distinct clinical and public terms.
Good example:
- clinical_term: "dopamine reward prediction error striatum"
- public_term: "dopamine hit detox menu fasting"

### For timeline work:
Use get_discourse_timeline before analyze_semantic_gap to understand
when divergence accelerated. This gives context for interpretation.

### What Claude should avoid:
Do not make clinical claims based on Guardian articles.
Do not treat public discourse volume as evidence of scientific consensus.
Always distinguish between what the clinical literature establishes
and what public discourse asserts.

## Known limitations
- Guardian data represents English-language quality journalism,
  not social media or wellness influencer content
- PubMed returns abstracts, not full papers
- Article count is a proxy for discourse volume, not a precise measure
- This server surfaces patterns for human interpretation,
  not clinical conclusions