import subprocess
import datetime
import os

# Exécuter le script Node.js qui fait la capture
try:
    print("Début de la capture à", datetime.datetime.now())
    env = os.environ.copy()
    env["PUPPETEER_EXECUTABLE_PATH"] = "/usr/bin/google-chrome-stable"

    result = subprocess.run(
        ["node", "/app/screenshot.cjs"],
        capture_output=True,
        text=True,
        env=env
    )
    
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

except Exception as e:
    print("Erreur lors de la capture :", str(e))
