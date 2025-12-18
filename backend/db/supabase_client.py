"""
Supabase Client for Hiring Evaluations
======================================

This module provides a client to interact with the resumes and hiring_evaluations tables in Supabase.
"""

import os
import json
from typing import Dict, List, Optional, Any
from supabase import create_client, Client
from datetime import datetime


SUPABASE_URL=os.getenv("SUPABASE_URL")
SUPABASE_KEY=os.getenv("SUPABASE_KEY")
# For testing purposes



print(SUPABASE_URL, SUPABASE_KEY)


class HiringEvaluationsClient:
    """Client for managing resumes and hiring evaluations in Supabase"""

    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """
        Initialize the Supabase client

        Args:
            supabase_url: Supabase project URL (defaults to SUPABASE_URL env var)
            supabase_key: Supabase anon key (defaults to SUPABASE_KEY env var)
        """
        self.supabase_url = supabase_url or SUPABASE_URL
        self.supabase_key = supabase_key or SUPABASE_KEY

        if not self.supabase_url or not self.supabase_key:
            raise ValueError(
                "Supabase URL and key must be provided or set as environment variables"
            )

        self.client: Client = create_client(self.supabase_url, self.supabase_key)

    # ===== RESUME METHODS =====

    async def create_resume(
        self,
        candidate_name: str,
        resume_text: str,
        original_filename: Optional[str] = None,
        skills: Optional[List[str]] = None,
        experience_years: Optional[int] = None,
        experience_level: Optional[str] = None,
        key_achievements: Optional[List[str]] = None,
        analysis_summary: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new resume record

        Args:
            candidate_name: Name of the candidate
            resume_text: Full text content of the resume
            original_filename: Original filename of the uploaded file
            skills: List of technical skills
            experience_years: Years of experience
            experience_level: Experience level (Junior, Mid-level, Senior)
            key_achievements: List of key achievements
            analysis_summary: Summary of the resume analysis

        Returns:
            Dictionary containing the created resume record
        """
        data = {
            "candidate_name": candidate_name,
            "resume_text": resume_text,
            "text_length": len(resume_text),
            "original_filename": original_filename,
            "skills": json.dumps(skills) if skills else None,
            "experience_years": experience_years,
            "experience_level": experience_level,
            "key_achievements": (
                json.dumps(key_achievements) if key_achievements else None
            ),
            "analysis_summary": analysis_summary,
        }

        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        response = self.client.table("resumes").insert(data).execute()

        if response.data:
            return response.data[0]
        else:
            raise Exception("Failed to create resume record")

    async def get_resume(self, resume_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a resume by ID

        Args:
            resume_id: UUID of the resume

        Returns:
            Dictionary containing the resume record or None if not found
        """
        response = (
            self.client.table("resumes").select("*").eq("id", resume_id).execute()
        )

        if response.data:
            return response.data[0]
        return None

    async def get_resumes_by_candidate(
        self, candidate_name: str
    ) -> List[Dict[str, Any]]:
        """
        Get all resumes for a specific candidate

        Args:
            candidate_name: Name of the candidate

        Returns:
            List of resume records
        """
        response = (
            self.client.table("resumes")
            .select("*")
            .eq("candidate_name", candidate_name)
            .execute()
        )
        return response.data or []

    async def search_resumes(
        self,
        skills: Optional[List[str]] = None,
        experience_level: Optional[str] = None,
        min_years: Optional[int] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Search resumes by criteria

        Args:
            skills: List of required skills
            experience_level: Required experience level
            min_years: Minimum years of experience
            limit: Maximum number of results

        Returns:
            List of matching resume records
        """
        query = self.client.table("resumes").select("*")

        if experience_level:
            query = query.eq("experience_level", experience_level)

        if min_years:
            query = query.gte("experience_years", min_years)

        # For skills, we'll need to use a more complex query
        # This is a simplified version - in production you might want full-text search

        response = query.limit(limit).execute()
        results = response.data or []

        # Filter by skills in Python (could be optimized with proper database queries)
        if skills:
            filtered_results = []
            for resume in results:
                resume_skills = (
                    json.loads(resume.get("skills", "[]"))
                    if resume.get("skills")
                    else []
                )
                resume_skills_lower = [skill.lower() for skill in resume_skills]
                required_skills_lower = [skill.lower() for skill in skills]

                if any(
                    req_skill in resume_skills_lower
                    for req_skill in required_skills_lower
                ):
                    filtered_results.append(resume)

            results = filtered_results

        return results

    async def get_recent_resumes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most recently uploaded resumes

        Args:
            limit: Maximum number of records to return

        Returns:
            List of recent resume records
        """
        response = (
            self.client.table("resumes")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data or []

    # ===== HIRING EVALUATION METHODS =====

    async def create_evaluation(
        self,
        resume_id: Optional[str],
        candidate_name: str,
        job_title: str,
        resume_summary: Optional[str] = None,
        resume_text: Optional[str] = None,
        job_summary: Optional[str] = None,
        intersection_score: Optional[float] = None,
        intersection_notes: Optional[str] = None,
        pro_arguments: Optional[List[Dict]] = None,
        anti_arguments: Optional[List[Dict]] = None,
        final_decision: Optional[str] = None,
        decision_confidence: Optional[float] = None,
        decision_reasoning: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new hiring evaluation record

        Args:
            resume_id: UUID of the resume being evaluated (optional for partial records)
            candidate_name: Name of the candidate
            job_title: Title of the job position
            resume_summary: Summary of the resume analysis
            resume_text: Full text content of the resume
            job_summary: Summary of the job requirements analysis
            intersection_score: Compatibility score (0.0 to 1.0)
            intersection_notes: Notes about the intersection analysis
            pro_arguments: List of pro-hire arguments
            anti_arguments: List of anti-hire arguments
            final_decision: Final decision ('HIRE' or 'REJECT')
            decision_confidence: Confidence in the decision (0.0 to 1.0)
            decision_reasoning: Reasoning for the final decision

        Returns:
            Dictionary containing the created record
        """
        data = {
            "resume_id": resume_id,
            "candidate_name": candidate_name,
            "job_title": job_title,
            "resume_summary": resume_summary,
            "resume_text": resume_text,
            "job_summary": job_summary,
            "intersection_score": intersection_score,
            "intersection_notes": intersection_notes,
            "pro_arguments": json.dumps(pro_arguments) if pro_arguments else None,
            "anti_arguments": json.dumps(anti_arguments) if anti_arguments else None,
            "final_decision": final_decision.upper() if final_decision else None,
            "decision_confidence": decision_confidence,
            "decision_reasoning": decision_reasoning,
        }

        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        response = self.client.table("hiring_evaluations").insert(data).execute()

        if response.data:
            return response.data[0]
        else:
            raise Exception("Failed to create evaluation record")

    async def get_evaluation(self, evaluation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a hiring evaluation by ID

        Args:
            evaluation_id: UUID of the evaluation

        Returns:
            Dictionary containing the evaluation record or None if not found
        """
        response = (
            self.client.table("hiring_evaluations")
            .select("*")
            .eq("id", evaluation_id)
            .execute()
        )

        if response.data:
            return response.data[0]
        return None

    async def get_evaluations_by_candidate(
        self, candidate_name: str
    ) -> List[Dict[str, Any]]:
        """
        Get all evaluations for a specific candidate

        Args:
            candidate_name: Name of the candidate

        Returns:
            List of evaluation records
        """
        response = (
            self.client.table("hiring_evaluations")
            .select("*")
            .eq("candidate_name", candidate_name)
            .execute()
        )
        return response.data or []

    async def get_evaluations_by_job(self, job_title: str) -> List[Dict[str, Any]]:
        """
        Get all evaluations for a specific job title

        Args:
            job_title: Title of the job position

        Returns:
            List of evaluation records
        """
        response = (
            self.client.table("hiring_evaluations")
            .select("*")
            .eq("job_title", job_title)
            .execute()
        )
        return response.data or []

    async def get_evaluations_by_decision(self, decision: str) -> List[Dict[str, Any]]:
        """
        Get all evaluations with a specific decision

        Args:
            decision: Decision to filter by ('HIRE' or 'REJECT')

        Returns:
            List of evaluation records
        """
        response = (
            self.client.table("hiring_evaluations")
            .select("*")
            .eq("final_decision", decision.upper())
            .execute()
        )
        return response.data or []

    async def get_recent_evaluations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most recent evaluations

        Args:
            limit: Maximum number of records to return

        Returns:
            List of recent evaluation records
        """
        response = (
            self.client.table("hiring_evaluations")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data or []

    async def update_evaluation(
        self, evaluation_id: str, **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing evaluation record

        Args:
            evaluation_id: UUID of the evaluation to update
            **kwargs: Fields to update

        Returns:
            Updated evaluation record or None if not found
        """
        # Convert decision to uppercase if provided
        if "final_decision" in kwargs:
            kwargs["final_decision"] = kwargs["final_decision"].upper()

        # Convert arguments to JSON if provided
        if "pro_arguments" in kwargs and kwargs["pro_arguments"]:
            kwargs["pro_arguments"] = json.dumps(kwargs["pro_arguments"])

        if "anti_arguments" in kwargs and kwargs["anti_arguments"]:
            kwargs["anti_arguments"] = json.dumps(kwargs["anti_arguments"])

        response = (
            self.client.table("hiring_evaluations")
            .update(kwargs)
            .eq("id", evaluation_id)
            .execute()
        )

        if response.data:
            return response.data[0]
        return None

    async def delete_evaluation(self, evaluation_id: str) -> bool:
        """
        Delete an evaluation record

        Args:
            evaluation_id: UUID of the evaluation to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        response = (
            self.client.table("hiring_evaluations")
            .delete()
            .eq("id", evaluation_id)
            .execute()
        )
        return len(response.data) > 0

    async def get_evaluation_stats(self) -> Dict[str, Any]:
        """
        Get statistics about hiring evaluations

        Returns:
            Dictionary containing various statistics
        """
        # Get total count
        total_response = (
            self.client.table("hiring_evaluations")
            .select("id", count="exact")
            .execute()
        )
        total_count = total_response.count or 0

        # Get hire count
        hire_response = (
            self.client.table("hiring_evaluations")
            .select("id", count="exact")
            .eq("final_decision", "HIRE")
            .execute()
        )
        hire_count = hire_response.count or 0

        # Get reject count
        reject_response = (
            self.client.table("hiring_evaluations")
            .select("id", count="exact")
            .eq("final_decision", "REJECT")
            .execute()
        )
        reject_count = reject_response.count or 0

        # Calculate hire rate
        hire_rate = (hire_count / total_count * 100) if total_count > 0 else 0

        return {
            "total_evaluations": total_count,
            "hire_count": hire_count,
            "reject_count": reject_count,
            "hire_rate_percentage": round(hire_rate, 2),
            "average_intersection_score": None,  # Would need a more complex query
            "average_decision_confidence": None,  # Would need a more complex query
        }

    # --- Job Postings Table Helpers ---

    async def create_job_posting(
        self,
        title: str,
        summary: str = None,
        description: str = None,
        skills: list = None,
        location: str = None,
        employment_type: str = None,
        salary: str = None,
        requirements: str = None,
        status: str = "ACTIVE",
        applicants_count: int = 0,
    ) -> dict:
        """
        Create a new job posting.
        """
        data = {
            "title": title,
            "summary": summary,
            "description": description,
            "skills": skills,
            "location": location,
            "employment_type": employment_type,
            "salary": salary,
            "requirements": requirements,
            "status": status,
            "applicants_count": applicants_count,
        }
        data = {k: v for k, v in data.items() if v is not None}
        response = self.client.table("job_postings").insert(data).execute()
        if response.data:
            return response.data[0]
        else:
            raise Exception("Failed to create job posting")

    async def get_job_posting(self, job_id: str) -> dict:
        """
        Get a job posting by ID.
        """
        response = (
            self.client.table("job_postings").select("*").eq("id", job_id).execute()
        )
        if response.data:
            return response.data[0]
        return None

    async def list_job_postings(self, status: str = "ACTIVE", limit: int = 20) -> list:
        """
        List job postings, optionally filtered by status.
        """
        query = self.client.table("job_postings").select("*")
        if status:
            query = query.eq("status", status)
        response = query.order("posted_at", desc=True).limit(limit).execute()
        return response.data or []

    async def update_job_posting(self, job_id: str, **kwargs) -> dict:
        """
        Update a job posting by ID.
        """
        response = (
            self.client.table("job_postings").update(kwargs).eq("id", job_id).execute()
        )
        if response.data:
            return response.data[0]
        return None

    async def delete_job_posting(self, job_id: str) -> bool:
        """
        Delete a job posting by ID.
        """
        response = self.client.table("job_postings").delete().eq("id", job_id).execute()
        return len(response.data) > 0

    # --- Top Candidates Table Helpers ---

    async def create_top_candidate(
        self,
        resume_id: Optional[str],
        evaluation_id: Optional[str],
        candidate_name: str,
        job_title: str,
        job_id: Optional[str],
        position: str,
        overall_score: float,
        confidence: float,
        decision: str = "HIRE",
        email: Optional[str] = None,
        phone: Optional[str] = None,
        location: Optional[str] = None,
        experience_years: Optional[int] = None,
        experience_level: Optional[str] = None,
        education: Optional[str] = None,
        skills: Optional[List[Dict]] = None,
        summary: Optional[str] = None,
        strengths: Optional[List[str]] = None,
        concerns: Optional[List[str]] = None,
        recommendation: Optional[str] = None,
        key_factors: Optional[List[str]] = None,
        achievements: Optional[List[str]] = None,
        skill_matches: Optional[List[str]] = None,
        skill_gaps: Optional[List[str]] = None,
        experience_match: Optional[str] = None,
        analysis: Optional[str] = None,
        applied_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Create a new top candidate record for candidates scoring above 85%.
        """
        print(f"🏗️ DB: create_top_candidate called with score: {overall_score}")
        print(f"🏗️ DB: Candidate: {candidate_name}, Job: {job_title}")

        # Validate score threshold
        if overall_score < 85.0:
            print(f"❌ DB: Score validation failed: {overall_score} < 85.0")
            raise ValueError(f"Overall score must be >= 85.0, got {overall_score}")
        print(f"✅ DB: Score validation passed: {overall_score} >= 85.0")

        data = {
            "resume_id": resume_id,
            "evaluation_id": evaluation_id,
            "candidate_name": candidate_name,
            "job_title": job_title,
            "job_id": job_id,
            "position": position,
            "overall_score": overall_score,
            "decision": decision.upper() if decision else "HIRE",
            "confidence": confidence,
            "email": email,
            "phone": phone,
            "location": location,
            "experience_years": experience_years,
            "experience_level": experience_level,
            "education": education,
            "skills": json.dumps(skills) if skills else None,
            "summary": summary,
            "strengths": json.dumps(strengths) if strengths else None,
            "concerns": json.dumps(concerns) if concerns else None,
            "recommendation": recommendation,
            "key_factors": json.dumps(key_factors) if key_factors else None,
            "achievements": json.dumps(achievements) if achievements else None,
            "skill_matches": json.dumps(skill_matches) if skill_matches else None,
            "skill_gaps": json.dumps(skill_gaps) if skill_gaps else None,
            "experience_match": experience_match,
            "analysis": analysis,
            "applied_date": applied_date.isoformat() if applied_date else None,
        }

        # Remove None values
        print(f"🧹 DB: Data before cleaning: {len(data)} fields")
        data = {k: v for k, v in data.items() if v is not None}
        print(f"🧹 DB: Data after cleaning: {len(data)} fields")
        print(f"📝 DB: Final data keys: {list(data.keys())}")

        print(f"🚀 DB: Inserting into top_candidates table...")
        response = self.client.table("top_candidates").insert(data).execute()
        print(f"📥 DB: Response received from Supabase")

        if response.data:
            print(f"✅ DB: Successfully created top candidate record")
            print(f"📄 DB: Record ID: {response.data[0].get('id', 'Unknown')}")
            return response.data[0]
        else:
            print(f"❌ DB: Failed to create record - no data returned")
            print(f"❌ DB: Response: {response}")
            raise Exception("Failed to create top candidate record")

    async def get_top_candidates(
        self, limit: int = 20, job_id: Optional[str] = None, min_score: float = 85.0
    ) -> List[Dict[str, Any]]:
        """
        Get top candidates sorted by score (highest first).
        """
        query = self.client.table("top_candidates").select("*")

        if job_id:
            query = query.eq("job_id", job_id)

        query = query.gte("overall_score", min_score)

        response = query.order("overall_score", desc=True).limit(limit).execute()
        return response.data or []

    async def get_top_candidate(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific top candidate by ID.
        """
        response = (
            self.client.table("top_candidates")
            .select("*")
            .eq("id", candidate_id)
            .execute()
        )

        if response.data:
            return response.data[0]
        return None

    async def update_top_candidate(
        self, candidate_id: str, **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing top candidate record.
        """
        # Convert decision to uppercase if provided
        if "decision" in kwargs:
            kwargs["decision"] = kwargs["decision"].upper()

        # Convert lists to JSON if provided
        json_fields = [
            "skills",
            "strengths",
            "concerns",
            "key_factors",
            "achievements",
            "skill_matches",
            "skill_gaps",
        ]
        for field in json_fields:
            if field in kwargs and kwargs[field]:
                kwargs[field] = json.dumps(kwargs[field])

        response = (
            self.client.table("top_candidates")
            .update(kwargs)
            .eq("id", candidate_id)
            .execute()
        )

        if response.data:
            return response.data[0]
        return None

    async def delete_top_candidate(self, candidate_id: str) -> bool:
        """
        Delete a top candidate record.
        """
        response = (
            self.client.table("top_candidates")
            .delete()
            .eq("id", candidate_id)
            .execute()
        )
        return len(response.data) > 0

    async def get_top_candidates_by_job(
        self, job_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get top candidates for a specific job.
        """
        response = (
            self.client.table("top_candidates")
            .select("*")
            .eq("job_id", job_id)
            .order("overall_score", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data or []

    async def candidate_exists_for_job(
        self, candidate_name: str, job_title: str
    ) -> bool:
        """
        Check if a candidate already exists for a specific job to avoid duplicates.
        """
        response = (
            self.client.table("top_candidates")
            .select("id")
            .eq("candidate_name", candidate_name)
            .eq("job_title", job_title)
            .execute()
        )
        return len(response.data) > 0


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test_client():
        # Initialize client (you'll need to set environment variables)
        client = HiringEvaluationsClient()

        # Create a test evaluation
        evaluation = await client.create_evaluation(
            resume_id="some-resume-id",
            candidate_name="John Doe",
            job_title="Software Engineer",
            resume_summary="Experienced developer with Python and JavaScript skills",
            job_summary="Mid-level position requiring Python and React",
            intersection_score=0.85,
            intersection_notes="Strong technical skills match",
            pro_arguments=[
                {"argument": "Strong technical background", "confidence": 0.9}
            ],
            anti_arguments=[
                {"argument": "Limited leadership experience", "confidence": 0.6}
            ],
            final_decision="HIRE",
            decision_confidence=0.8,
            decision_reasoning="Candidate's technical skills outweigh concerns",
        )

        print(f"Created evaluation: {evaluation['id']}")

        # Get statistics
        stats = await client.get_evaluation_stats()
        print(f"Statistics: {stats}")

        # Create a job posting
        job_posting = await client.create_job_posting(
            title="Frontend Developer Intern",
            summary="Craft clean, responsive UIs for AI dashboards using React and collaborate with designers and engineers.",
            description="Craft clean, responsive UIs for AI dashboards using React and collaborate with designers and engineers.",
            skills=["React", "JavaScript", "Tailwind CSS", "UI/UX"],
            location="Remote",
            employment_type="Full-time",
            salary="$30,000 - $40,000",
            requirements="3+ years of experience in React development",
        )
        print(f"Created job posting: {job_posting['id']}")

        # List job postings
        jobs = await client.list_job_postings()
        print(f"List of job postings: {jobs}")

        # Get a job posting by ID
        job = await client.get_job_posting(job_id="...")
        print(f"Retrieved job posting: {job}")

        # Update a job posting
        updated_job = await client.update_job_posting(job_id="...", status="INACTIVE")
        print(f"Updated job posting: {updated_job}")

        # Delete a job posting
        deleted = await client.delete_job_posting(job_id="...")
        print(f"Job posting deleted: {deleted}")

    # Uncomment to test
    # asyncio.run(test_client())
