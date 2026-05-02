# Images

The 20 post images live here as `image-1.jpg` through `image-20.jpg`,
matching the `image` field in `content/posts.json`. The `raw/` subfolder
holds the originals downloaded from Dropbox so you can verify the match.

## How they're produced

The `Fetch Dropbox images` workflow runs in two phases:

1. **Phase 1** — downloads every image in the Dropbox shared folder to
   `images/raw/` keeping the original filename.
2. **Phase 2** — reads `images/mapping.json` and copies each raw file to
   `images/image-N.jpg` (where N matches the post id).

If `mapping.json` is missing, phase 2 is skipped — only the raw download
runs. That gives you a chance to inspect the raw images and decide which
goes with which post before producing the named copies.

## mapping.json

```json
{
  "Original Filename From Dropbox.jpg": 1,
  "Another File.png": 2,
  ...
}
```

The value is the post id (1..20). After committing `mapping.json`, the
workflow runs phase 2 automatically and produces the named copies.

## Hook → image-N mapping

| File | Hook |
|---|---|
| `image-1.jpg` | You're not broken. You're exhausted. |
| `image-2.jpg` | No one told you desire could disappear this slowly. |
| `image-3.jpg` | You're not fighting. But something is missing. |
| `image-4.jpg` | You miss being looked at like that. |
| `image-5.jpg` | The loneliest place can be next to someone you love. |
| `image-6.jpg` | This is how she came back to herself. |
| `image-7.jpg` | Everything looks fine. That's the part that hurts. |
| `image-8.jpg` | You don't hate your body. You've stopped listening to her. |
| `image-9.jpg` | There is nothing wrong with wanting more. |
| `image-10.jpg` | Maybe you're not tired of sex. Maybe you're tired of performing. |
| `image-11.jpg` | The love is still there. The closeness got buried. |
| `image-12.jpg` | Your body was never the enemy. |
| `image-13.jpg` | Desire doesn't come back through pressure. |
| `image-14.jpg` | When did love become logistics? |
| `image-15.jpg` | You've been holding everyone together. But who's holding you? |
| `image-16.jpg` | One honest sentence can change the whole room. |
| `image-17.jpg` | Your sensuality didn't vanish. It went underground. |
| `image-18.jpg` | It's not about sex. It's about feeling wanted. |
| `image-19.jpg` | The woman you miss is still in there. |
| `image-20.jpg` | Come back to your body before you try to fix your desire. |
