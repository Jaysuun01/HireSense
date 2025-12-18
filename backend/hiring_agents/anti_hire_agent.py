"""
Anti-Hire Advocate Agent
========================

This agent advocates against hiring candidates by building compelling anti-hire arguments.
"""

from uagents import Agent, Context, Protocol
# from uagents.setup import fund_agent_if_low
from .models import DebateRequest, DebateResponse
from .llm_client import SimpleLLMAgent


class AntiHireAgent(Agent):
    def __init__(self, port=8005):
        super().__init__("anti_hire_advocate", port, "anti_hire_seed")
        # fund_agent_if_low(self.wallet.address())

        self.llm_agent = SimpleLLMAgent("anti_hire_advocate") # Model
        self.protocol = Protocol()

        @self.protocol.on_message(model=DebateRequest)
        async def handle_debate(ctx: Context, sender: str, msg: DebateRequest):
            print(
                f"❌ {self.name}: Building anti-hire argument (round {msg.round_number})"
            )

            prompt = f"""
            You are an anti-hire advocate. Build a compelling argument against hiring this candidate.
            
            Intersection Analysis:
            {msg.intersection_analysis.analysis}
            Overall Compatibility: {msg.intersection_analysis.overall_compatibility}
            Skill Matches: {', '.join(msg.intersection_analysis.skill_matches)}
            Skill Gaps: {', '.join(msg.intersection_analysis.skill_gaps)}
            
            Previous Pro-Hire Argument: {msg.previous_argument}
            
            Build a strong anti-hire argument for round {msg.round_number}.
            Focus on the candidate's weaknesses and potential risks.
            
            Respond with ONLY a JSON object in this exact format:
            {{
                "argument": "<your anti-hire argument>",
                "confidence": <0.0 to 1.0>,
                "key_points": ["point1", "point2", "point3"]
            }}
            """

            result = await self.llm_agent.query_llm(prompt)

            if result["success"]:
                try:
                    analysis = self.llm_agent.parse_json_response(result["content"])

                    if analysis:
                        response = DebateResponse(
                            position="anti",
                            argument=analysis.get(
                                "argument", "Candidate has significant skill gaps"
                            ),
                            confidence=analysis.get("confidence", 0.6),
                            key_points=analysis.get(
                                "key_points", ["Missing skills", "Experience concerns"]
                            ),
                        )
                    else:
                        response = DebateResponse(
                            position="anti",
                            argument="Candidate has significant skill gaps",
                            confidence=0.6,
                            key_points=["Missing skills", "Experience concerns"],
                        )

                    print(f"❌ {self.name}: Anti-hire argument complete")
                    await ctx.send(sender, response)

                except Exception as e:
                    print(f"❌ {self.name}: Error processing response: {e}")
                    response = DebateResponse(
                        position="anti",
                        argument="Candidate has significant skill gaps",
                        confidence=0.6,
                        key_points=["Missing skills", "Experience concerns"],
                    )
                    await ctx.send(sender, response)
            else:
                response = DebateResponse(
                    position="anti",
                    argument="Candidate has significant skill gaps",
                    confidence=0.6,
                    key_points=["Missing skills", "Experience concerns"],
                )
                await ctx.send(sender, response)

        self.include(self.protocol)
