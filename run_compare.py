import subprocess
result = subprocess.run(['python', 'compare_forms.py'], capture_output=True, text=True, encoding='utf-8')
print(result.stdout)
if result.stderr:
    print("ERRORS:", result.stderr)
