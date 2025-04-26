import random

def generate_data(num_lines=50):
    """
    Generates a list of strings in the format "x:y" where x is between 1 and 4
    and y is between 1 and 100.

    Args:
        num_lines: The number of lines to generate.

    Returns:
        A list of strings, each representing a line of data.
    """
    data = []
    for _ in range(num_lines):
        x = random.randint(1, 4)
        y = random.randint(1, 100)
        data.append(f"{x}:{y}")
    return data

# Generate the data and print it
data = generate_data()
# For outputting to a file instead of printing to console
with open(f"SimulationData{random.randint(0, 100)}.txt", "w") as f:
    for line in data:
        f.write(line + "\n")  # Add a newline character to separate lines