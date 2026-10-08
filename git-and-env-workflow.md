# Git Commits and Environment Files

This is the workflow we used when the commit message needed to become `env config` and the project contained private environment variables.

## 1. Keep secrets in `.env`

Use `.env` for real local credentials:

```env
STRIPE_SECRET_KEY=your_real_local_key
STRIPE_WEBHOOK_SECRET=your_real_local_webhook_secret
```

The `.env` file should be ignored by Git. Check that `.gitignore` contains:

```gitignore
.env
```

Commit only a safe template such as `.env.example`:

```env
STRIPE_SECRET_KEY=sk_test_replace_me
STRIPE_WEBHOOK_SECRET=whsec_replace_me_from_stripe_listen
```

The template tells another developer which variables are required without exposing credentials.

## 2. Check what Git sees

Run these from the repository folder:

```powershell
git status
git log --oneline -5
git diff
git diff --cached
```

Useful meanings:

- `git status` shows changed, staged, and untracked files.
- `git diff` shows unstaged changes.
- `git diff --cached` shows changes prepared for the next commit.
- `git log --oneline -5` shows the latest five commit titles.

Before committing, check for accidental secrets:

```powershell
git diff --cached
```

Never paste real API keys into a commit, screenshot, chat, or public repository.

## 3. Stage and create a commit

Stage only the files that belong together:

```powershell
git add .gitignore
git add my_python_work/web_practice/03_mini_checkout_lab/.env.example
git add my_python_work/web_practice/03_mini_checkout_lab/mini_checkout_lab/settings.py
```

Review the staged version, then commit it:

```powershell
git diff --cached --check
git commit -m "env config"
```

The `-m` value is the commit message. A good message briefly describes the change, such as `env config`, `fix Stripe webhook setup`, or `add receipt emails`.

## 4. Rename the latest commit

If the latest commit already exists but its title is wrong, amend only that commit:

```powershell
git commit --amend -m "env config"
```

This creates a replacement commit with the same file changes and a new message. Git commit IDs include the message, so the commit ID changes too.

Check the result:

```powershell
git log -1 --oneline
git status
```

## 5. Push an amended commit safely

If the old version was already pushed, the remote branch still points to the old commit. Update it with:

```powershell
git push --force-with-lease origin main
```

`--force-with-lease` is safer than plain `--force`: it refuses to overwrite newer work that appeared on GitHub after your last fetch.

After pushing, verify synchronization:

```powershell
git fetch origin
git status
git log --oneline --decorate -3
```

A clean, synchronized branch should say that it is up to date with `origin/main`.

## 6. If Git says one push and one pull

That means the local and remote branches have different commits. Do not immediately reset anything. First inspect both sides:

```powershell
git fetch origin
git log --oneline --decorate --graph --all -10
```

If the only difference is your amended local commit, use:

```powershell
git push --force-with-lease origin main
```

If GitHub contains someone else’s work, stop and inspect before choosing a merge or rebase. Never delete commits blindly.

## 7. Environment variables in VS Code

The project can load variables from:

```text
my_python_work/03_mini_checkout_lab/.env
```

The workspace setting can point Python terminals at that file:

```json
{
  "python.terminal.useEnvFile": true,
  "python.envFile": "${workspaceFolder}/my_python_work/web_practice/03_mini_checkout_lab/.env"
}
```

After changing `.env`, restart the Django server. A running process keeps the environment it received when it started.

To check a variable in PowerShell without printing its secret:

```powershell
if ($env:STRIPE_SECRET_KEY) {
    Write-Host "Stripe key is loaded"
} else {
    Write-Host "Stripe key is missing"
}
```

## The short version

For a normal safe change:

```powershell
git status
git add <files>
git diff --cached --check
git commit -m "describe the change"
git push origin main
```

For correcting the latest commit title after it was pushed:

```powershell
git commit --amend -m "env config"
git push --force-with-lease origin main
```

