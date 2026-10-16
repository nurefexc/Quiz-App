#!/usr/bin/env python3
import sys
import subprocess

def compile_translations():
    """Compile translation files"""
    # First attempt: use babel module directly
    try:
        from babel.messages.frontend import CommandLineInterface
        cli = CommandLineInterface()
        result = cli.run(['pybabel', 'compile', '-d', 'app/translations'])
        if result == 0 or result is None:
            print("Translations compiled successfully via Babel CLI interface")
            return True
    except Exception as e:
        pass

    # Second attempt: run pybabel via subprocess
    try:
        subprocess.run(
            ['pybabel', 'compile', '-d', 'app/translations'],
            check=True,
            capture_output=True,
            text=True
        )
        print("Translations compiled successfully via pybabel subprocess")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        pass

    # Third attempt: run python -m babel.messages.frontend
    try:
        subprocess.run(
            [sys.executable, '-m', 'babel.messages.frontend', 'compile', '-d', 'app/translations'],
            check=True,
            capture_output=True,
            text=True
        )
        print("Translations compiled successfully via python module")
        return True
    except Exception as e:
        print(f"Error compiling translations: {e}")
        return False

if __name__ == '__main__':
    success = compile_translations()
    if not success:
        sys.exit(1)
