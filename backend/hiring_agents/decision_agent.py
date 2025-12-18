"""
Decision Maker Agent
===================

This agent makes the final hiring decision based on the debate between pro and anti hire advocates.
"""

from uagents import Agent, Context, Protocol

# from uagents.setup import fund_agent_if_low
from .models import DecisionRequest, DecisionResponse, Reasoning
from .llm_client import SimpleLLMAgent
from db.supabase_client import HiringEvaluationsClient


class DecisionAgent(Agent):
    def __init__(self, port=8006):
        super().__init__("decision_maker", port, "decision_seed")
        # fund_agent_if_low(self.wallet.address())

        self.llm_agent = SimpleLLMAgent("decision_maker")
        self.db_client = HiringEvaluationsClient()
        self.protocol = Protocol()

        @self.protocol.on_message(model=DecisionRequest)
        async def handle_decision(ctx: Context, sender: str, msg: DecisionRequest):
            print(f"🎯 {self.name}: Making final hiring decision")

            # Format debate arguments for the prompt
            pro_args = "\n".join(
                [
                    f"Round {i+1}: {arg.argument}"
                    for i, arg in enumerate(msg.pro_arguments)
                ]
            )
            anti_args = "\n".join(
                [
                    f"Round {i+1}: {arg.argument}"
                    for i, arg in enumerate(msg.anti_arguments)
                ]
            )

            prompt = f"""
            You are the final decision maker for a hiring decision. Evaluate all the arguments and make a final, well-reasoned decision. Your reasoning should be comprehensive.
            
            Intersection Analysis:
            {msg.intersection_analysis.analysis}
            Overall Compatibility: {msg.intersection_analysis.overall_compatibility}
            
            Pro-Hire Arguments:
            {pro_args}
            
            Anti-Hire Arguments:
            {anti_args}
            
            Evaluate the strength of each side's arguments and make a final, well-reasoned decision. Your reasoning should be comprehensive.
            
            Respond with ONLY a JSON object in this exact format. The reasoning MUST be broken down into a detailed summary, and comprehensive lists of pros and cons.
            {{
                "decision": "<hire/no_hire>",
                "confidence": <0.0 to 1.0>,
                "reasoning": {{
                    "summary": "<A detailed, 2-3 sentence summary explaining the final verdict and its context.>",
                    "pros": ["<A comprehensive list of all key strengths and pro-hire arguments. Include at least 2-3 points.>", "<...more pros>"],
                    "cons": ["<A comprehensive list of all key weaknesses and anti-hire arguments. Include at least 2-3 points.>", "<...more cons>"]
                }},
                "key_factors": ["<The most important factors that drove the decision.>", "<...more factors>"]
            }}
            """

            result = await self.llm_agent.query_llm(prompt)

            if result["success"]:
                try:
                    analysis = self.llm_agent.parse_json_response(result["content"])

                    if analysis:
                        reasoning_data = analysis.get("reasoning", {})
                        response = DecisionResponse(
                            decision=analysis.get("decision", "no_hire"),
                            confidence=analysis.get("confidence", 0.7),
                            reasoning=Reasoning(
                                summary=reasoning_data.get(
                                    "summary", "Analysis incomplete."
                                ),
                                pros=reasoning_data.get("pros", []),
                                cons=reasoning_data.get("cons", []),
                            ),
                            key_factors=analysis.get("key_factors", ["N/A"]),
                        )
                    else:
                        # Default response if parsing fails
                        response = DecisionResponse(
                            decision="no_hire",
                            confidence=0.0,
                            reasoning=Reasoning(
                                summary="Failed to parse LLM response.",
                                pros=[],
                                cons=["Could not generate analysis from AI."],
                            ),
                            key_factors=["Parsing Error"],
                        )

                    print(f"🎯 {self.name}: Decision made")

                    # Save high-scoring candidates to database (85% or higher)
                    confidence_score = analysis.get("confidence", 0.7)
                    confidence_percentage = confidence_score * 100

                    print(
                        f"🎯 {self.name}: Confidence score: {confidence_score} ({confidence_percentage}%)"
                    )

                    if confidence_percentage >= 85.0:
                        print(
                            f"✅ {self.name}: Candidate qualifies for top_candidates (≥85%)"
                        )
                        await self._save_top_candidate(
                            msg, response, confidence_percentage
                        )
                    else:
                        print(
                            f"❌ {self.name}: Candidate doesn't qualify for top_candidates ({confidence_percentage}% < 85%)"
                        )

                    await ctx.send(sender, response)

                except Exception as e:
                    print(f"❌ {self.name}: Error processing response: {e}")
                    response = DecisionResponse(
                        decision="no_hire",
                        confidence=0.0,
                        reasoning=Reasoning(
                            summary="An exception occurred while processing the response.",
                            pros=[],
                            cons=[str(e)],
                        ),
                        key_factors=["Processing Error"],
                    )
                    await ctx.send(sender, response)
            else:
                # Default response if API call fails
                response = DecisionResponse(
                    decision="no_hire",
                    confidence=0.0,
                    reasoning=Reasoning(
                        summary="API Error.",
                        pros=[],
                        cons=[f"API Error: {result['content']}"],
                    ),
                    key_factors=["API Error"],
                )
                await ctx.send(sender, response)

        self.include(self.protocol)

    async def _save_top_candidate(
        self,
        request: DecisionRequest,
        response: DecisionResponse,
        confidence_percentage: float,
    ):
        """Save high-scoring candidates to the top_candidates table"""
        print(f"🔄 {self.name}: Starting _save_top_candidate method")
        try:
            # Extract data from the intersection analysis and decision
            intersection = request.intersection_analysis
            resume_analysis = (
                intersection.analysis if hasattr(intersection, "analysis") else ""
            )

            # Get candidate name and job title from the request
            candidate_name = request.candidate_name or "Unknown Candidate"
            job_title = request.job_title or "Unknown Position"

            print(f"📝 {self.name}: Candidate: {candidate_name}, Job: {job_title}")

            # Extract strengths and concerns from pro/anti arguments
            strengths = []
            concerns = []

            for arg in request.pro_arguments:
                strengths.extend(arg.key_points)

            for arg in request.anti_arguments:
                concerns.extend(arg.key_points)

            # Create summary from reasoning
            summary = response.reasoning.summary

            # Check if candidate already exists to avoid duplicates
            print(f"🔍 {self.name}: Checking if candidate already exists...")
            exists = await self.db_client.candidate_exists_for_job(
                candidate_name, job_title
            )
            print(f"🔍 {self.name}: Candidate exists check result: {exists}")
            if exists:
                print(
                    f"🔄 Candidate {candidate_name} already exists for {job_title}, skipping..."
                )
                return

            # Create the top candidate record
            top_candidate_data = {
                "resume_id": None,  # TODO: Pass resume_id from coordinator
                "evaluation_id": None,  # TODO: Pass evaluation_id from coordinator
                "job_id": None,  # TODO: Pass job_id from coordinator
                "candidate_name": candidate_name,
                "job_title": job_title,
                "position": job_title,  # Using job_title as position for now
                "overall_score": confidence_percentage,
                "confidence": response.confidence,
                "decision": response.decision.upper(),
                "summary": summary,
                "strengths": strengths,
                "concerns": concerns,
                "key_factors": response.key_factors,
                "skill_matches": intersection.skill_matches,
                "skill_gaps": intersection.skill_gaps,
                "experience_match": intersection.experience_match,
                "analysis": intersection.analysis,
            }

            print(f"💾 {self.name}: Attempting to save to database...")
            print(f"💾 {self.name}: Data keys: {list(top_candidate_data.keys())}")
            result = await self.db_client.create_top_candidate(**top_candidate_data)
            print(f"💾 {self.name}: Database save result: {result}")
            print(
                f"✅ Saved top candidate: {candidate_name} with score {confidence_percentage}%"
            )

        except Exception as e:
            print(f"❌ Error saving top candidate: {e}")
            # Don't fail the main decision process if saving fails
