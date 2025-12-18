"""
Main Hiring System
=================

Main execution file for the uAgents hiring system.
Coordinates all agents and provides the entry point.
"""

import asyncio
from uagents import Agent, Context, Protocol

# from uagents.setup import fund_agent_if_low
from hiring_agents import (
    JobParserAgent,
    ResumeParserAgent,
    IntersectionAgent,
    ProHireAgent,
    AntiHireAgent,
    DecisionAgent,
)
from hiring_agents.models import (
    JobParseRequest,
    ResumeParseRequest,
    IntersectionRequest,
    DebateRequest,
    DecisionRequest,
    JobParseResponse,
    ResumeParseResponse,
    IntersectionResponse,
    DebateResponse,
    DecisionResponse,
    TranscriptEntry,
    FinalResult,
)


# Main Coordinator
class HiringCoordinator(Agent):
    def __init__(self, event_emitter=None, base_port=8007):
        super().__init__("hiring_coordinator", base_port, "coordinator_seed")
        # fund_agent_if_low(self.wallet.address())  # Disabled for local operation

        # Store event emitter for real-time updates
        self.event_emitter = event_emitter

        # Store agent addresses
        self.job_parser_address = None
        self.resume_parser_address = None
        self.intersection_address = None
        self.pro_hire_address = None
        self.anti_hire_address = None
        self.decision_address = None

        # Store results
        self.job_analysis = None
        self.resume_analysis = None
        self.intersection_analysis = None
        self.pro_arguments = []
        self.anti_arguments = []
        self.final_decision = None

        # Add completion flags
        self.job_complete = False
        self.resume_complete = False
        self.intersection_complete = False
        self.debate_complete = False
        self.decision_complete = False

        # Add flag to prevent duplicate requests
        self.initial_requests_sent = False

        # Store initial data
        self.resume_content = None
        self.job_description = None
        self.candidate_name = None
        self.job_title = None

        self.protocol = Protocol()

        # Timer to send initial requests after startup
        @self.on_interval(period=3.0)
        async def send_initial_requests(ctx: Context):
            if (
                not self.initial_requests_sent
                and self.job_description
                and self.resume_content
            ):
                print("🤖 Starting Hiring Evaluation Process")
                print("=" * 60)
                print("\n📋 STEP 1: Parsing Job and Resume")

                # Send initial requests
                job_request = JobParseRequest(
                    job_description=self.job_description, job_title=self.job_title
                )
                await ctx.send(self.job_parser_address, job_request)

                resume_request = ResumeParseRequest(
                    resume_content=self.resume_content,
                    candidate_name=self.candidate_name,
                )
                await ctx.send(self.resume_parser_address, resume_request)

                # Mark as sent to prevent duplicates
                self.initial_requests_sent = True

        # Handle responses from each agent
        @self.protocol.on_message(model=JobParseResponse)
        async def handle_job_response(ctx: Context, sender: str, msg: JobParseResponse):
            self.job_analysis = msg
            self.job_complete = True
            print(f"Job Analysis: {msg.analysis}")

            # Emit WebSocket event
            if self.event_emitter:
                await self.event_emitter("Job Parser Agent", msg.analysis, "parsing")

            await self._check_and_proceed(ctx)

        @self.protocol.on_message(model=ResumeParseResponse)
        async def handle_resume_response(
            ctx: Context, sender: str, msg: ResumeParseResponse
        ):
            self.resume_analysis = msg
            self.resume_complete = True
            print(f"Resume Analysis: {msg.analysis}")

            # Emit WebSocket event
            if self.event_emitter:
                await self.event_emitter("Resume Parser Agent", msg.analysis, "parsing")

            await self._check_and_proceed(ctx)

        @self.protocol.on_message(model=IntersectionResponse)
        async def handle_intersection_response(
            ctx: Context, sender: str, msg: IntersectionResponse
        ):
            self.intersection_analysis = msg
            self.intersection_complete = True
            print(f"\n🔍 STEP 2: Evaluating Intersection")
            print(f"Intersection Analysis: {msg.analysis}")
            print(f"Overall Compatibility: {msg.overall_compatibility:.2f}")

            # Emit WebSocket event
            if self.event_emitter:
                await self.event_emitter(
                    "Intersection Evaluator", msg.analysis, "evaluation", "evaluation"
                )

            await self._start_debate(ctx)

        @self.protocol.on_message(model=DebateResponse)
        async def handle_debate_response(
            ctx: Context, sender: str, msg: DebateResponse
        ):
            if msg.position == "pro":
                self.pro_arguments.append(msg)
                print(f"Pro-Hire Round {len(self.pro_arguments)}: {msg.argument}")

                # Emit WebSocket event
                if self.event_emitter:
                    await self.event_emitter(
                        "Pro-Hire Advocate", msg.argument, "debate", "pro"
                    )
            else:
                self.anti_arguments.append(msg)
                print(f"Anti-Hire Round {len(self.anti_arguments)}: {msg.argument}")

                # Emit WebSocket event
                if self.event_emitter:
                    await self.event_emitter(
                        "Anti-Hire Advocate", msg.argument, "debate", "anti"
                    )

            await self._continue_debate(ctx)

        @self.protocol.on_message(model=DecisionResponse)
        async def handle_decision_response(
            ctx: Context, sender: str, msg: DecisionResponse
        ):
            self.final_decision = msg
            print(f"\n🎯 STEP 4: Making Final Decision")
            print("\n" + "=" * 60)
            print("FINAL HIRING DECISION")
            print("=" * 60)
            print(f"Decision: {msg.decision.upper()}")
            print(f"Confidence: {msg.confidence:.2f}")
            print(f"Reasoning: {msg.reasoning}")
            print(f"Key Factors: {', '.join(msg.key_factors)}")
            print("=" * 60)

            # Emit WebSocket event
            if self.event_emitter:
                decision_summary = f"Decision: {msg.decision.upper()}\nConfidence: {msg.confidence:.2f}\nReasoning: {msg.reasoning}"
                await self.event_emitter(
                    "Decision Agent", decision_summary, "decision", "decision"
                )

            self.decision_complete = True

        self.include(self.protocol)

    async def _check_and_proceed(self, ctx: Context):
        """Check if we have both job and resume analysis, then proceed to intersection"""
        if self.job_complete and self.resume_complete:
            print(f"\n🔍 STEP 2: Evaluating Intersection")

            # Emit step transition event
            if self.event_emitter:
                await self.event_emitter(
                    "System", "Starting intersection evaluation", "intersection"
                )

            request = IntersectionRequest(
                job_analysis=self.job_analysis, resume_analysis=self.resume_analysis
            )
            await ctx.send(self.intersection_address, request)

    async def _start_debate(self, ctx: Context):
        """Start the debate between pro and anti hire agents"""
        print(f"\n⚖️ STEP 3: Conducting Debate")

        # Emit step transition event
        if self.event_emitter:
            await self.event_emitter("System", "Starting debate phase", "debate")

        # Start with pro-hire argument
        pro_request = DebateRequest(
            intersection_analysis=self.intersection_analysis, round_number=1
        )
        await ctx.send(self.pro_hire_address, pro_request)

    async def _continue_debate(self, ctx: Context):
        """Continue the debate or end it and make decision"""
        total_rounds = len(self.pro_arguments) + len(self.anti_arguments)

        if total_rounds < 6:  # 3 rounds each = 6 total
            # Continue debate
            if len(self.pro_arguments) > len(self.anti_arguments):
                # Anti-hire's turn
                round_num = len(self.anti_arguments) + 1
                previous_arg = self.pro_arguments[-1].argument

                anti_request = DebateRequest(
                    intersection_analysis=self.intersection_analysis,
                    round_number=round_num,
                    previous_argument=previous_arg,
                )
                await ctx.send(self.anti_hire_address, anti_request)
            else:
                # Pro-hire's turn
                round_num = len(self.pro_arguments) + 1
                previous_arg = (
                    self.anti_arguments[-1].argument if self.anti_arguments else ""
                )

                pro_request = DebateRequest(
                    intersection_analysis=self.intersection_analysis,
                    round_number=round_num,
                    previous_argument=previous_arg,
                )
                await ctx.send(self.pro_hire_address, pro_request)
        else:
            # Debate complete, make decision
            print(f"\n🎯 STEP 4: Making Final Decision")

            # Emit step transition event
            if self.event_emitter:
                await self.event_emitter(
                    "System", "Making final hiring decision", "decision"
                )

            decision_request = DecisionRequest(
                pro_arguments=self.pro_arguments,
                anti_arguments=self.anti_arguments,
                intersection_analysis=self.intersection_analysis,
            )
            await ctx.send(self.decision_address, decision_request)


