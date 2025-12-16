"""
Quick runner for geocoding with automatic confirmation
"""
import subprocess
import sys

# Run the geocoding script and provide 'yes' input
process = subprocess.Popen(
    ['python', 'scripts/geocode_little_pantries.py', '100'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
    cwd=r'C:\Users\ohmeg\code\FoodFinder'
)

# Send 'yes' to the prompt
output, _ = process.communicate(input='yes\n')
print(output)
