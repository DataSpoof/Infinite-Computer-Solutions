"""
SSH & Terminal Automation with Python (Paramiko) -- Windows / localhost
=======================================================================

This is set up for OPTION 1: practise by SSH-ing into your OWN Windows PC.

STEP 1 -- enable the built-in OpenSSH server (one time).
    Open PowerShell AS ADMINISTRATOR and run:

        Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
        Start-Service sshd
        Set-Service -Name sshd -StartupType Automatic

    Check it's listening:
        Get-Service sshd
        Get-NetTCPConnection -LocalPort 22 -State Listen

STEP 2 -- run this script (a normal terminal is fine):
        python ssh_automation.py

    It connects to 127.0.0.1 as your Windows user and runs a few commands.
    You'll be asked for your Windows login password (typed securely, not
    stored). Set SSH_PASSWORD in the environment if you'd rather not be asked.

IMPORTANT: because you're SSH-ing into WINDOWS, the remote shell is Windows
(cmd), so the commands below are Windows commands (whoami, hostname, ver,
ipconfig...) -- NOT Linux ones like uname/df/uptime.

Install:  pip install paramiko
"""

import getpass
import os
import socket

import paramiko

# ---------------------------------------------------------------------------
# Configuration (env vars override these defaults)
# ---------------------------------------------------------------------------
SSH_HOST = os.environ.get("SSH_HOST", "127.0.0.1")
SSH_PORT = int(os.environ.get("SSH_PORT", "22"))
SSH_USER = os.environ.get("SSH_USER", os.environ.get("USERNAME", "Abhishek"))
SSH_PASSWORD = os.environ.get("SSH_PASSWORD")            # None -> we'll prompt
SSH_KEY_PATH = os.environ.get("SSH_KEY_PATH")            # optional key auth
SSH_KEY_PASSPHRASE = os.environ.get("SSH_KEY_PASSPHRASE")

KNOWN_HOSTS = os.path.expanduser(os.path.join("~", ".ssh", "known_hosts"))

# Windows remote shell => Windows commands.
WINDOWS_DEMO_COMMANDS = [
    "whoami",
    "hostname",
    "ver",
    "echo %USERDOMAIN%",
    "ipconfig | findstr IPv4",
]


class SSHSession:
    """A secure, reusable SSH connection usable as a context manager:

        with SSHSession(host, user, password=...) as ssh:
            code, out, err = ssh.run("whoami")
    """

    def __init__(self, host, user, port=22, password=None,
                 key_path=None, key_passphrase=None, timeout=15):
        self.host = host
        self.user = user
        self.port = port
        self.password = password
        self.key_path = key_path
        self.key_passphrase = key_passphrase
        self.timeout = timeout
        self._client = None

    # -- connection lifecycle ------------------------------------------------
    def connect(self):
        client = paramiko.SSHClient()

        # Load known host keys so the server's identity can be verified.
        client.load_system_host_keys()
        if os.path.exists(KNOWN_HOSTS):
            client.load_host_keys(KNOWN_HOSTS)

        # SECURE default: refuse to connect to a host we don't already know.
        # (ensure_host_trusted() below pins the key deliberately first.)
        client.set_missing_host_key_policy(paramiko.RejectPolicy())

        connect_kwargs = dict(
            hostname=self.host,
            port=self.port,
            username=self.user,
            timeout=self.timeout,
            allow_agent=False,
            look_for_keys=False,     # be explicit about which auth we use
        )

        # Prefer key-based auth; fall back to password.
        if self.key_path:
            connect_kwargs["key_filename"] = os.path.expanduser(self.key_path)
            if self.key_passphrase:
                connect_kwargs["passphrase"] = self.key_passphrase
            connect_kwargs["look_for_keys"] = True
        elif self.password:
            connect_kwargs["password"] = self.password
        else:
            raise ValueError("Provide either key_path or password for auth.")

        client.connect(**connect_kwargs)
        self._client = client
        return self

    def close(self):
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc, tb):
        self.close()

    # -- remote commands -----------------------------------------------------
    def run(self, command, timeout=30):
        """Run one command. Returns (exit_code, stdout_text, stderr_text)."""
        if not self._client:
            raise RuntimeError("Not connected. Call connect() first.")
        stdin, stdout, stderr = self._client.exec_command(command, timeout=timeout)
        out = stdout.read().decode(errors="replace")
        err = stderr.read().decode(errors="replace")
        code = stdout.channel.recv_exit_status()      # blocks until finished
        return code, out, err

    def run_many(self, commands):
        """Run a list of commands, printing each result."""
        for cmd in commands:
            code, out, err = self.run(cmd)
            status = "OK" if code == 0 else f"FAILED ({code})"
            print(f"\n$ {cmd}   [{status}]")
            if out.strip():
                print(out.strip())
            if err.strip():
                print("stderr:", err.strip())

    # -- file transfer (SFTP) ------------------------------------------------
    def upload(self, local_path, remote_path):
        """Copy a local file to the server over SFTP."""
        with self._client.open_sftp() as sftp:
            sftp.put(local_path, remote_path)
        print(f"Uploaded {local_path} -> {remote_path}")

    def download(self, remote_path, local_path):
        """Copy a file from the server to the local machine over SFTP."""
        with self._client.open_sftp() as sftp:
            sftp.get(remote_path, local_path)
        print(f"Downloaded {remote_path} -> {local_path}")