# Main execution function
async def run_hiring_system(
    resume_content: str,
    job_description: str,
    candidate_name: str,
    job_title: str,
    event_emitter=None,
):
    """Run the complete hiring system with uAgents"""
    print("🚀 Starting uAgents Hiring System")
    print("=" * 60)

    # Use dynamic ports to avoid conflicts
    import random

    base_port = random.randint(9000, 9500)

    # Create all agents with dynamic ports
    job_parser = JobParserAgent(base_port + 1)
    resume_parser = ResumeParserAgent(base_port + 2)
    intersection_evaluator = IntersectionAgent(base_port + 3)
    pro_hire = ProHireAgent(base_port + 4)
    anti_hire = AntiHireAgent(base_port + 5)
    decision_maker = DecisionAgent(base_port + 6)
    coordinator = HiringCoordinator(event_emitter, base_port + 7)

    # Start all agents in background tasks
    tasks = []
    try:
        job_parser_task = asyncio.create_task(job_parser.run_async())
        tasks.append(job_parser_task)
        resume_parser_task = asyncio.create_task(resume_parser.run_async())
        tasks.append(resume_parser_task)
        intersection_task = asyncio.create_task(intersection_evaluator.run_async())
        tasks.append(intersection_task)
        pro_hire_task = asyncio.create_task(pro_hire.run_async())
        tasks.append(pro_hire_task)
        anti_hire_task = asyncio.create_task(anti_hire.run_async())
        tasks.append(anti_hire_task)
        decision_task = asyncio.create_task(decision_maker.run_async())
        tasks.append(decision_task)
        coordinator_task = asyncio.create_task(coordinator.run_async())
        tasks.append(coordinator_task)

        # Wait for initialization
        print("⏳ Waiting for agents to initialize...")
        await asyncio.sleep(5)

        # Store addresses
        coordinator.job_parser_address = job_parser.address
        coordinator.resume_parser_address = resume_parser.address
        coordinator.intersection_address = intersection_evaluator.address
        coordinator.pro_hire_address = pro_hire.address
        coordinator.anti_hire_address = anti_hire.address
        coordinator.decision_address = decision_maker.address

        # Store initial data
        coordinator.resume_content = resume_content
        coordinator.job_description = job_description
        coordinator.candidate_name = candidate_name
        coordinator.job_title = job_title

        # Wait for decision to complete with timeout
        print("⏳ Waiting for hiring process to complete...")
        timeout_counter = 0
        max_timeout = 120  # 2 minutes max

        while not coordinator.decision_complete and timeout_counter < max_timeout:
            await asyncio.sleep(1)
            timeout_counter += 1

        if timeout_counter >= max_timeout:
            print("⚠️ Hiring process timed out")
            if event_emitter:
                await event_emitter("System", "Process timed out", "error")
            return None

        print("✅ Hiring process finished.")

        # Construct the full transcript
        transcript = []

        # 1. Add Intersection Agent's output
        if coordinator.intersection_analysis:
            transcript.append(
                TranscriptEntry(
                    agent_name="Intersection Evaluator",
                    position="evaluation",
                    content=coordinator.intersection_analysis.analysis,
                    details=coordinator.intersection_analysis.model_dump(),
                )
            )

        # 2. Add Debate arguments
        pro_idx, anti_idx = 0, 0
        num_pro = len(coordinator.pro_arguments)
        num_anti = len(coordinator.anti_arguments)
        while pro_idx < num_pro or anti_idx < num_anti:
            if pro_idx < num_pro:
                arg = coordinator.pro_arguments[pro_idx]
                transcript.append(
                    TranscriptEntry(
                        agent_name="Pro-Hire Advocate",
                        position="pro",
                        content=arg.argument,
                        details=arg.model_dump(),
                    )
                )
                pro_idx += 1
            if anti_idx < num_anti:
                arg = coordinator.anti_arguments[anti_idx]
                transcript.append(
                    TranscriptEntry(
                        agent_name="Anti-Hire Advocate",
                        position="anti",
                        content=arg.argument,
                        details=arg.model_dump(),
                    )
                )
                anti_idx += 1

        # Construct and return the final comprehensive result
        if coordinator.final_decision:
            return FinalResult(
                resume_analysis=coordinator.resume_analysis,
                job_analysis=coordinator.job_analysis,
                intersection_analysis=coordinator.intersection_analysis,
                decision=coordinator.final_decision,
                transcript=transcript,
            )
        return None

    except Exception as e:
        print(f"❌ Error in hiring system: {e}")
        if event_emitter:
            await event_emitter("System", f"Error: {str(e)}", "error")
        return None

    finally:
        # Minimal cleanup that won't interfere with server
        print("🧹 Cleaning up agents...")

        # Don't actually wait for or cancel anything - just let them finish naturally
        # This prevents any CancelledError from propagating to the server
        try:
            print(f"✅ Leaving {len(tasks)} agent tasks to finish naturally")
        except:
            pass

        print("✅ Agent cleanup completed (non-blocking)")


# Test data and main execution
if __name__ == "__main__":
    # Only run test data if explicitly requested (commented out for production)
    print("🔧 main.py is now configured to work with the API server.")
    print("📡 To test the hiring system, use the API server at http://localhost:8080")
    print("🚀 Start the API server with: python api_server.py")

    # Uncomment below for standalone testing with dummy data:

    # # Test data
    # resume_content = """
    # Software Engineer with 3 years of experience in web development.
    # Proficient in Python, JavaScript, React, and Node.js.
    # Experience with MongoDB and AWS services.
    # Led development of multiple production applications.
    # Strong problem-solving skills and experience with agile methodologies.
    # """
    #
    # job_description = """
    # Mid-level Software Engineer position.
    # Required skills: Python, JavaScript, React.
    # Preferred skills: Node.js, MongoDB, AWS.
    # Experience with microservices and cloud deployment preferred.
    # Looking for someone with 2-5 years of experience.
    # """
    #
    # # Run the hiring system
    # asyncio.run(run_hiring_system(
    #     resume_content=resume_content,
    #     job_description=job_description,
    #     candidate_name="John Doe",
    #     job_title="Software Engineer"
    # ))
