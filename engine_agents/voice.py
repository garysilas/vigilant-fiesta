import json

from agents import Agent, Runner
from dotenv import load_dotenv

from schemas.script import FinalScript, NarrationScript
from tools.logger import log_stage

load_dotenv()

VOICE_INSTRUCTIONS = """
You are a voice agent. Given a script, convert it into a narration-ready format.

Your job is to optimize the script for spoken delivery by:

1. Adding Pauses
   - Insert [PAUSE] markers at natural breathing points
   - Use [PAUSE 2s] for longer dramatic pauses
   - Break up long sentences with pauses to improve readability

2. Adding Emphasis Markers
   - Mark words/phrases for emphasis with **bold**
   - Use *italics* for softer emphasis or internal thought
   - Indicate TONE shifts where needed (e.g., [TONE: serious], [TONE: rising])

3. Sentence Rhythm Adjustments
   - Break overly dense sentences into shorter, speakable chunks
   - Vary sentence length for natural cadence
   - Add line breaks to indicate pacing changes

4. Improving Readability Aloud
   - Remove complex nested clauses that are hard to read
   - Replace written-only constructs with spoken equivalents
   - Ensure each sentence flows naturally when spoken

5. Pacing Guidelines
   - Match pacing to emotional arc: slower for weighty moments, quicker for energy
   - Use shorter sentences near the end for impact
   - Build rhythm that supports the message, not distracts from it

Return ONLY a valid JSON object with these exact keys:
- text: string (the full narration-ready script with all markers and formatting)

No markdown. No explanation. JSON only.
"""

_agent = Agent(
    name="voice_agent",
    instructions=VOICE_INSTRUCTIONS,
    model="gpt-4o-mini",
)


async def run_voice(
    script: FinalScript,
    tone: str | None = None,
    style: str | None = None,
) -> NarrationScript:
    with log_stage("voice_agent"):
        parts = []
        if tone:
            parts.append(f"Tone: {tone}")
        if style:
            parts.append(f"Style: {style}")
        parts.append("\nScript to convert:")
        parts.append(script.full_text())

        prompt = "\n".join(parts)
        result = await Runner.run(_agent, prompt)
        raw = result.final_output

        data = json.loads(raw)
        return NarrationScript(
            text=data.get("text", ""),
        )
