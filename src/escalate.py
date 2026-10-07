
class Escalate:
    def __init__(self, shell):
        self.shell = shell

    def scan(self):
        suid = self.shell.command("find /usr/bin -type f -perm -4000 -ls 2>/dev/null").decode()
        getcap = self.shell.command("getcap -r /usr/bin 2>/dev/null").decode()
        cron = self.shell.command("cat /etc/crontab").decode()
        print(suid, "-"*30, "\n\n", getcap, "-"*30, "\n\n", cron)
