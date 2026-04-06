import os
import json
from openai import OpenAI
from environment import SREEnvironment
from models import SREAction

# Make sure you set your API key in your terminal before running this:
# Windows: set OPENAI_API_KEY=your-key-here
# Mac/Linux: export OPENAI_API_KEY=your-key-here

client = OpenAI()
env = SREEnvironment()

# The System Prompt that tells the AI how to play your game
SYSTEM_PROMPT = """
You are an elite Site Reliability Engineer (SRE). 
You have been dropped into a broken Linux server environment. 
You must use terminal commands to investigate logs, find the bugs, and patch the broken files.

You can ONLY output raw JSON matching this schema:
{
  "action_type": "bash_command" | "patch_file" | "submit_report",
  "command": "string (only if bash_command)",
  "file_path": "string (only if patch_file)",
  "new_content": "string (only if patch_file)",
  "root_cause": "string (only if submit_report)"
}
Output NOTHING else. No markdown, no explanations. Just valid JSON.
"""

def run_agent():
    print("--- 🤖 BOOTING AI AGENT ---")
    obs = env.reset()
    
    # We feed the AI the initial state
    chat_history = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"SYSTEM CRASHED. You are in {obs.current_directory}. Initial Health: {obs.system_health_score}. Output your first JSON action."}
    ]

    done = False
    
    while not done:
        # 1. Ask the AI what it wants to do
        print("\n🧠 AI is thinking...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=chat_history,
            temperature=0.2
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # Strip markdown if the AI accidentally adds it
        if ai_response.startswith("```json"):
            ai_response = ai_response[7:-3].strip()
            
        print(f"⚡ AI Chose:\n{ai_response}")
        
        try:
            # 2. Parse the AI's JSON into your Pydantic Model
            action_dict = json.loads(ai_response)
            action = SREAction(**action_dict)
            
            # 3. Pass the action to your environment
            result = env.step(action)
            obs = result.observation
            done = result.done
            
            print(f"🖥️ Environment Output:\n{obs.terminal_output[:200]}...") # Print first 200 chars
            print(f"❤️ Health: {obs.system_health_score} | 💰 Reward: {result.reward}")
            
            # 4. Add the result back to the chat history so the AI can read it
            chat_history.append({"role": "assistant", "content": ai_response})
            chat_history.append({"role": "user", "content": f"Command Output:\n{obs.terminal_output}\nCurrent Health: {obs.system_health_score}"})

        except Exception as e:
            print(f"❌ AI formatted JSON incorrectly or crashed: {e}")
            chat_history.append({"role": "assistant", "content": ai_response})
            chat_history.append({"role": "user", "content": f"System Error: Invalid JSON or action formatting. Try again. Error: {str(e)}"})

    print(f"\n🏁 EPISODE FINISHED. Final Reward: {result.reward}")

if __name__ == "__main__":
    run_agent()