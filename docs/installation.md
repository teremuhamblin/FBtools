# Installation

FBtools nécessite **Python 3.10 ou plus**.

=== "pipx (recommandé)"

    ```bash
    pipx install git+https://github.com/teremuhamblin/FBtools.git
    fbtools --version
    ```

=== "pip"

    ```bash
    python -m venv .venv && source .venv/bin/activate
    pip install git+https://github.com/teremuhamblin/FBtools.git
    ```

=== "Docker"

    ```bash
    docker run --rm -it \
      -e FBTOOLS_ACCESS_TOKEN \
      -v fbtools-config:/config \
      ghcr.io/teremuhamblin/fbtools:latest pages list
    ```

    L'image est publiée sur GHCR à chaque version taguée.

=== "Depuis les sources"

    ```bash
    git clone https://github.com/teremuhamblin/FBtools.git
    cd FBtools
    python -m venv .venv && source .venv/bin/activate
    pip install -e ".[dev]"
    ```

## Vérifier l'installation

```bash
fbtools --version
fbtools --help
python -m fbtools --help   # équivalent
```

## Mettre à jour

```bash
pipx upgrade fbtools                                              # pipx
pip install -U git+https://github.com/teremuhamblin/FBtools.git   # pip
```
