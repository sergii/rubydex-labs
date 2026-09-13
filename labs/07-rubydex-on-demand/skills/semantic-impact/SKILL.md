# Semantic impact tracing

When analyzing a change to a Ruby method:

1. Trace real callers, not lexical mentions.
2. Check inheritance and aliases before deciding which public behavior reaches the changed method.
3. Check whether subclasses override extension hooks called by the changed method.
4. Remember that a Ruby class may be reopened in another file.
5. Treat similarly named legacy classes, comments, and strings as possible decoys unless they are structurally connected.
6. Translate the structural path into system consequences using the supplied architecture knowledge.

Use deterministic semantic tooling when available and useful, but do not call tools merely because they exist.
