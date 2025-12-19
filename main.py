import asyncio
import sys
from pathlib import Path

# Add backend directory to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from ds_star import DSStarSession, OpenAIProvider, DSStarConfig

async def main():
    print("🚀 Starting DS-STAR quick test...")
    print("=" * 60)

    try:
        # Initialize the LLM provider
        print("\n1. Initializing OpenAI provider (gpt-5-nano)...")
        provider = OpenAIProvider()
        print("   ✓ Provider initialized")

        # Create a session with optional configuration
        print("\n2. Creating DS-STAR session...")
        config = DSStarConfig(
            max_iterations=20,
            max_debug_attempts=3,
        )
        session = DSStarSession(provider=provider, config=config)
        print("   ✓ Session created")

        # Use absolute paths for data files
        project_root = Path(__file__).parent
        data_files = [
            str(project_root / "data" / "transactions.csv"),
            str(project_root / "data" / "countries.json")
        ]

        print(f"\n3. Data files:")
        for df in data_files:
            exists = "✓" if Path(df).exists() else "✗"
            print(f"   {exists} {df}")

        # Run DS-STAR on your data science task
        query = "What is the MoM percentage change in revenue for each country?"
        print(f"\n4. Running query: '{query}'")
        print("-" * 60)

        answer = await session.run(
            query=query,
            data_files=data_files
        )

        print("\n" + "=" * 60)
        print("📊 RESULT:")
        print("=" * 60)
        print(f"{answer}")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())