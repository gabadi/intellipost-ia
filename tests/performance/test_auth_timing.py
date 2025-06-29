#!/usr/bin/env python3
"""
Performance testing script for authentication endpoints.

This script validates that authentication endpoints meet the <200ms requirement.
"""

import asyncio
import time
import statistics
import json
import sys
from typing import List, Dict, Any
from dataclasses import dataclass
import httpx
import argparse


@dataclass
class PerformanceResult:
    """Performance test result data."""
    endpoint: str
    method: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    median_response_time: float
    p95_response_time: float
    p99_response_time: float
    min_response_time: float
    max_response_time: float
    requests_per_second: float
    passed: bool


class AuthPerformanceTester:
    """Authentication endpoints performance tester."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize performance tester.

        Args:
            base_url: Base URL for API endpoints
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_user_email = f"perftest_{int(time.time())}@example.com"
        self.test_user_password = "PerfTest123!"

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()

    async def test_endpoint_performance(
        self,
        endpoint: str,
        method: str,
        payload: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
        num_requests: int = 100,
        concurrent_requests: int = 10
    ) -> PerformanceResult:
        """
        Test endpoint performance with concurrent requests.

        Args:
            endpoint: API endpoint path
            method: HTTP method
            payload: Request payload
            headers: Request headers
            num_requests: Total number of requests
            concurrent_requests: Number of concurrent requests

        Returns:
            PerformanceResult with timing statistics
        """
        response_times = []
        successful_requests = 0
        failed_requests = 0

        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(concurrent_requests)

        async def make_request():
            """Make single HTTP request and measure time."""
            nonlocal successful_requests, failed_requests

            async with semaphore:
                start_time = time.perf_counter()
                try:
                    response = await self.client.request(
                        method=method,
                        url=f"{self.base_url}{endpoint}",
                        json=payload,
                        headers=headers or {}
                    )
                    end_time = time.perf_counter()

                    response_time = (end_time - start_time) * 1000  # Convert to ms
                    response_times.append(response_time)

                    if response.status_code < 400:
                        successful_requests += 1
                    else:
                        failed_requests += 1

                except Exception as e:
                    end_time = time.perf_counter()
                    response_time = (end_time - start_time) * 1000
                    response_times.append(response_time)
                    failed_requests += 1
                    print(f"Request failed: {e}")

        # Execute all requests
        start_total = time.perf_counter()
        tasks = [make_request() for _ in range(num_requests)]
        await asyncio.gather(*tasks)
        end_total = time.perf_counter()

        # Calculate statistics
        if response_times:
            avg_time = statistics.mean(response_times)
            median_time = statistics.median(response_times)
            p95_time = self._percentile(response_times, 95)
            p99_time = self._percentile(response_times, 99)
            min_time = min(response_times)
            max_time = max(response_times)
        else:
            avg_time = median_time = p95_time = p99_time = min_time = max_time = 0

        total_time = end_total - start_total
        rps = num_requests / total_time if total_time > 0 else 0

        # Check if performance requirement is met (200ms)
        passed = avg_time < 200 and p95_time < 200

        return PerformanceResult(
            endpoint=endpoint,
            method=method,
            total_requests=num_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=avg_time,
            median_response_time=median_time,
            p95_response_time=p95_time,
            p99_response_time=p99_time,
            min_response_time=min_time,
            max_response_time=max_time,
            requests_per_second=rps,
            passed=passed
        )

    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        lower = int(index)
        upper = lower + 1
        weight = index - lower

        if upper >= len(sorted_data):
            return sorted_data[-1]

        return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight

    async def test_registration_performance(self, num_requests: int = 50) -> PerformanceResult:
        """Test user registration endpoint performance."""
        # Use unique emails for each request
        base_time = int(time.time())

        async def get_unique_payload(index: int):
            return {
                "email": f"perftest_{base_time}_{index}@example.com",
                "password": "PerfTest123!",
                "first_name": "Perf",
                "last_name": "Test"
            }

        response_times = []
        successful_requests = 0
        failed_requests = 0

        for i in range(num_requests):
            payload = await get_unique_payload(i)

            start_time = time.perf_counter()
            try:
                response = await self.client.post(
                    f"{self.base_url}/auth/register",
                    json=payload
                )
                end_time = time.perf_counter()

                response_time = (end_time - start_time) * 1000
                response_times.append(response_time)

                if response.status_code < 400:
                    successful_requests += 1
                else:
                    failed_requests += 1

            except Exception as e:
                end_time = time.perf_counter()
                response_time = (end_time - start_time) * 1000
                response_times.append(response_time)
                failed_requests += 1

        # Calculate statistics
        avg_time = statistics.mean(response_times) if response_times else 0
        median_time = statistics.median(response_times) if response_times else 0
        p95_time = self._percentile(response_times, 95)
        p99_time = self._percentile(response_times, 99)
        min_time = min(response_times) if response_times else 0
        max_time = max(response_times) if response_times else 0

        passed = avg_time < 200 and p95_time < 200

        return PerformanceResult(
            endpoint="/auth/register",
            method="POST",
            total_requests=num_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=avg_time,
            median_response_time=median_time,
            p95_response_time=p95_time,
            p99_response_time=p99_time,
            min_response_time=min_time,
            max_response_time=max_time,
            requests_per_second=0,  # Not applicable for sequential requests
            passed=passed
        )

    async def test_login_performance(self, num_requests: int = 100) -> PerformanceResult:
        """Test user login endpoint performance."""
        # First, register a test user
        register_payload = {
            "email": self.test_user_email,
            "password": self.test_user_password,
            "first_name": "Perf",
            "last_name": "Test"
        }

        await self.client.post(f"{self.base_url}/auth/register", json=register_payload)

        # Test login performance
        login_payload = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }

        return await self.test_endpoint_performance(
            endpoint="/auth/login",
            method="POST",
            payload=login_payload,
            num_requests=num_requests
        )

    async def test_token_refresh_performance(self, num_requests: int = 100) -> PerformanceResult:
        """Test token refresh endpoint performance."""
        # First, get tokens
        register_payload = {
            "email": self.test_user_email,
            "password": self.test_user_password,
            "first_name": "Perf",
            "last_name": "Test"
        }

        response = await self.client.post(f"{self.base_url}/auth/register", json=register_payload)
        tokens = response.json().get("tokens", {})
        refresh_token = tokens.get("refresh_token")

        if not refresh_token:
            raise Exception("Failed to get refresh token for testing")

        # Test refresh performance
        refresh_payload = {"refresh_token": refresh_token}

        return await self.test_endpoint_performance(
            endpoint="/auth/refresh",
            method="POST",
            payload=refresh_payload,
            num_requests=min(num_requests, 10)  # Limit to avoid token invalidation
        )

    async def test_protected_endpoint_performance(self, num_requests: int = 100) -> PerformanceResult:
        """Test protected endpoint access performance."""
        # First, get access token
        register_payload = {
            "email": self.test_user_email,
            "password": self.test_user_password,
            "first_name": "Perf",
            "last_name": "Test"
        }

        response = await self.client.post(f"{self.base_url}/auth/register", json=register_payload)
        tokens = response.json().get("tokens", {})
        access_token = tokens.get("access_token")

        if not access_token:
            raise Exception("Failed to get access token for testing")

        # Test protected endpoint performance
        headers = {"Authorization": f"Bearer {access_token}"}

        return await self.test_endpoint_performance(
            endpoint="/auth/me",
            method="GET",
            headers=headers,
            num_requests=num_requests
        )

    def print_result(self, result: PerformanceResult) -> None:
        """Print performance test result."""
        status = "✅ PASS" if result.passed else "❌ FAIL"

        print(f"\n{status} {result.method} {result.endpoint}")
        print(f"  Total Requests: {result.total_requests}")
        print(f"  Successful: {result.successful_requests}")
        print(f"  Failed: {result.failed_requests}")
        print(f"  Average Response Time: {result.avg_response_time:.2f}ms")
        print(f"  Median Response Time: {result.median_response_time:.2f}ms")
        print(f"  95th Percentile: {result.p95_response_time:.2f}ms")
        print(f"  99th Percentile: {result.p99_response_time:.2f}ms")
        print(f"  Min/Max: {result.min_response_time:.2f}ms / {result.max_response_time:.2f}ms")
        if result.requests_per_second > 0:
            print(f"  Requests/Second: {result.requests_per_second:.2f}")

        if not result.passed:
            print(f"  ⚠️  Performance requirement not met (>200ms average or 95th percentile)")


async def main():
    """Main performance testing function."""
    parser = argparse.ArgumentParser(description="Authentication Performance Tester")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL for API")
    parser.add_argument("--requests", type=int, default=100, help="Number of requests per test")
    parser.add_argument("--output", help="Output file for JSON results")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    print(f"🚀 Starting Authentication Performance Tests")
    print(f"📍 Target URL: {args.url}")
    print(f"📊 Requests per test: {args.requests}")
    print("=" * 60)

    results = []
    all_passed = True

    async with AuthPerformanceTester(args.url) as tester:
        try:
            # Test registration performance
            print("Testing user registration performance...")
            reg_result = await tester.test_registration_performance(args.requests // 2)
            results.append(reg_result)
            tester.print_result(reg_result)
            if not reg_result.passed:
                all_passed = False

            # Test login performance
            print("\nTesting user login performance...")
            login_result = await tester.test_login_performance(args.requests)
            results.append(login_result)
            tester.print_result(login_result)
            if not login_result.passed:
                all_passed = False

            # Test token refresh performance
            print("\nTesting token refresh performance...")
            refresh_result = await tester.test_token_refresh_performance(10)
            results.append(refresh_result)
            tester.print_result(refresh_result)
            if not refresh_result.passed:
                all_passed = False

            # Test protected endpoint performance
            print("\nTesting protected endpoint performance...")
            protected_result = await tester.test_protected_endpoint_performance(args.requests)
            results.append(protected_result)
            tester.print_result(protected_result)
            if not protected_result.passed:
                all_passed = False

        except Exception as e:
            print(f"\n❌ Performance testing failed: {e}")
            return 1

    # Summary
    print("\n" + "=" * 60)
    print("📈 PERFORMANCE TEST SUMMARY")
    print("=" * 60)

    passed_tests = sum(1 for result in results if result.passed)
    total_tests = len(results)

    print(f"Tests Passed: {passed_tests}/{total_tests}")

    if all_passed:
        print("✅ All authentication endpoints meet 200ms performance requirement!")
    else:
        print("❌ Some endpoints failed to meet 200ms performance requirement")

    # Save results to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump([
                {
                    "endpoint": r.endpoint,
                    "method": r.method,
                    "total_requests": r.total_requests,
                    "successful_requests": r.successful_requests,
                    "failed_requests": r.failed_requests,
                    "avg_response_time": r.avg_response_time,
                    "median_response_time": r.median_response_time,
                    "p95_response_time": r.p95_response_time,
                    "p99_response_time": r.p99_response_time,
                    "min_response_time": r.min_response_time,
                    "max_response_time": r.max_response_time,
                    "requests_per_second": r.requests_per_second,
                    "passed": r.passed
                }
                for r in results
            ], f, indent=2)
        print(f"📄 Results saved to {args.output}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
