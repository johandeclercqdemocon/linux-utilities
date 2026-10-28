# gvisor-docker

Installs [gVisor](https://gvisor.dev) as an **extra** Docker runtime called `runsc`, checks it, and
removes it again. Docker's default runtime stays `runc`: only a container started with
`--runtime=runsc` (or `runtime: runsc` in compose) runs in gVisor.

| File | What it does | Root |
|---|---|---|
| `install-gvisor` | downloads a release, checks its sha512, installs it, registers it with Docker, restarts Docker | yes (`--dry-run`: no) |
| `check-gvisor` | runs the same probe under `runc` and under `runsc` and shows the difference | no |

## Why

gVisor gives each container its own kernel, written in Go, between the container and the real kernel.
Two consequences matter here:

- **A process in the container talks to gVisor, not to the laptop's kernel.** A container escape has to
  break gVisor first.
- **Sandboxes inside the container work.** Under Docker's normal runtime, `bwrap` cannot run inside a
  container: Docker's AppArmor profile forbids its mount changes ("Failed to make / slave"), even with
  seccomp off or with `SYS_ADMIN` added. Under gVisor it works, as a normal user, with Docker's default
  seccomp filter. So does `unshare -rn` (a process without network).

This is what `ask` in `~/claude/multi-model-setup` needs: its agents run in `bwrap`, so that they cannot
read the answer keys, and its probes run with `unshare -rn`. See that repo's `V2.md`, item 7.

## Measured on this laptop (2026-10-24)

Ubuntu 24.04.5, kernel 7.0.0-38-generic, Docker 29.9.2, gVisor release-20261019.0.
`./check-gvisor ask:latest` (the `ask` image, user `ask`, default seccomp):

| | `--runtime=runc` | `--runtime=runsc` |
|---|---|---|
| kernel | 7.0.0-38-generic | 4.19.0-gvisor |
| `bwrap` | fails | **works** |
| `unshare -rn` | fails | **works** |
| network | yes | yes |

Start time of `docker run --rm debian:12-slim true`, 5 runs each: runc 0.39–0.41 s, runsc 0.39–0.44 s.
gVisor is slower for heavy file and network work. That was not measured here.

## Install

First look at what it will do. This downloads and verifies the release, but changes nothing:

```bash
./install-gvisor --dry-run
```

Then install. It asks before it restarts Docker:

```bash
sudo ./install-gvisor
```

What it does:

1. Downloads `gvisor.tar.zstd` (about 58 MB; `.tar.bz2` if `zstd` is missing) for the release in the
   script (`RELEASE=20261019.0`, the one tested here) and its `.sha512`. It stops if the checksum fails.
2. Installs `runsc` and `containerd-shim-runsc-v1` into `/usr/local/bin`, and the helper programs into
   `/usr/local/bin/gvisor-bin/`, where `runsc` looks for them.
3. Backs up `/etc/docker/daemon.json` (if it exists) to `daemon.json.bak-gvisor-<date>`, then runs
   `runsc install --download-sidecars=NEVER`. That adds the `runsc` runtime to `daemon.json` and keeps
   the rest of the file.
4. Lists the running containers with their restart policy, and asks before `systemctl restart docker`.
   **A restart stops every running container.** Only those with a restart policy (`always`,
   `unless-stopped`) come back by themselves.

Options:

| Option | Effect |
|---|---|
| `--release latest` | the newest release instead of the tested one |
| `--release 20261019.0` | a given release (the folder names in the gVisor bucket) |
| `--tarball FILE` | use a file you already downloaded; `FILE.sha512` must be next to it |
| `--restart` | restart Docker without asking |
| `--dry-run` | verify and list the steps, change nothing |

## Check

```bash
./check-gvisor
./check-gvisor ask:latest
```

It needs no root and changes nothing. It shows whether `runsc` is on the `PATH` and registered with Docker.
Then it runs one probe in the image twice, under `runc` and under `runsc`: the kernel, gVisor's own
`dmesg` line, and `bwrap`, `unshare -rn` and network if the image has them. It ends with `OK`, or
`FAILED` and exit code 1. Without an image argument, it uses `debian:12-slim`, which Docker pulls if
it is not on the machine.

## Use

```bash
docker run --rm --runtime=runsc debian:12-slim uname -r
```

In a compose file:

```yaml
services:
  app:
    runtime: runsc
```

## Remove

```bash
sudo ./install-gvisor --uninstall
```

This runs `runsc uninstall`, deletes the three installed items in `/usr/local/bin`, and asks before it
restarts Docker. `runsc uninstall` removes only the `runsc` entry from `/etc/docker/daemon.json` and
keeps the other keys (tested on a copy with a second runtime and a `log-driver`; `runsc install` keeps
them too). The backup of `daemon.json` stays. A container or compose file that asks for
`runtime: runsc` needs the runtime: install it again first.

## Limits

- **x86_64 and aarch64 only**: gVisor has no other builds.
- **Not every program runs in gVisor.** It implements most Linux system calls, not all. Run
  `./check-gvisor YOUR-IMAGE`, then your own tests.
- **The release is pinned.** `RELEASE` in `install-gvisor` is the one tested here. Change it, or use
  `--release latest`, on purpose.
- **The script trusts Google's release bucket.** The `.sha512` comes from the same place as the archive.
  That catches a broken download, not a compromised bucket.

## Installed here

On 2026-10-24, by hand, with the same steps as the script, from the same archive (sha512 checked).
