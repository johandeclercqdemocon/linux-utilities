# ollama-gpu-watchdog

GPU_BOX_IP is a placeholder: put in the address of the machine that runs Ollama.

Ollama can load a model partly into GPU memory and partly into system RAM. Nothing reports it:
requests still succeed, they are only slower. This tool shows when it has happened, and undoes it
while a long job runs. It contains one script, `watchdog.sh`.

## The problem (found 2026-10-16)

Machine: the GPU box (GTX 1070 Max-Q, 8 GB), Ollama 0.40.2 as a systemd service, during a long run of
the ml-book's Chapter 33 experiments. The job used `granite3.3:2b` and `llama3.1:8b` in turn.

Midway through, the job was slower than earlier runs of the same kind. The server showed why:

| | before | after one unload |
|---|---|---|
| `llama3.1:8b` in GPU memory (`/api/ps`) | 4.10 GB; the rest on the CPU | 5.26 of 5.26 GB |
| GPU memory used (`nvidia-smi`) | 3,937 of 8,192 MiB | 5,042 MiB |
| GPU utilisation | 0% at the moment of reading; CPU load average 6 | 100% |
| replies cached per minute by the job | about 22 | about 39 |

So the same job ran **about 1.8 times faster** after one API call. Each rate is from one window of
30 to 60 seconds, so read 1.8 as a rough figure.

The likely cause: the server decides how many layers go on the GPU when it loads a model, from the
memory free at that moment. If another model is loaded, the layers that do not fit go to the CPU,
and they stay there after the other model is gone. That mechanism is not verified. The table is what
was measured.

**How to see it yourself:** in `/api/ps`, `size_vram` is smaller than `size`. `ollama ps` shows the
same thing as a split such as `25%/75% CPU/GPU`.

## Requirements

`bash`, `curl` and `python3`, on any machine that can reach the Ollama server. Nothing runs on the
server itself.

## Use

Check once:

```bash
./watchdog.sh check http://GPU_BOX_IP:11434
```

```
granite3.3:2b                 1.94 of  1.94 GB on the GPU (100%)
llama3.1:8b                   5.26 of  5.26 GB on the GPU (100%)
```

A model partly on the CPU gets `<- partly on the CPU` at the end of its line.

Watch while a long job runs, checking every 60 seconds:

```bash
./watchdog.sh watch http://GPU_BOX_IP:11434 60
```

When any loaded model is partly on the CPU, `watch` unloads **every** loaded model and prints one line:

```
17:42:10 llama3.1:8b was partly on the CPU; unloaded every model
```

The unload asks Ollama for `keep_alive: 0`. A request already in progress finishes first. The next
request then reloads only the model it needs, onto a GPU that is now empty. Stop `watch` with Ctrl-C.

To run it beside a job and stop it when the job ends:

```bash
./watchdog.sh watch http://GPU_BOX_IP:11434 60 & dog=$!; ./long_job.sh; kill $dog
```

`HOST` defaults to `http://localhost:11434`, and the interval to 60 seconds.

## The catch: two models that do not fit together

If a job uses two models in turn and the two **cannot** fit in GPU memory at the same time, each
reload pushes part of the other model to the CPU again. `watch` then unloads at every check, and
every unload costs a reload of several seconds. You see this as a `watch` line every interval. In that
case stop `watch`, and use the server-side fix below, or run the two models' parts of the job
separately.

On the 8 GB box, `granite3.3:2b` and `llama3.1:8b` fit together (7.2 GB), so this did not happen.

## The server-side fix (not applied)

`OLLAMA_MAX_LOADED_MODELS=1` in the service's environment keeps only one model loaded, so a new model
always gets the whole GPU:

```bash
sudo systemctl edit ollama      # add: [Service] Environment="OLLAMA_MAX_LOADED_MODELS=1"
sudo systemctl restart ollama
```

It is not applied here, for two reasons. It changes a systemd unit as root, and restarting the service
stops any request in progress. And it makes a job that uses two models in turn reload a model at every
switch, even when both would fit. The watchdog acts only when there is a problem.

## Undo

Stop the `watch` process. The script changes no configuration, so nothing else needs undoing.
