"""Bookly support chat (CLI)"""

from agent import get_agent_reply

def main():
    print("=" * 60)
    print("  Bookly Customer Support  (type 'quit' to exit)")
    print("=" * 60)
    conversation = []
    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("\nBookly: Thanks for reading with Bookly!")
            break
        conversation.append({"role": "user", "content": user_input})
        reply = get_agent_reply(conversation)
        conversation.append({"role": "assistant", "content": reply})
        print(f"\nBookly: {reply}")

if __name__ == "__main__":
    main()