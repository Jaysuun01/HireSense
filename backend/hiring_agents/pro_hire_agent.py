"""
Pro-Hire Advocate Agent
======================

This agent advocates for hiring candidates by building compelling pro-hire arguments.
"""

from uagents import Agent, Context, Protocol
# from uagents.setup import fund_agent_if_low
from .models import DebateRequest, DebateResponse
from .llm_client import SimpleLLMAgent


class ProHireAgent(Agent):
    def __init__(self, port=8004):
        super().__init__("pro_hire_advocate", port, "pro_hire_seed")
        # fund_agent_if_low(self.wallet.address())

        self.llm_agent = SimpleLLMAgent("pro_hire_advocate")
        self.protocol = Protocol()

        @self.protocol.on_message(model=DebateRequest)
        async def handle_debate(ctx: Context, sender: str, msg: DebateRequest):
            print(
                f"✅ {self.name}: Building pro-hire argument (round {msg.round_number})"
            )

            prompt = f"""
            You are a pro-hire advocate. Build a compelling argument for hiring this candidate.
            
            Intersection Analysis:
            {msg.intersection_analysis.analysis}
            Overall Compatibility: {msg.intersection_analysis.overall_compatibility}
            Skill Matches: {', '.join(msg.intersection_analysis.skill_matches)}
            Skill Gaps: {', '.join(msg.intersection_analysis.skill_gaps)}
            
            Previous Anti-Hire Argument: {msg.previous_argument}
            
            Build a strong pro-hire argument for round {msg.round_number}.
            Focus on the candidate's strengths and how they outweigh any concerns.
            
            Respond with ONLY a JSON object in this exact format:
            {{
                "argument": "<your pro-hire argument>",
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
                            position="pro",
                            argument=analysis.get(
                                "argument",
                                "Candidate has strong technical skills and relevant experience",
                            ),
                            confidence=analysis.get("confidence", 0.8),
                            key_points=analysis.get(
                                "key_points", ["Technical skills", "Experience level"]
                            ),
                        )
                    else:
                        response = DebateResponse(
                            position="pro",
                            argument="Candidate has strong technical skills and relevant experience",
                            confidence=0.8,
                            key_points=["Technical skills", "Experience level"],
                        )

                    print(f"✅ {self.name}: Pro-hire argument complete")
                    await ctx.send(sender, response)

                except Exception as e:
                    print(f"❌ {self.name}: Error processing response: {e}")
                    response = DebateResponse(
                        position="pro",
                        argument="Candidate has strong technical skills and relevant experience",
                        confidence=0.8,
                        key_points=["Technical skills", "Experience level"],
                    )
                    await ctx.send(sender, response) # send the response(information) to the user
            else:
                response = DebateResponse(
                    position="pro",
                    argument="Candidate has strong technical skills and relevant experience",
                    confidence=0.8,
                    key_points=["Technical skills", "Experience level"],
                )
                await ctx.send(sender, response)

        self.include(self.protocol)
