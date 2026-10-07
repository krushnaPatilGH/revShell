from src.colours import RED, GREEN, YELLOW, RESET
class stable:
    def __init__(self, shell):
        self.shell = shell
        self.info = dict()

    def inspect(self):
        print(f"\n{YELLOW}[*] Inspecting shell...")
        checks = {
            "python3" : "command -v python3 2>/dev/null",
            "python": "command -v python 2>/dev/null",
            "script": "command -v script 2>/dev/null",
        }

        for name, cmd in checks.items():
            result = self.shell.command(cmd)
            if result:
                result = result.splitlines()[-1].strip()
                self.info[name] = result

    def upgrade(self):
        print(f"[*] Checking available methods\n")
        methods = []
        if self.info.get("python"):
            methods.append(("python PTY", "python -c 'import pty; pty.spawn(\"/bin/bash\")'"))
        if self.info.get("python3"):
            methods.append(("python3 PTY", "python3 -c 'import pty; pty.spawn(\"/bin/bash\")'"))
        if self.info.get("script"):
            methods.append(("script PTY", "script -qc /bin/bash /dev/null"))

        if not methods:
            print(f"{RED}[-] no methods found{YELLOW}")
            return
        
        print(f"{GREEN}[*] choose the method: {RESET}")
        for i, (name, _) in enumerate(methods, 1):
            print(f"\t[{i}] {name}")
        
        try:
            choice = int(input("choice: "))
            name, cmd = methods[choice - 1]
        except (ValueError, IndexError):
            print("[-] Invalid Selection")
            return
        
        print(f"\n{GREEN}starting shell{RESET}")
        self.shell.command(cmd)
