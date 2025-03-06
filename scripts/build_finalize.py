import subprocess
import sys
import cowsay

def main():
    try:
        # Check last commit message with commitizen
        subprocess.run(["cz", "check", "--rev-range", "HEAD^..HEAD"], check=True)
        print("Commit message validated with commitizen")

        # Run black formatting
        subprocess.run(["black", "."], check=True)
        print("Code formatted with black")

        # Run ruff linting
        subprocess.run(["ruff", "check", "."], check=True)
        print("Code linted with ruff")

        # Build the package
        subprocess.run(["poetry", "build"], check=True)
        print("Package built successfully")

        # Display cowsay message
        cowsay.cow("Build finalized successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error during build process: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()