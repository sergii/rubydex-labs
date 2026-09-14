# Identity boundary

## Thesis

> Identity links answer whether two representations refer to the same durable thing or how one representation maps to that thing. Domain relationships belong in assertions.

The existing `identity-link.schema.json` intentionally remains unchanged for compatibility while Lab 13 validates a narrower contract.

## Keep in the identity layer

These relations are identity/representation semantics:

```text
SAME_AS
RENAMED_FROM
MOVED_FROM
REPRESENTS
OBSERVED_AS
```

`DEPLOYED_AS` is provisionally allowed only when it means representation mapping between a durable entity and its deployment representation. If it instead means an operational/domain relationship, it should become an assertion.

## Move to ordinary assertions

These are claims about the world, not identity equivalence or representation continuity:

```text
IMPLEMENTED_BY
OWNED_BY
SERVES_CAPABILITY
DERIVED_FROM
```

Examples:

```text
Service --OWNED_BY--> Team
Capability --IMPLEMENTED_BY--> Service
Service --SERVES_CAPABILITY--> Capability
Assertion --DERIVED_FROM--> Assertion
```

should be modeled as evidence-backed assertions so they can carry kind, provenance, scope, valid time, confidence, conflict/comparison semantics, and temporal evolution.

## Why this matters

An ownership change must not alter the identity of the service. A capability can gain or lose implementations without becoming a different capability. A service can serve several capabilities. These are mutable domain facts.

Identity links have a much stricter job:

```text
representation A
        ↓
identity continuity / mapping
        ↓
durable entity
```

## Lab 13 invariant

> If a relation can change while both endpoint entities remain the same entities, it is probably an assertion, not an identity link.

This is not a universal logical proof, but it is a strong default design rule.

## Non-breaking migration rule

Do not remove legacy enum values from `identity-link.schema.json` yet. During Lab 13:

1. classify each relation as `IDENTITY`, `REPRESENTATION`, or `DOMAIN_ASSERTION`;
2. reject new domain relations from the identity path;
3. emit equivalent `Assertion` fixtures for domain relations;
4. validate that comparison/conflict semantics work correctly on those assertions;
5. only then consider a v2 identity schema.
