import subprocess
import sys
import time

def main():
    print("Starting FastAPI backend...", flush=True)
    backend = subprocess.Popen(
        ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=sys.stdout,
        stderr=sys.stderr
    )

    # Give backend 3 seconds to fully bind before traffic hits
    time.sleep(3)

    print("Starting Streamlit frontend...", flush=True)
    frontend = subprocess.Popen(
        ["streamlit", "run", "app/frontend/streamlit_app.py", "--server.port", "8501", "--server.address", "0.0.0.0", "--server.headless", "true"],
        stdout=sys.stdout,
        stderr=sys.stderr
    )

    while True:
        try:
            b_ret = backend.poll()
            f_ret = frontend.poll()

            if b_ret is not None:
                print(f"ERROR: Backend crashed with exit code {b_ret}. Terminating frontend and exiting.", flush=True)
                frontend.terminate()
                sys.exit(b_ret)

            if f_ret is not None:
                print(f"ERROR: Frontend crashed with exit code {f_ret}. Terminating backend and exiting.", flush=True)
                backend.terminate()
                sys.exit(f_ret)

            time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down...", flush=True)
            backend.terminate()
            frontend.terminate()
            break
        except Exception as e:
            print(f"Launcher error: {e}", flush=True)
            backend.terminate()
            frontend.terminate()
            sys.exit(1)

if __name__ == "__main__":
    main()
