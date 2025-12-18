"""
Hiring Coordinator Agent
=======================

This agent coordinates the entire hiring process by managing communication between all other agents.
"""

import asyncio
from uagents import Agent, Context, Protocol
from uagents.setup import fund_agent_if_low
from .models import (
    JobParseRequest,
    JobParseResponse,
    ResumeParseRequest,
    ResumeParseResponse,
    IntersectionRequest,
    IntersectionResponse,
    DebateRequest,
    DebateResponse,
    DecisionRequest,
    DecisionResponse,
)


class HiringCoordinator(Agent):
    def __init__(self):
        super().__init__("hiring_coordinator", 8007, "coordinator_seed")
        fund_agent_if_low(self.wallet.address())

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

        # Add completion flags
        self.job_complete = False
        self.resume_complete = False
        self.intersection_complete = False
        self.debate_complete = False
        self.decision_complete = False

        # Add failure tracking
        self.api_failure_count = 0
        self.max_api_failures = 3  # Stop process after 3 API failures

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
            await self._check_and_proceed(ctx)

        @self.protocol.on_message(model=ResumeParseResponse)
        async def handle_resume_response(
            ctx: Context, sender: str, msg: ResumeParseResponse
        ):
            self.resume_analysis = msg
            self.resume_complete = True
            print(f"Resume Analysis: {msg.analysis}")
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
            await self._start_debate(ctx)

        @self.protocol.on_message(model=DebateResponse)
        async def handle_debate_response(
            ctx: Context, sender: str, msg: DebateResponse
        ):
            # Check for API failure responses (generic fallback responses)
            if (
                msg.argument
                == "Candidate has strong technical skills and relevant experience"
            ):
                self.api_failure_count += 1
                print(
                    f"⚠️ Detected API failure response (count: {self.api_failure_count})"
                )

                if self.api_failure_count >= self.max_api_failures:
                    print(
                        f"🛑 Stopping process due to {self.api_failure_count} API failures"
                    )
                    # Send error decision immediately
                    await self._handle_api_failure_shutdown(ctx)
                    return

            if msg.position == "pro":
                self.pro_arguments.append(msg)
                print(f"Pro-Hire Round {len(self.pro_arguments)}: {msg.argument}")
            else:
                self.anti_arguments.append(msg)
                print(f"Anti-Hire Round {len(self.anti_arguments)}: {msg.argument}")

            await self._continue_debate(ctx)

        @self.protocol.on_message(model=DecisionResponse)
        async def handle_decision_response(
            ctx: Context, sender: str, msg: DecisionResponse
        ):
            print(f"\n🎯 STEP 4: Making Final Decision")
            print("\n" + "=" * 60)
            print("FINAL HIRING DECISION")
            print("=" * 60)
            print(f"Decision: {msg.decision.upper()}")
            print(f"Confidence: {msg.confidence:.2f}")
            print(f"Reasoning: {msg.reasoning}")
            print(f"Key Factors: {', '.join(msg.key_factors)}")
            print("=" * 60)
            self.decision_complete = True

        self.include(self.protocol)

    async def _handle_api_failure_shutdown(self, ctx: Context):
        """Handle shutdown due to API failures"""
        print("🚨 API failure shutdown initiated")
        if self.websocket_manager:
            await self.websocket_manager.send_event(
                "System",
                "Process stopped due to API rate limit. Please try again later.",
            )
        # Mark process as complete to prevent further execution
        self.decision_complete = True

    async def _check_and_proceed(self, ctx: Context):
        """Check if we have both job and resume analysis, then proceed to intersection"""
        if self.job_complete and self.resume_complete:
            print(f"\n🔍 STEP 2: Evaluating Intersection")

            request = IntersectionRequest(
                job_analysis=self.job_analysis, resume_analysis=self.resume_analysis
            )
            await ctx.send(self.intersection_address, request)

    async def _start_debate(self, ctx: Context):
        """Start the debate between pro and anti hire agents"""
        print(f"\n⚖️ STEP 3: Conducting Debate")

        # Start with pro-hire argument
        pro_request = DebateRequest(
            intersection_analysis=self.intersection_analysis, round_number=1
        )
        await ctx.send(self.pro_hire_address, pro_request)

    async def _continue_debate(self, ctx: Context):
        """Continue the debate or end it and make decision"""
        total_rounds = len(self.pro_arguments) + len(self.anti_arguments)
        print(
            f"🔄 Continue debate check: Pro={len(self.pro_arguments)}, Anti={len(self.anti_arguments)}, Total={total_rounds}"
        )

        # Strict bounds checking to prevent extra rounds
        if (
            total_rounds < 6
            and len(self.pro_arguments) <= 3
            and len(self.anti_arguments) <= 3
        ):
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

            decision_request = DecisionRequest(
                pro_arguments=self.pro_arguments,
                anti_arguments=self.anti_arguments,
                intersection_analysis=self.intersection_analysis,
                candidate_name=self.candidate_name,
                job_title=self.job_title,
            )
            await ctx.send(self.decision_address, decision_request)
