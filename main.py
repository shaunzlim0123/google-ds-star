import asyncio
from pathlib import Path
from ds_star import DSStarSession, OpenAIProvider, DSStarConfig

async def main():
    # Initialize the LLM provider
    provider = OpenAIProvider()

    # Create a session with optional configuration
    config = DSStarConfig(
        max_iterations=20,
        max_debug_attempts=3,
    )
    session = DSStarSession(provider=provider, config=config)

    # Use absolute paths for data files
    project_root = Path(__file__).parent
    data_files = [
        str(project_root / "data" / "transactions.csv"),
        str(project_root / "data" / "countries.json")
    ]

    # Run DS-STAR on your data science task
    answer = await session.run(
        query="What product had made the most money for each country?",
        data_files=data_files
    )

    print(f"Answer: {answer}")

if __name__ == "__main__":
    asyncio.run(main())