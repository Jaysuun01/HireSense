"""
Resume Parser Agent
==================

This agent parses resumes using ASI:One LLM to extract candidate information.
"""

from uagents import Agent, Context, Protocol
# from uagents.setup import fund_agent_if_low  # Disabled to avoid network calls
from .models import ResumeParseRequest, ResumeParseResponse
#Model for resume parsing
from .llm_client import SimpleLLMAgent


class ResumeParserAgent(Agent):
    def __init__(self, port=8002):
        super().__init__("resume_parser", port, "resume_parser_seed")
        # fund_agent_if_low(self.wallet.address())  # Disabled for local operation

        self.llm_agent = SimpleLLMAgent("resume_parser")
        self.protocol = Protocol()

        @self.protocol.on_message(model=ResumeParseRequest)
        async def handle_resume_parse(
            ctx: Context, sender: str, msg: ResumeParseRequest # the information for the LLM(Context)
        ):
            print(f"📄 {self.name}: Parsing resume for {msg.candidate_name}")
            #The content and rules for the LLM(Protocol)
            prompt = f"""
            Analyze the following resume and extract key information.
            
            Candidate Name: {msg.candidate_name}
            Resume Content:
            {msg.resume_content}
            
            Extract and analyze:
            1. Technical skills (programming languages, frameworks, tools)
            2. Years of experience
            3. Experience level (Junior, Mid-level, Senior)
            4. Key achievements and accomplishments
            
            Respond with ONLY a JSON object in this exact format:
            {{
                "skills": ["skill1", "skill2", "skill3"],
                "experience_years": <number>,
                "experience_level": "<Junior/Mid-level/Senior>",
                "key_achievements": ["achievement1", "achievement2"],
                "analysis": "<brief analysis of the candidate's profile>"
            }}
            """

            result = await self.llm_agent.query_llm(prompt)

            if result["success"]:
                try:
                    analysis = self.llm_agent.parse_json_response(result["content"])

                    if analysis:
                        response = ResumeParseResponse(
                            candidate_name=msg.candidate_name,
                            skills=analysis.get(
                                "skills", ["python", "javascript", "react"]
                            ),
                            experience_years=analysis.get("experience_years", 3),
                            experience_level=analysis.get(
                                "experience_level", "Mid-level"
                            ),
                            key_achievements=analysis.get(
                                "key_achievements", ["Led development team"]
                            ),
                            analysis=analysis.get(
                                "analysis", "Resume analysis completed"
                            ),
                        )
                    else:
                        response = ResumeParseResponse(
                            candidate_name=msg.candidate_name,
                            skills=["python", "javascript", "react"],
                            experience_years=3,
                            experience_level="Mid-level",
                            key_achievements=["Led development team"],
                            analysis="Failed to parse LLM response, using defaults",
                        )

                    print(f"📄 {self.name}: Resume parsing complete")
                    await ctx.send(sender, response)

                except Exception as e:
                    print(f"❌ {self.name}: Error processing response: {e}")
                    response = ResumeParseResponse(
                        candidate_name=msg.candidate_name,
                        skills=["python", "javascript", "react"],
                        experience_years=3,
                        experience_level="Mid-level",
                        key_achievements=["Led development team"],
                        analysis="Error processing response, using defaults",
                    )
                    await ctx.send(sender, response)
            else:
                response = ResumeParseResponse(
                    candidate_name=msg.candidate_name,
                    skills=["python", "javascript", "react"],
                    experience_years=3,
                    experience_level="Mid-level",
                    key_achievements=["Led development team"],
                    analysis=f"API Error: {result['content']}",
                )
                await ctx.send(sender, response)

        self.include(self.protocol)
