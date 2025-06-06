from os import error
from typing import Final
from typing_extensions import List
import typer
import subprocess
from pathlib import Path
import sys
import re

app = typer.Typer()

# Production
base_path = Path(sys.executable).parent.parent
model_file_name: Final[str] = str(base_path / "model.txt")

# Dev 
# model_file_name = "model.txt"

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
    prompt: Final[str] = f"""
            System:
            You are an AI Agent for generating Nushell command for specific task.
            You will generate a command for nushell in Windows.
            
            Rules:
            1. GENERATE ONLY THE COMMAND AND NOT A SINGLE LETTER MORE. 
            2. DO NOT USE ANY MARKDOWN OR ANYTHING ELSE. JUST THE COMMAND. NOT EVEN NEW LINES. NOT EVEN `` THESE.
            3. NOT A SINGLE ANYTHING ELSE THAN A COMMAND.
            4. DO NOT USE ABSOLUTE PATHS. USE ONLY REALTIVE PATHS FOR FILES
            4. DO NOT ANSWER OR REPLY ANY SINGLE PROMPT THAT DOES NOT INCLUDE GENERATING A COMMAND.
            5. FOLLOW IT STRICTLY
            
            Example:
            1.List Files
                prompt: list files
                thinking: I have to generate a nushell command for listing all files
                
                response:
                ls -al
                
            2. Create Directory
                prompt: make a dir named Test
                thinking: I have to generate a nushell command for creating a directory named Test
                
                response: 
                mkdir Test
                
            3. Running Code
                prompt: run main.c file
                thinking: I have to compile the `main.c` file first. It will generate a `main` file. I have to run itt.
                
                response:
                gcc main.c -o main
                ./main
                
            4. Deleting File
                prompt: remove test.py
                thinking: I have to generate a command for nushell to remove the file named test.py
                
                response:
                rm -rf test.py
            
                
            Generation:
            According to the examples and strictly following the rules, 
            generate a command for nushell in windows to {command}
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
        
@app.command(help="Provide a valid Ollama Model installed in your system like `llama3.2@latest`, `gemma3.2@latest` etc")
def set(model: str):
    """This is a command for changing the AI Ollama LLM Model"""
    try:
        model_list = list_model()

        # Find the first matching model (partial match)
        matching_model = next((m for m in model_list if model in m), None)

        if not matching_model:
            print(f"Can't set model to '{model}'. No model found.")
            show_available_models(model_list)
            sys.exit(1)

        with open(model_file_name, "w") as file:
            file.write(matching_model)

        print(f"Model successfully set to: {matching_model}")

    except Exception as e:
        print(f"Could not load the model. Error: {e}")

        
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


if __name__ == "__main__":
    app()
