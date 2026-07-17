# Release Notes

One text file per RHDH release, extracted from the official Red Hat documentation.

These are **maintainer-managed files** — users of the skill do not need any tools to use them. The skill reads local files only.

## File naming

`{major}.{minor}.md` — e.g., `1.9.md`, `1.10.md`

## How to add a new release

Pick whichever method works for you:

**Option A — lynx + Claude (recommended):**

```bash
# Install lynx (one-time): brew install lynx / dnf install lynx / apt install lynx
lynx -dump -nolist \
  "https://docs.redhat.com/en/documentation/red_hat_developer_hub/{X.Y}/html-single/red_hat_developer_hub_release_notes/index" \
  > raw.txt
```

Then ask Claude to convert it:

```
Convert raw.txt to a release notes markdown file matching the format in
skills/rhdh-upgrade-helper/references/release-notes/1.10.md
```

Claude strips the navigation boilerplate and structures it into the required sections.

**Option B — paste from browser + Claude:**
Open the single-page release notes URL in your browser, select all, copy, paste into `raw.txt`. Then ask Claude to convert it as above.

**Option C — PDF + Claude:**
Download the PDF from docs.redhat.com, convert with `pdftotext -layout file.pdf raw.txt`. Then ask Claude to convert it as above.

### Required sections

Keep these sections in each file:

- New features and enhancements
- Technology Preview
- Deprecated features
- Removed features (breaking changes)
- Known issues
- Fixed issues (include only upgrade-relevant fixes)

## How the skill uses these files

`workflows/full-report.md` Step 4c reads the release notes files for every release in the FROM→TO range. For example, `--from 1.8 --to 1.10` reads `1.9.md` and `1.10.md` to gather all breaking changes and new features across the skipped releases.

If a file is missing for a version in the range, the report notes the gap and points users to the official docs URL.
