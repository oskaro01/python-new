# Repairing A Git Commit Message Safely

This is the workflow for correcting the latest commit title when the commit is
already on GitHub and the working tree also contains newer, uncommitted work.

## The situation

Suppose the latest commit was accidentally named after a terminal command:

```text
.\.venv\Scripts\python.exe ... run_chat_cleanup --interval 2
```

The files in that commit are correct. Only the message is wrong. At the same
time, the next lesson may already have edits that must remain uncommitted.

## 1. Inspect before changing anything

```powershell
git status --short --branch
git log --oneline --decorate -4
git show --stat --oneline HEAD
git diff
git diff --cached
```

Read the results this way:

- `HEAD` is the commit currently checked out.
- `git diff` is work in the working tree that is not staged.
- `git diff --cached` is work already staged for the next commit.
- A clean branch line such as `main...origin/main` means local and remote
  pointers currently agree.

Do not use `git reset --hard` to solve a naming problem. That could delete the
newer uncommitted lesson work.

## 2. Protect newer lesson work

`git commit --amend` replaces the latest commit using the current index. If
newer files are staged, they could accidentally become part of the amended
commit. Before amending, make sure the new lesson edits are unstaged:

```powershell
git diff --cached
```

If the output shows newer lesson files, unstage only those files. This keeps
their contents in the working tree:

```powershell
git restore --staged <file>
```

Then check again:

```powershell
git diff --cached
```

For our Chat Lab repair, the async composer files stayed uncommitted while the
Lesson 19 commit was renamed.

## 3. Replace the latest message

Use `--amend` because the latest commit's file snapshot is already correct:

```powershell
git commit --amend -m "Lesson 19: background cleanup and disappearing messages"
```

This does not create a second Lesson 19 commit. It creates a replacement commit
with the same files and a new message. The commit ID changes because Git hashes
the commit message as part of the commit:

```text
old bc3d8a3  ->  new a6c9339
```

Check locally:

```powershell
git log -1 --oneline
git status --short --branch
```

The uncommitted files should still appear with `M` or `??` in `git status`.

## 4. Update GitHub safely

GitHub still points to the old commit ID, so a normal push is rejected. Because
we are intentionally replacing our own latest commit, update the remote with:

```powershell
git push --force-with-lease origin main
```

`--force-with-lease` checks that the remote still has the commit you last saw.
It refuses to overwrite newer remote work that appeared after your last fetch.
Plain `--force` skips that protection and should not be the default workflow.

## 5. Verify both pointers

```powershell
git fetch origin
git status --short --branch
git log --oneline --decorate -4
```

The branch should show `main...origin/main` with no ahead/behind count. The
new commit message should have both `HEAD -> main` and `origin/main` beside it.
Your newer lesson edits should still be listed separately as uncommitted.

## If you want to rename an older commit

For an older commit, use an interactive rebase:

```powershell
git rebase -i HEAD~3
```

In the editor, change `pick` to `reword` for the commit whose message needs
changing, save and close, then enter the new message when Git asks. After the
rebase finishes, inspect the history and use `git push --force-with-lease` if
the old history was already pushed.

The text `e -i HEAD~3` is not a Git command or a special file. The command is
`git rebase -i HEAD~3`; `-i` means interactive.

## Memory hook

```text
inspect -> keep newer work unstaged -> amend latest -> force-with-lease -> verify
```

Suggested normal lesson workflow afterward:

```powershell
git add <lesson-files>
git diff --cached --check
git commit -m "add async chat composer"
git push origin main
```
