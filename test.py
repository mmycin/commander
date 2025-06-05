import subprocess

# Run the command
result = subprocess.run(["ollama", "list"], capture_output=True, text=True, shell=True)

# Decode and split lines
lines = result.stdout.strip().split("\n")

# Skip the header
model_lines = lines[1:]

# Extract model names
model_names = [line.split()[0] for line in model_lines if line.strip()]

# Print formatted output
print("Available Models:")
print("=================")
for i, name in enumerate(model_names, start=1):
    print(f"{i}. {name}")
