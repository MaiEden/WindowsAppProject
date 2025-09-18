# geo_client_tester.py
import asyncio
from typing import List, Tuple
from geocoding_client import get_address, get_address_async


class GeoClientTester:
    """Simple tester that demonstrates sync and async usage and prints results."""
    def __init__(self, samples: List[Tuple[float, float]]):
        """Store a list of (lat, lon) samples to test."""
        self.samples = samples

    def run_sync(self):
        """
            Iterate samples and call get_address(lat, lon)
            print formatted addresses or errors.
        """
        print("=== Sync tests ===")
        for lat, lon in self.samples:
            try:
                result = get_address(lat, lon)
                print(f"[SYNC] ({lat:.5f}, {lon:.5f}) => {result.get('formatted_address')}")
            except Exception as e:
                print(f"[SYNC] ({lat:.5f}, {lon:.5f}) ERROR: {e}")

    async def run_async(self):
        """
            Iterate samples and await get_address_async(lat, lon)
            print results or errors.
        """
        print("=== Async tests ===")
        for lat, lon in self.samples:
            try:
                result = await get_address_async(lat, lon)
                print(f"[ASYNC] ({lat:.5f}, {lon:.5f}) => {result.get('formatted_address')}")
            except Exception as e:
                print(f"[ASYNC] ({lat:.5f}, {lon:.5f}) ERROR: {e}")


if __name__ == "__main__":
    # Define a few well-known landmarks and run both sync and async tests.
    samples = [
        (32.0853, 34.7818),   # Tel Aviv
        (31.7784, 35.2066),   # Jerusalem
        (40.6892, -74.0445),  # Statue of Liberty
        (48.8584, 2.2945),    # Eiffel Tower
    ]
    tester = GeoClientTester(samples)
    tester.run_sync()
    asyncio.run(tester.run_async())
