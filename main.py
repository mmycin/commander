from os import error
from typing import Final
import typer
import subprocess
from pathlib import Path
import sys

app = typer.Typer()
base_path = Path(sys.executable).parent.parent
model_file_name: Final[str] = str(base_path / "model.txt")

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
    cmd = generate_command(command)
    if cmd is not None:
        try:
            subprocess.run(["nu", "-c", cmd], shell=True)
            print("Success")
        except:
            print("Incorrect command. Try again")
    else:
        pass
        
@app.command(help="Provide a valid Ollama Model installed in your system like `llama3.2@latest`, `gemma3.2@latest` etc")
def set(model: str):
    """This is a command for changing the AI Ollama LLM Model"""
    try:    
        with open(model_file_name, "w") as file:
            file.write(model)
        print(f"Model Successfully Set to: {model}")
    except:
        print("Could not load the model")
        
@app.command(help="Shows the current model")
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
    model_names = [line.split()[0] for line in model_lines if line.strip()]
    
    # Print formatted output
    print("\nAvailable Models:")
    print("=================")
    for i, name in enumerate(model_names, start=1):
        print(f"{i}. {name}")


if __name__ == "__main__":
    app()