# ---------------------------------------------------------------------------
# Host-key trust helpers
# ---------------------------------------------------------------------------
def trust_host_key(host, port=22):
    """Fetch a server's host key and save it to known_hosts.

    For a REAL server, compare the printed fingerprint against one your admin
    gave you out-of-band before trusting it -- that's your MITM protection.
    For localhost (Option 1) it's safe to accept.
    """
    transport = paramiko.Transport((host, port))
    try:
        transport.start_client(timeout=10)
        key = transport.get_remote_server_key()
    finally:
        transport.close()

    fp = key.get_fingerprint().hex(":")
    print(f"Pinning {host}:{port} host key ({key.get_name()})")
    print(f"  fingerprint: {fp}")

    os.makedirs(os.path.dirname(KNOWN_HOSTS), exist_ok=True)
    host_keys = paramiko.HostKeys(KNOWN_HOSTS) if os.path.exists(KNOWN_HOSTS) \
        else paramiko.HostKeys()
    # For a non-default port, known_hosts uses the "[host]:port" form.
    entry = host if port == 22 else f"[{host}]:{port}"
    host_keys.add(entry, key.get_name(), key)
    host_keys.save(KNOWN_HOSTS)
    print(f"  saved to {KNOWN_HOSTS}")


def ensure_host_trusted(host, port=22):
    """Pin the host key on first use so RejectPolicy won't block us."""
    entry = host if port == 22 else f"[{host}]:{port}"
    known = paramiko.HostKeys(KNOWN_HOSTS) if os.path.exists(KNOWN_HOSTS) \
        else paramiko.HostKeys()
    if known.lookup(entry) is None:
        print(f"{entry} is not in known_hosts yet -- pinning it now.")
        trust_host_key(host, port)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
def main():
    # Ask for the Windows password securely if none was provided and no key.
    password = SSH_PASSWORD
    if not password and not SSH_KEY_PATH:
        password = getpass.getpass(f"Windows password for {SSH_USER}: ")

    # First run: make sure the server's host key is trusted.
    try:
        ensure_host_trusted(SSH_HOST, SSH_PORT)
    except Exception as e:
        raise SystemExit(
            f"Could not reach an SSH server on {SSH_HOST}:{SSH_PORT} ({e}).\n"
            "Is the OpenSSH server running?  In an ADMIN PowerShell:\n"
            "  Start-Service sshd ;  Get-Service sshd"
        )

    try:
        with SSHSession(
            host=SSH_HOST,
            user=SSH_USER,
            port=SSH_PORT,
            password=password,
            key_path=SSH_KEY_PATH,
            key_passphrase=SSH_KEY_PASSPHRASE,
        ) as ssh:
            print(f"\nConnected to {SSH_USER}@{SSH_HOST}:{SSH_PORT}")

            ssh.run_many(WINDOWS_DEMO_COMMANDS)

            # Example file transfer over SFTP (uncomment to try):
            # ssh.upload("abc.txt", "C:/Users/%s/abc_uploaded.txt" % SSH_USER)
            # ssh.download("C:/Users/%s/abc_uploaded.txt" % SSH_USER, "abc_back.txt")

            print("\nDone.")

    except paramiko.AuthenticationException:
        print("Authentication failed -- wrong username or password.")
    except paramiko.SSHException as e:
        print("SSH error:", e)
    except socket.timeout:
        print("Connection timed out. Check host/port/firewall.")
    except Exception as e:
        print(f"{type(e).__name__}: {e}")


if __name__ == "__main__":
    main()