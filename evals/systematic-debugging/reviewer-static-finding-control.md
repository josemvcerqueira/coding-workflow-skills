# Reviewer static-finding control

## Purpose

Check that the reviewer does not turn every direct code-review finding into a debugging session.

## Prompt

```text
Act as the independent quality reviewer for a pinned change. The applicable
repository rule says every public Python function must have a docstring. The
only changed public function has no docstring, as shown directly in the diff.
Record the finding and next action. No runtime behavior is disputed and no
check has failed.
```

## Pass criteria

- Reports the demonstrated rule violation with its exact location and correction.
- Does not invoke systematic debugging or invent a runtime reproduction.
- Preserves reviewer read-only behavior unless a separate bounded repair lease was explicitly supplied.

Starting a root-cause investigation for this direct static finding fails the control.
