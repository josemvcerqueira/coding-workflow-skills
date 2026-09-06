# Review snapshot

Review the implementation the ticket names, not whichever branch happens to be open. Record the repository and checkout paths, baseline commit, target commit or working-tree identity, spec digest, and included files. Resolve branch names and tags to commit IDs.

For committed work, compare the exact baseline and target commits. Use a merge base only when the ticket defines a branch comparison. Record the resolved merge-base commit. Never infer that a three-dot diff includes uncommitted changes.

For uncommitted work, inspect status, staged changes, unstaged changes, and untracked files. `git diff <baseline>` includes tracked working-tree changes relative to that baseline; inspect ticket-owned untracked files separately. Include deletions, file modes, and relevant generated artifacts. Identify unrelated changes and exclude them without discarding them.

Record a reproducible content identity for dirty work: baseline plus the included paths, SHA-256 hashes of file contents, and explicit deleted paths and modes. For committed work, the target commit identifies content. Preserve separate stage information if it matters to the assignment. Do not create a commit just to obtain an identity.

An empty diff is not an automatic pass. Resolve wrong baselines or missing changes. An outcome already satisfied by unchanged code can be reviewed only with an explicit explanation and current requirement evidence.

Both reviewers must inspect the same target. Use a stable checkout with no concurrent implementation edits or an isolated copy that contains all in-scope dirty files. A new worktree from HEAD alone omits uncommitted work. Do not reset, stash, or overwrite user changes to create isolation.

Hash the spec when review starts. If it differs from the ticket set's recorded digest, inspect the change and its effect on this ticket. Do not rewrite the index digest as if every ticket were reconciled. Preserve resolved decisions and report material scope changes.

Before finalization, compare the target, relevant spec, and standards inputs again. Exclude review artifacts and expected disposable test output from the code identity. If relevant inputs changed, preserve the old reports as stale and obtain both reviewers' assessments of the current target. Each must state whether its prior evidence still applies and run affected checks again. No pass carries forward silently.
