# Publish this story to GitHub Pages

The project is a plain static website. GitHub Pages can host it without React, Node, npm, a backend, or an API key. The recommended setup uses the repository **root**.

## Method A: GitHub website, no command line

1. In GitHub, create a new repository (for example, `golf-animated-story`). You choose whether the repository is public or private, subject to your GitHub plan's Pages availability.
2. Download the project ZIP and **extract it**. Upload the **contents of the `golf-animated-story` folder**, including `index.html`, `.nojekyll`, `assets/`, `css/`, `data/`, `js/`, `docs/`, `dist/`, and `tools/`, into the repository root.
3. Open **Settings → Pages**.
4. Under **Build and deployment**, select **Deploy from a branch**. Choose `main` and `/(root)`, then save.
5. After GitHub completes publishing, the address should resemble `https://YOUR_USERNAME.github.io/golf-animated-story/`.
6. Verify the story, clue overlays, chapter navigation, and sources on the published URL.

GitHub's interface and plan requirements can change; see [GitHub Pages documentation](https://docs.github.com/en/pages/quickstart).

## Method B: Git command line

From inside this folder:

```bash
git init
git add .
git commit -m "Publish 43-scene animated golf story"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/golf-animated-story.git
git push -u origin main
```

Then enable Pages as in Method A. Create the empty GitHub repository before pushing; never paste an access token into this project.

## Important technical details

- The site uses **relative paths**. It works at `username.github.io/repo-name/`, not just at the domain root.
- `index.html` is the entry point.
- `.nojekyll` prevents unwanted Jekyll processing of the static folder.
- The website needs no server-side components, authentication, analytics, or paid hosting.
- Direct file opening is also supported (`file://`) because `data/scenes.js` and `data/illustrations.js` are regular scripts, not `fetch()` requests.
- A link such as `#scene=30` opens a specific scene on the hosted site.
- The alternate single-file story can be downloaded from `dist/` and opened offline.

## Domain and future options

You can later configure a custom domain from **Settings → Pages → Custom domain**. Only create a `CNAME` file when you know the domain and have configured DNS. Do not put credentials, private notes, or anything you do not intend to publish inside this GitHub Pages project.

## Publish responsibly

This exhibition includes allegations and unproven theories involving historical institutions and child exploitation. Keep the evidentiary labels and source context visible; check primary sources before asserting particular historical crimes as established facts. The underlying private Google Drive dossier has deliberately not been bundled.
