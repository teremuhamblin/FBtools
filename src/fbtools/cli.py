"""Point d'entrée de la CLI `fbtools`."""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import click

from . import __version__
from .client import GraphAPIError, GraphClient
from .config import Config
from .output import render, to_csv, to_json

FORMAT = click.option("-f", "--format", "fmt", type=click.Choice(["table", "json", "csv"]),
                      default="table", show_default=True, help="Format de sortie.")


def get_client(ctx: click.Context) -> GraphClient:
    cfg: Config = ctx.obj["config"]
    if not cfg.access_token:
        raise click.UsageError("Aucun jeton configuré. Lancez `fbtools config set-token`.")
    return GraphClient(cfg.access_token, cfg.api_version, cfg.app_secret)


def resolve_page(ctx: click.Context, page_id: str | None) -> str:
    page_id = page_id or ctx.obj["config"].default_page_id
    if not page_id:
        raise click.UsageError("Indiquez --page ou définissez une Page par défaut "
                               "(`fbtools config set-page <ID>`).")
    return page_id


def parse_when(value: str) -> int:
    """Convertit une date ISO 8601 (ex. 2026-12-01T09:00+01:00) en timestamp Unix."""
    try:
        dt = datetime.fromisoformat(value)
    except ValueError as exc:
        raise click.BadParameter("Format attendu : AAAA-MM-JJTHH:MM[+HH:MM]") from exc
    if dt.tzinfo is None:
        dt = dt.astimezone()  # fuseau local
    ts = int(dt.timestamp())
    if ts < int(datetime.now(timezone.utc).timestamp()) + 600:
        raise click.BadParameter("La publication programmée doit être au moins 10 min dans le futur.")
    return ts


@click.group()
@click.version_option(__version__, prog_name="fbtools")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """FBtools — gérez vos Pages Facebook depuis le terminal."""
    ctx.ensure_object(dict)
    ctx.obj["config"] = Config.load()


# ---------------- config ----------------
@cli.group()
def config() -> None:
    """Configurer le jeton, la version d'API et la Page par défaut."""


@config.command("set-token")
@click.option("--token", prompt="Jeton d'accès utilisateur", hide_input=True)
@click.option("--app-secret", default=None, help="Secret d'app (active appsecret_proof).")
@click.pass_context
def config_set_token(ctx, token: str, app_secret: str | None) -> None:
    cfg: Config = ctx.obj["config"]
    cfg.access_token = token.strip()
    if app_secret:
        cfg.app_secret = app_secret.strip()
    click.echo(f"Configuration enregistrée dans {cfg.save()}")


@config.command("set-version")
@click.argument("version")
@click.pass_context
def config_set_version(ctx, version: str) -> None:
    cfg: Config = ctx.obj["config"]
    cfg.api_version = version if version.startswith("v") else f"v{version}"
    cfg.save()
    click.echo(f"Version d'API : {cfg.api_version}")


@config.command("set-page")
@click.argument("page_id")
@click.pass_context
def config_set_page(ctx, page_id: str) -> None:
    cfg: Config = ctx.obj["config"]
    cfg.default_page_id = page_id
    cfg.save()
    click.echo(f"Page par défaut : {page_id}")


@config.command("show")
@click.pass_context
def config_show(ctx) -> None:
    click.echo(to_json(ctx.obj["config"].masked()))


# ---------------- compte ----------------
@cli.command()
@click.pass_context
def whoami(ctx) -> None:
    """Afficher l'utilisateur associé au jeton et ses permissions."""
    client = get_client(ctx)
    me = client.me()
    perms = client.permissions()
    granted = sorted(p["permission"] for p in perms if p.get("status") == "granted")
    click.echo(f"{me.get('name')} (id {me.get('id')}) — API {client.api_version}")
    click.echo("Permissions : " + (", ".join(granted) or "aucune"))


# ---------------- pages ----------------
@cli.group()
def pages() -> None:
    """Lister les Pages administrées."""


@pages.command("list")
@FORMAT
@click.pass_context
def pages_list(ctx, fmt: str) -> None:
    rows = [{k: v for k, v in p.items() if k != "access_token"} for p in get_client(ctx).pages()]
    click.echo(render(rows, fmt, ["id", "name", "category"]))


# ---------------- posts ----------------
@cli.group()
def posts() -> None:
    """Lister, publier, programmer et supprimer des publications."""


@posts.command("list")
@click.option("--page", "page_id", help="ID de la Page.")
@click.option("-n", "--limit", default=25, show_default=True)
@FORMAT
@click.pass_context
def posts_list(ctx, page_id, limit: int, fmt: str) -> None:
    rows = get_client(ctx).posts(resolve_page(ctx, page_id), limit=limit)
    click.echo(render(rows, fmt, ["id", "created_time", "message", "permalink_url"]))


