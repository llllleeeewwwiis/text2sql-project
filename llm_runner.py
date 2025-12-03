# llm_runner.py
import subprocess
import json
import sys


class OllamaRunner:
    def __init__(self, model="qwen2.5:3b", stream=False, verbose=False):
        """
        model: Ollama model name, e.g. qwen2.5:3b
        stream: whether to use streaming output
        verbose: show internal logs
        """
        self.model = model
        self.stream = stream
        self.verbose = verbose

    def run(self, prompt: str) -> str:
        """
        Run LLM with full prompt and return text output.
        """
        if self.verbose:
            print(f"[OllamaRunner] Running model {self.model} ...")
            print(f"[Prompt] {prompt}")

        # Prepare command
        cmd = ["ollama", "run", self.model]

        try:
            if not self.stream:
                # Non-stream mode (simple)
                process = subprocess.run(
                    cmd,
                    input=prompt,
                    capture_output=True,
                    text=True
                )
                if process.returncode != 0:
                    raise RuntimeError(process.stderr)
                return process.stdout.strip()

            else:
                # Stream mode
                process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                # Write prompt
                process.stdin.write(prompt)
                process.stdin.close()

                # Read streaming output
                output = []
                for line in process.stdout:
                    sys.stdout.write(line)  # print stream to console
                    output.append(line)

                process.wait()
                return "".join(output).strip()

        except Exception as e:
            print("[OllamaRunner] ERROR:", e)
            return ""


# Test
if __name__ == "__main__":
    runner = OllamaRunner(model="qwen2.5:3b", stream=False, verbose=True)
    query = "Explain what a database index is in one sentence."
    resp = runner.run(query)
    print("\n=== MODEL OUTPUT ===")
    print(resp)
