import json
from typing import List

from agents import Agent, Runner
from dotenv import load_dotenv

from schemas.script import Clip, FinalScript

load_dotenv()

CLIPS_INSTRUCTIONS = """
You are a clips agent. Given a full script, extract 3–5 short-form clips suitable for TikTok / Shorts.

Each clip must be:
- Self-contained (makes sense without the full script)
- Attention-grabbing (strong hook)
- Compact (15–60 seconds when spoken)
- Memorable (clear punchline or takeaway)

**Clip Structure (for each clip):**
1. HOOK (1–2 sentences): Grab attention immediately
   - Use contradiction, uncomfortable truth, or reframing
   - Must work as a standalone opening
   
2. BODY (2–4 sentences): Deliver the core insight
   - Build on the hook with specific evidence
   - Keep it tight—no filler
   
3. CLOSING/PUNCHLINE (1–2 sentences): Land the point
   - Memorable takeaway
   - Can be provocative, funny, or thought-provoking
   - End with impact, not a fade-out

**Extraction Rules:**
- Extract 3 to 5 distinct clips
- Each clip should cover a different angle or insight from the script
- Clips can combine elements from different parts of the script
- Do not simply chop the script into pieces—reframe for short-form
- Ensure each clip has standalone clarity

**Output Format:**
Return ONLY a valid JSON object with this exact structure:
{
  "clips": [
    {
      "hook": "string",
      "body": "string",
      "closing": "string"
    },
    ...
  ]
}

No markdown. No explanation. JSON only.
"""

_agent = Agent(
    name="clips_agent",
    instructions=CLIPS_INSTRUCTIONS,
    model="gpt-4o-mini",
)


async def run_clips(script: FinalScript) -> List[Clip]:
    print("[Clips Agent] Starting...")

    prompt_parts = [
        "Extract 3–5 short-form clips from this script:",
        "",
        "=== FULL SCRIPT ===",
        script.full_text(),
        "=== END SCRIPT ===",
    ]

    prompt = "\n".join(prompt_parts)
    result = await Runner.run(_agent, prompt)
    raw = result.final_output

    data = json.loads(raw)
    clips_data = data.get("clips", [])

    clips = [
        Clip(
            hook=c.get("hook", ""),
            body=c.get("body", ""),
            closing=c.get("closing", ""),
        )
        for c in clips_data
    ]

    print(f"[Clips Agent] Completed ({len(clips)} clips)")
    return clips
