# Giving Claude Code durable Dropbox access

Two routes. Route A is two minutes and probably all that is needed. Route B is
the full permanent grant, from scratch.

Dropbox access tokens expire after four hours. A **refresh token** does not
expire, so anything described here as permanent means a refresh token plus the
app key and app secret. That trio is what `automation/fetch_dropbox_images.py`
already prefers, and what the `Fetch Dropbox images` workflow already uses.

---

## Route A, you already have permanent access, just point it at the photos

The repo already holds these as GitHub Actions secrets, and the last run's
`images/_diagnostic.json` shows the refresh exchange working:

```
DROPBOX_REFRESH_TOKEN
DROPBOX_APP_KEY
DROPBOX_APP_SECRET
DROPBOX_FOLDER_URL              → the daily social photos folder
DROPBOX_INFOGRAPHIC_FOLDER_URL  → /A Radiant Woman/Content Club/Infographics
```

Neither folder holds the website photography. Notion says that lives at
`/A Radiant Woman/Marketing/love-adventure-photos/`.

The script reads folders through **shared links**, not paths, so all that is
missing is a shared link to that folder.

1. Open Dropbox, find `A Radiant Woman / Marketing / love-adventure-photos`
2. Share, then Create link, then Copy link
3. Add it in both places below, as `DROPBOX_WEBSITE_FOLDER_URL`

Nothing else changes, and the existing token keeps working.

---

## Route B, a fresh permanent grant from scratch

Do this only if the existing app is gone, or its scopes are wrong, or the
access should be separated from the old Radiant Woman automation.

### 1. Create the app

Go to <https://www.dropbox.com/developers/apps>, choose **Create app**.

- **Choose an API:** Scoped access
- **Type of access:** see the note below before choosing
- **Name:** anything unused, for example `claude-code-tla`

**On access type.** *App folder* creates one sandboxed folder and the app can
never see anything else. *Full Dropbox* means every file in the account,
including `05 Personal/Separation Starr Family/`. The photo fetching only ever
needs the folders that are explicitly shared with it, so App folder, or Full
Dropbox with only `sharing.read` ticked, both do the job without exposing the
personal and legal material. Full Dropbox with read scopes is the literal
"full access forever" and it is a real choice, just make it knowingly.

### 2. Tick the scopes

On the **Permissions** tab:

| Scope | Needed for |
|---|---|
| `sharing.read` | required, this is what the fetch script actually calls |
| `files.metadata.read` | listing folders by path rather than shared link |
| `files.content.read` | downloading by path rather than shared link |
| `files.content.write` | only if Claude should upload or change files |

Click **Submit** at the bottom. Scopes do not apply until submitted, and a
token minted before submitting will not carry them.

### 3. Copy the app key and secret

**Settings** tab, near the top. Both are needed.

### 4. Authorise, with offline access

Open this in a browser, replacing `APP_KEY`:

```
https://www.dropbox.com/oauth2/authorize?client_id=APP_KEY&response_type=code&token_access_type=offline
```

`token_access_type=offline` is the part that makes it permanent. Without it
you get a four hour token and have to do this again.

Click **Allow**, then copy the authorisation code it shows.

### 5. Exchange the code for the refresh token

The code is single use and expires within minutes, so do this promptly.

```bash
curl -sS https://api.dropbox.com/oauth2/token \
  -u "APP_KEY:APP_SECRET" \
  -d grant_type=authorization_code \
  -d code=THE_CODE_FROM_STEP_4
```

The reply contains `"refresh_token": "..."`. That value never expires.

If there is no way to run curl, paste the app key, app secret and code into
the session and Claude will run the exchange and hand back the refresh token.
Anything pasted into a chat should be treated as exposed, so revoke and redo
it later if that matters.

---

## Where to put the values

Two different places, doing two different jobs. For both, set all four:

```
DROPBOX_REFRESH_TOKEN
DROPBOX_APP_KEY
DROPBOX_APP_SECRET
DROPBOX_WEBSITE_FOLDER_URL
```

**GitHub Actions secrets**, so the `Fetch Dropbox images` workflow can run:
repo → Settings → Secrets and variables → Actions → New repository secret.

**The Claude Code environment**, so Claude can use Dropbox live during a
session: Claude Code on the web → the environment used for this project →
its environment variables.

Setting only the first means the workflow works but Claude cannot fetch
anything mid-session. Setting only the second means the reverse.

---

## Revoking

<https://www.dropbox.com/account/connected_apps>, find the app, Disconnect.
That kills the refresh token immediately and everything using it stops. Worth
knowing before granting anything, and worth doing to any credential that has
been pasted into a chat.
