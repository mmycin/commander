import os
from os import error
from typing import Final
from typing_extensions import List
import typer
import subprocess
from pathlib import Path
import sys
import re
from dotenv import load_dotenv
load_dotenv()

app = typer.Typer(
    help=(
        "Commander — An AI-powered CLI assistant built with Ollama's local LLMs.\n\n"
        "It generates and executes terminal commands for specific tasks using natural language input. "
        "Let the AI handle your shell work — securely, locally, and smartly.\n\n"
        "Created by Mycin."
    )
)

# Setup
model_file_name: str = ""
system_file_name: str = ""
process: Final[str] = str(os.getenv("PROCESS"))
filename = os.path.basename(__file__)
if process == "PRODUCTION" or not filename.endswith(".py"):
    # Production
    base_path = Path(sys.executable).parent.parent
    model_file_name = str(base_path / "model.txt")
    system_file_name = str(base_path / "systemprompt.txt")
elif process == "DEVELOPMENT" or filename.endswith(".py"):
    # Dev 
    model_file_name = "model.txt"
    system_file_name = "systemprompt.txt"
else:
    print("Set up your environment variable")
    sys.exit(1)


# Utility Functions 

def remove_newlines(s, n=3):
    count = 0
    i = len(s)
    while i > 0 and count < n:
        if s[i-1] == '\n':
            i -= 1
            if i > 0 and s[i-1] == '\r':
                i -= 1
            count += 1
        else:
            break
    return s[:i]

def generate_command(command: str) -> str | None:
    systemPrompt = ""
    with open(system_file_name, "r") as file:
        systemPrompt = file.read()
    
    prompt: Final[str] = systemPrompt + f"""
            Generation:
            According to the examples and strictly following the rules, 
            generate a command for unix to {command}
        """
    
    try:
        modelName: str = ""
        with open(model_file_name, "r") as file:
            modelName = file.read()
        result = subprocess.run(["ollama", "run", modelName, prompt], capture_output=True, text=True)
        output = result.stdout
        output = format(output)
        output = remove_newlines(output)
    
        if output.startswith("```") or output.endswith("```\n"):
            output = output[3:-3].strip()
        return output
    except:
        print("Run your Ollama model 1st")
        return None

def list_model() -> List[str]: 
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, shell=True)
        
        # Decode and split lines
        lines = result.stdout.strip().split("\n")
        
        # Skip the header
        model_lines = lines[1:]
        
        # Extract model names
        model_names = [line.split()[0] for line in model_lines if line.strip()]
        return model_names
    except:
        print("You don't have Ollama Setup to your path.")
        return []
        
def format(text: str) -> str:
    if text.__contains__("<think>") or text.__contains__("</think>"):
        compiler: Final[re.Pattern] = re.compile(r"<think>.*?</think>\s*", re.DOTALL)
        output: Final[str] = compiler.sub("", text).strip()
        return output
    return text
        
def show_available_models(models: List[str]):
    print("\nAvailable Models:")
    print("=================")
    for i, name in enumerate(models, start=1):
        print(f"{i}. {name}")

def set_model(model: str, model_list: List[str]):
    matching_model = next((m for m in model_list if model in m), None)

    if not matching_model:
        print(f"Can't set model to '{model}'. No model found.")
        show_available_models(model_list)
        sys.exit(1)

    with open(model_file_name, "w") as file:
        file.write(matching_model)

    print(f"Model successfully set to: {matching_model}")


# CLI Commands

@app.command(help="Initalize Commander CLI")
def init():
    model_names = list_model()
    print("Initializing Commander")
    try:
        res = subprocess.run(["ollama"], capture_output=True, text=True)
        if res.returncode == 0:
            show_available_models(model_names)
            model: str = input("Enter the model you want to use: ")
            try:
                set_model(model, model_names)
                print("Setup complete.")
            except:
                print("Something went wrong. Try again.")
        else:
            print("You don't have Ollama installed.")
    except FileNotFoundError:
        print("You don't have Ollama installed.")
    
@app.command(help="Provide aetailed information about your situation and get a generated command for it.")
def gen(command: str):
    """This is a command for generating a Nushell Command for given input"""
    cmd = generate_command(command)
    print(cmd)

@app.command(help="Provide aetailed information about your situation and the AI Agent will do the process.")
def run(command: str):
    """This is a command for running a Nushell Command for given input"""
    try:
        cmd = generate_command(command)
        if cmd is not None:
            try:
                subprocess.run(["nu", "-c", cmd], shell=True)
                print("Success")
            except:
                print("Incorrect command. Try again")
        else:
            pass
    except:
        print("Somthing went wrong.")    

@app.command(help="Shows the current model and available model list")
def model():
    with open(model_file_name, "r") as file:
        model_name = file.read()
        print(f"Current Ollama Model Name: {model_name}")
    
    
    result = subprocess.run(["ollama", "list"], capture_output=True, text=True, shell=True)
    
    # Decode and split lines
    lines = result.stdout.strip().split("\n")
    
    # Skip the header
    model_lines = lines[1:]
    
    # Extract model names
    model_names = list_model()
    
    if not model_file_name:
        print("Something went Wrong")
    else:
    # Print formatted output
        show_available_models(model_names)
        
@app.command(help="Provide a valid Ollama Model installed in your system like `llama3.2@latest`, `gemma3.2@latest` etc")
def set(model: str):
    """This is a command for changing the AI Ollama LLM Model"""
    try:
        model_list = list_model()

        # Find the first matching model (partial match)
        set_model(model, model_list)

    except Exception as e:
        print(f"Could not load the model. Error: {e}")
    

if __name__ == "__main__":
    app()
