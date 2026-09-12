#!/usr/bin/env python3
"""Publish a blog post to sexualempowermentforwomen.com via the WordPress REST API.

Uploads the post image to the media library, then creates the post with that
image inlined and set as the featured image.

Credentials come from the environment, never from the repo:

    export WP_USER="tarisha"
    export WP_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"

Usage:
    python3 automation/publish_post.py --status draft
    python3 automation/publish_post.py --status publish

The script refuses to overwrite an existing post with the same slug unless
--update is passed, and prints what it is about to do before it does it.
"""

import argparse
import base64
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request

SITE = "https://sexualempowermentforwomen.com"
API = SITE + "/wp-json/wp/v2"

BODY_FILE = "content/blog/ship-model-wordpress.html"
IMAGE_FILE = "images/infographics/ship-model-wheel-serw.jpg"

SLUG = "low-libido-after-40-five-things"
TITLE = "Low Libido After 40? You Have Five Other Things Going On"
EXCERPT = (
    "Low libido after 40 is almost never one thing. A sex therapist on the "
    "five doors the SHIP model opens, and why nothing about you is broken."
)
CATEGORY_SLUGS = ["female-sexual-desire", "sexuality", "relationships", "self-help"]
IMAGE_ALT = (
    "The SHIP model. An outer ring holds five foundations: systemic, bio "
    "psycho social cultural, across the lifespan, empiricism and "
    "intersectionality. Five inner circles hold the therapeutic components: "
    "sexual adaptation and resilience, relational intimacy, pleasure oriented "
    "positive sexuality, multidisciplinary care and sexual literacy."
)
IMAGE_CAPTION = (
    "The SHIP model, redrawn in my colours. The model itself was developed by "
    "Girard, Newstrom, Connor, Arenella, Vencill and Robinson (2023), Journal "
    "of Marital and Family Therapy."
)


def auth_header():
    user = os.environ.get("WP_USER")
    pw = os.environ.get("WP_APP_PASSWORD")
    if not user or not pw:
        sys.exit(
            "Set WP_USER and WP_APP_PASSWORD first.\n"
            "The application password is created in WordPress under "
            "Users, Profile, Application Passwords."
        )
    token = base64.b64encode(f"{user}:{pw}".encode()).decode()
    return "Basic " + token


def call(method, url, data=None, headers=None, raw=False):
    headers = dict(headers or {})
    headers["Authorization"] = auth_header()
    body = None
    if data is not None:
        if raw:
            body = data
        else:
            body = json.dumps(data).encode()
            headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode()[:600]
        sys.exit(f"{method} {url} failed: {e.code}\n{detail}")


def category_ids(slugs):
    ids = []
    for slug in slugs:
        url = f"{API}/categories?slug={slug}&_fields=id,slug"
        with urllib.request.urlopen(url, timeout=60) as r:
            found = json.loads(r.read().decode())
        if not found:
            sys.exit(f"No category with slug {slug!r} on the site.")
        ids.append(found[0]["id"])
    return ids


def existing_post(slug):
    url = f"{API}/posts?slug={slug}&status=any&_fields=id,link,status"
    req = urllib.request.Request(url, headers={"Authorization": auth_header()})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            found = json.loads(r.read().decode())
    except urllib.error.HTTPError:
        return None
    return found[0] if found else None


def upload_image(path):
    name = os.path.basename(path)
    ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
    with open(path, "rb") as fh:
        blob = fh.read()
    media = call(
        "POST",
        f"{API}/media",
        data=blob,
        raw=True,
        headers={
            "Content-Disposition": f'attachment; filename="{name}"',
            "Content-Type": ctype,
        },
    )
    call(
        "POST",
        f"{API}/media/{media['id']}",
        data={"alt_text": IMAGE_ALT, "caption": IMAGE_CAPTION, "title": "The SHIP model"},
    )
    return media["id"], media["source_url"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", choices=["draft", "publish"], default="draft")
    ap.add_argument("--update", action="store_true",
                    help="update the post if one already exists at this slug")
    args = ap.parse_args()

    body = open(BODY_FILE).read()
    cats = category_ids(CATEGORY_SLUGS)

    prior = existing_post(SLUG)
    if prior and not args.update:
        sys.exit(
            f"A post already exists at /{SLUG}/ (id {prior['id']}, "
            f"{prior['status']}): {prior['link']}\n"
            "Pass --update to change it."
        )

    print(f"Site      {SITE}")
    print(f"Post      {TITLE}")
    print(f"Slug      /{SLUG}/")
    print(f"Category  {', '.join(CATEGORY_SLUGS)} (ids {cats})")
    print(f"Status    {args.status}")
    print(f"Action    {'update id ' + str(prior['id']) if prior else 'create new'}")
    print()

    print("Uploading image ...")
    media_id, media_url = upload_image(IMAGE_FILE)
    print(f"  media id {media_id}\n  {media_url}")

    payload = {
        "title": TITLE,
        "slug": SLUG,
        "status": args.status,
        "content": body.replace("__IMAGE_URL__", media_url),
        "excerpt": EXCERPT,
        "categories": cats,
        "featured_media": media_id,
        "comment_status": "open",
    }

    if prior:
        post = call("POST", f"{API}/posts/{prior['id']}", data=payload)
    else:
        post = call("POST", f"{API}/posts", data=payload)

    print()
    print(f"Done. id {post['id']}, status {post['status']}")
    print(post["link"])


if __name__ == "__main__":
    main()