@posts.command("publish")
@click.option("--page", "page_id", help="ID de la Page.")
@click.option("-m", "--message", help="Texte de la publication.")
@click.option("--message-file", type=click.Path(exists=True, dir_okay=False, path_type=Path),
              help="Lire le texte depuis un fichier.")
@click.option("--link", help="Lien à partager.")
@click.option("--at", "when", help="Programmer (ISO 8601, ex. 2026-12-01T09:00+01:00).")
@click.option("--dry-run", is_flag=True, help="Afficher la requête sans publier.")
@click.option("-y", "--yes", is_flag=True, help="Ne pas demander de confirmation.")
@click.pass_context
def posts_publish(ctx, page_id, message, message_file, link, when, dry_run, yes) -> None:
    page_id = resolve_page(ctx, page_id)
    if message_file:
        message = message_file.read_text(encoding="utf-8").strip()
    if not message and not link:
        raise click.UsageError("Indiquez --message, --message-file ou --link.")
    ts = parse_when(when) if when else None
    summary = {"page": page_id, "message": message, "link": link,
               "scheduled_publish_time": ts}
    if dry_run:
        click.echo(to_json({"dry_run": True, **summary}))
        return
    if not yes:
        click.echo(to_json(summary))
        click.confirm("Publier ?" if not ts else "Programmer ?", abort=True)
    res = get_client(ctx).publish(page_id, message, link, ts)
    click.echo(("Programmée" if ts else "Publiée") + f" : {res.get('id')}")


@posts.command("delete")
@click.argument("post_id")
@click.option("-y", "--yes", is_flag=True)
@click.pass_context
def posts_delete(ctx, post_id: str, yes: bool) -> None:
    if not yes:
        click.confirm(f"Supprimer définitivement {post_id} ?", abort=True)
    res = get_client(ctx).delete_post(post_id)
    click.echo("Supprimée." if res.get("success") else to_json(res))


# ---------------- comments ----------------
@cli.group()
def comments() -> None:
    """Exporter les commentaires d'une publication."""


@comments.command("export")
@click.argument("post_id")
@click.option("-n", "--limit", type=int, default=None, help="Nombre max (défaut : tous).")
@click.option("-o", "--output", type=click.Path(dir_okay=False, path_type=Path),
              help="Fichier de sortie (.csv ou .json). Défaut : stdout en CSV.")
@click.pass_context
def comments_export(ctx, post_id: str, limit, output: Path | None) -> None:
    rows = get_client(ctx).comments(post_id, limit=limit)
    cols = ["id", "created_time", "from.id", "from.name", "message", "like_count", "comment_count"]
    text = to_json(rows) if output and output.suffix == ".json" else to_csv(rows, cols)
    if output:
        output.write_text(text, encoding="utf-8")
        click.echo(f"{len(rows)} commentaires exportés vers {output}")
    else:
        click.echo(text, nl=False)


# ---------------- insights ----------------
DEFAULT_METRICS = "page_post_engagements,page_total_media_view_unique,page_follows"


@cli.command()
@click.option("--page", "page_id", help="ID de la Page.")
@click.option("--metric", "metrics", default=DEFAULT_METRICS, show_default=True,
              help="Métriques séparées par des virgules.")
@click.option("--period", type=click.Choice(["day", "week", "days_28", "month", "lifetime"]),
              default="day", show_default=True)
@click.option("--since", help="Date de début (AAAA-MM-JJ).")
@click.option("--until", help="Date de fin (AAAA-MM-JJ).")
@FORMAT
@click.pass_context
def insights(ctx, page_id, metrics, period, since, until, fmt) -> None:
    """Afficher les statistiques d'une Page."""
    data = get_client(ctx).insights(resolve_page(ctx, page_id),
                                    [m.strip() for m in metrics.split(",") if m.strip()],
                                    period, since, until)
    if fmt == "json":
        click.echo(to_json(data))
        return
    rows = [{"metric": m.get("name"), "period": m.get("period"),
             "end_time": v.get("end_time"), "value": v.get("value")}
            for m in data for v in m.get("values", [])]
    click.echo(render(rows, fmt, ["metric", "period", "end_time", "value"]))


def main() -> None:
    try:
        cli(standalone_mode=True)
    except GraphAPIError as exc:
        click.secho(f"Erreur API Graph : {exc}", fg="red", err=True)
        sys.exit(2)
    except ValueError as exc:
        click.secho(f"Erreur : {exc}", fg="red", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
