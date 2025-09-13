#!/usr/bin/env python3
"""
Example usage of the ORC system with Claude Code-style interaction
"""

import asyncio
from interactive_loop import InteractiveORCLoop


async def demo_claude_style():
    """Demonstrate Claude Code-style interaction"""

    orc = InteractiveORCLoop()

    print("=" * 60)
    print("ORC Demo - Claude Code Style Interaction")
    print("=" * 60)
    print()

    # Example 1: High confidence - auto proceeds
    print("Example 1: High confidence input")
    print("-" * 40)
    print("User: scan example.com for vulnerabilities stealthily")

    response = await orc.process_user_input("scan example.com for vulnerabilities stealthily")

    if response["status"] == "executing":
        print("✓ ORC made assumptions and started automatically")
        print(f"  Target: {response['plan']['target']}")
        print(f"  Mode: {'Stealth' if response['plan']['stealth'] else 'Aggressive'}")
        print(f"  Agents: {', '.join(response['plan']['initial_agents'])}")

    print("\n" + "=" * 60 + "\n")

    # Reset for next example
    orc = InteractiveORCLoop()

    # Example 2: Lower confidence - asks for confirmation
    print("Example 2: Ambiguous input requiring confirmation")
    print("-" * 40)
    print("User: check that server")

    response = await orc.process_user_input("check that server")

    if response["status"] == "confirm":
        print("✓ ORC needs confirmation due to ambiguity")
        print(response["message"])

        # User confirms
        print("\nUser: y")
        response = await orc.process_user_input("y")
        print(f"→ Operation started: {response.get('message')}")

    print("\n" + "=" * 60 + "\n")

    # Example 3: User provides correction instead of yes/no
    orc = InteractiveORCLoop()

    print("Example 3: User provides correction")
    print("-" * 40)
    print("User: test the network")

    response = await orc.process_user_input("test the network")

    if response["status"] == "confirm":
        print("ORC's plan:")
        print(response["message"])

        # User provides correction
        print("\nUser: actually do internal network 192.168.1.0/24 aggressively")
        response = await orc.process_user_input("actually do internal network 192.168.1.0/24 aggressively")

        if response["status"] == "executing":
            print(f"✓ Adjusted and started: {response['plan']['target']}")
            print(f"  Scope: {response['plan']['scope']}")
            print(f"  Mode: {'Aggressive' if not response['plan']['stealth'] else 'Stealth'}")

    print("\n" + "=" * 60 + "\n")

    # Example 4: Continuous operation with auto-decisions
    orc = InteractiveORCLoop()

    print("Example 4: Automatic flow with high confidence")
    print("-" * 40)
    print("User: complete security assessment of 10.0.0.1 internal network quickly")

    response = await orc.process_user_input(
        "complete security assessment of 10.0.0.1 internal network quickly"
    )

    # Should auto-proceed due to clear instructions
    if response["status"] == "executing":
        print("✓ Clear instructions - proceeding automatically")
        print(f"→ {response['message']}")

        # Simulate successful results triggering auto-continue
        if response.get("next_action", {}).get("action") == "auto_continue":
            print("✓ Initial phase successful - continuing automatically...")

    print("\n" + "=" * 60)
    print("Demo complete!")


async def interactive_demo():
    """Run an interactive demo"""

    print("=" * 60)
    print("ORC Interactive Demo")
    print("=" * 60)
    print("\nTry these examples:")
    print("  • scan example.com")
    print("  • quick recon on 192.168.1.0/24")
    print("  • thorough security assessment of target.com")
    print("  • aggressive test on internal network")
    print("\n")

    orc = InteractiveORCLoop()

    while True:
        try:
            user_input = input("[ORC] > ").strip()

            if user_input.lower() in ['exit', 'quit']:
                break

            response = await orc.process_user_input(user_input)

            # Display based on status
            if response["status"] == "confirm":
                print(response["message"])
                confirm = input(response.get("prompt", "Proceed? (y/n): ")).strip()
                confirm_response = await orc.process_user_input(confirm)
                print(f"→ {confirm_response.get('message', 'Processing...')}")

            elif response["status"] == "executing":
                print(f"→ {response['message']}")
                if "initial_results" in response:
                    for result in response["initial_results"]:
                        status = "✓" if result.get("success") else "✗"
                        print(f"  {status} {result.get('agent', 'agent')}")

            elif response["status"] == "complete":
                print("Operation complete!")
                break

            else:
                print(f"[{response['status']}] {response.get('message', response)}")

        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
            break
        except Exception as e:
            print(f"Error: {e}")

    print("\nGoodbye!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        asyncio.run(demo_claude_style())
    else:
        asyncio.run(interactive_demo())