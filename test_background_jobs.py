#!/usr/bin/env python3
"""
Test script for background jobs API.
Demonstrates how to use the background jobs API with status tracking.
"""

import asyncio
import json
import time
from typing import Any, Dict

import httpx


class BackgroundJobTester:
    """Test client for background jobs API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def create_article_job(
        self, article_id: int, processing_time: int = 5
    ) -> str:
        """Create an article processing job."""
        response = await self.client.post(
            f"{self.base_url}/api/v1/jobs/process-article",
            params={"article_id": article_id, "processing_time": processing_time},
        )
        response.raise_for_status()
        data = response.json()
        return data["data"]["job_id"]

    async def create_email_job(self, recipient: str, subject: str) -> str:
        """Create an email sending job."""
        response = await self.client.post(
            f"{self.base_url}/api/v1/jobs/send-email",
            params={"recipient": recipient, "subject": subject},
        )
        response.raise_for_status()
        data = response.json()
        return data["data"]["job_id"]

    async def create_report_job(
        self, report_type: str, date_range: str = "last_30_days"
    ) -> str:
        """Create a report generation job."""
        response = await self.client.post(
            f"{self.base_url}/api/v1/jobs/generate-report",
            params={"report_type": report_type, "date_range": date_range},
        )
        response.raise_for_status()
        data = response.json()
        return data["data"]["job_id"]

    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get job status."""
        response = await self.client.get(f"{self.base_url}/api/v1/jobs/{job_id}/status")
        response.raise_for_status()
        return response.json()["data"]

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a job."""
        response = await self.client.delete(f"{self.base_url}/api/v1/jobs/{job_id}")
        return response.status_code == 200

    async def list_jobs(self, status_filter: str = None) -> Dict[str, Any]:
        """List all jobs."""
        params = {}
        if status_filter:
            params["status_filter"] = status_filter

        response = await self.client.get(f"{self.base_url}/api/v1/jobs", params=params)
        response.raise_for_status()
        return response.json()["data"]

    async def list_all_jobs(self) -> Dict[str, Any]:
        """List all jobs using the dedicated /all endpoint."""
        response = await self.client.get(f"{self.base_url}/api/v1/jobs/all")
        response.raise_for_status()
        return response.json()["data"]

    async def monitor_job(self, job_id: str, max_wait: int = 30) -> Dict[str, Any]:
        """Monitor a job until completion or timeout."""
        start_time = time.time()

        while time.time() - start_time < max_wait:
            status = await self.get_job_status(job_id)
            print(f"Job {job_id}: {status['status']} ({status['progress']}%)")

            if status["status"] in ["completed", "failed", "cancelled"]:
                return status

            await asyncio.sleep(1)

        print(f"Job {job_id} monitoring timed out after {max_wait} seconds")
        return await self.get_job_status(job_id)


async def main():
    """Main test function."""
    tester = BackgroundJobTester()

    try:
        print("🚀 Testing Background Jobs API")
        print("=" * 50)

        # Test 1: Create and monitor article processing job
        print("\n📝 Test 1: Article Processing Job")
        article_job_id = await tester.create_article_job(
            article_id=123, processing_time=3
        )
        print(f"Created article job: {article_job_id}")

        final_status = await tester.monitor_job(article_job_id, max_wait=10)
        print(f"Final status: {json.dumps(final_status, indent=2)}")

        # Test 2: Create and monitor email job
        print("\n📧 Test 2: Email Sending Job")
        email_job_id = await tester.create_email_job(
            recipient="test@example.com", subject="Test Email from FastAPI"
        )
        print(f"Created email job: {email_job_id}")

        final_status = await tester.monitor_job(email_job_id, max_wait=10)
        print(f"Final status: {json.dumps(final_status, indent=2)}")

        # Test 3: Create report job and cancel it
        print("\n📊 Test 3: Report Generation Job (with cancellation)")
        report_job_id = await tester.create_report_job(
            report_type="monthly_sales", date_range="2024-01"
        )
        print(f"Created report job: {report_job_id}")

        # Wait a bit then cancel
        await asyncio.sleep(2)
        cancelled = await tester.cancel_job(report_job_id)
        print(f"Job cancelled: {cancelled}")

        final_status = await tester.get_job_status(report_job_id)
        print(f"Final status: {json.dumps(final_status, indent=2)}")

        # Test 4: List all jobs
        print("\n📋 Test 4: List All Jobs")
        all_jobs = await tester.list_jobs()
        print(f"Total jobs: {all_jobs['total']}")
        for job in all_jobs["jobs"]:
            print(f"  - {job['job_id']}: {job['status']} ({job['progress']}%)")

        # Test 5: List completed jobs only
        print("\n✅ Test 5: List Completed Jobs Only")
        completed_jobs = await tester.list_jobs(status_filter="completed")
        print(f"Completed jobs: {completed_jobs['total']}")
        for job in completed_jobs["jobs"]:
            print(f"  - {job['job_id']}: {job['job_type']}")

        # Test 6: List all jobs using dedicated /all endpoint
        print("\n📋 Test 6: List All Jobs (Dedicated Endpoint)")
        all_jobs_dedicated = await tester.list_all_jobs()
        print(f"Total jobs (dedicated endpoint): {all_jobs_dedicated['total']}")
        for job in all_jobs_dedicated["jobs"]:
            print(
                f"  - {job['job_id']}: {job['status']} ({job['progress']}%) - {job['job_type']}"
            )

        print("\n🎉 All tests completed successfully!")

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback

        traceback.print_exc()

    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
