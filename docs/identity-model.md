# Identity model

The evidence-backed world model needs stable identity across code, runtime, architecture, deployment, and time.

The hard problem is not naming. It is deciding when two observations refer to the same underlying thing, when one thing represents another, and when two similarly named things must remain distinct.

## Core rule

> Names are observations. Identity is a durable system concept.

A rename must not create a new logical entity merely because a symbol or service name changed. Conversely, equal names must never be treated as proof of equal identity.

```text
name != identity
path != identity
runtime service.name != identity
repository symbol != business capability
```

## Entity versus representation

The model separates a durable entity from the representations through which sensors observe it.

```text
Entity: ENT-PAYMENT-CAPTURE
  type: Capability
  canonical_name: Payment Capture

Representations:
  Ruby constant: Payments::Gateway
  renamed constant: PaymentProvider
  OTEL service.name: payments
  deploy unit: payments-api
  architecture node: payment-capture
```

Those representations are related, but they are not automatically the same object.

A business capability can be implemented by a service. A service can be deployed as a deployment unit. A Ruby constant can implement part of that service. An OTEL resource can represent a running instance of it.

Flattening these into a single `same_as` node destroys useful semantics.

## Three identity questions

For any two observed things, the system must distinguish:

1. **Same identity** — two observations refer to the same durable entity.
2. **Representation relation** — one entity represents, implements, deploys, or observes another.
3. **Unresolved similarity** — evidence suggests a relationship, but it is not strong enough to assert one.

Examples:

```text
Payments::Gateway at revision A
PaymentProvider at revision B
    -> may be SAME_IDENTITY if Git rename/history and semantic continuity establish it

Capability: Payment Capture
Service: payments-api
    -> not SAME_IDENTITY
    -> IMPLEMENTED_BY / SERVES_CAPABILITY

OTEL service.name=payments
Deployment: payments-api
    -> REPRESENTS / OBSERVED_AS depending on evidence
```

## Stable entity IDs

World-model entity IDs must be opaque and stable across renames.

Recommended shape:

```text
ENT-01H...
```

or another implementation-independent identifier.

Do not derive canonical IDs from:

- class names;
- file paths;
- repository names;
- Kubernetes names;
- OTEL `service.name`;
- human display labels.

Those values belong in aliases/representations and can change over time.

## Entity classes

Identity is scoped by entity type. The same label can legitimately identify different entities in different layers.

Initial entity classes:

```text
Capability
BusinessFlow
System
Service
Component
CodeSymbol
Repository
DeploymentUnit
RuntimeResource
Database
Queue
ExternalDependency
Team
Owner
Policy
SLO
Change
Incident
Environment
```

The taxonomy should remain extensible. A `CodeSymbol` and a `Service` must never be merged simply because they share a name.

## Identity evidence

Identity resolution is itself evidence-backed.

Possible evidence sources include:

```text
Git rename / move history
semantic continuity
stable external IDs
configuration mappings
OTEL resource attributes
Kubernetes labels
repository ownership metadata
architecture declarations
explicit human assertions
runtime call relationships
```

No single heuristic should silently become authoritative across every entity type.

## Identity links

Instead of destructive merge, sensors and resolvers create versioned identity links.

Useful relations include:

```text
SAME_AS
RENAMED_FROM
MOVED_FROM
REPRESENTS
OBSERVED_AS
IMPLEMENTED_BY
DEPLOYED_AS
OWNED_BY
SERVES_CAPABILITY
```

Each link carries:

```text
source entity
relation
target entity
evidence references
confidence
valid time
recorded time
status
resolver/method
```

An identity link can later be superseded or retracted without deleting historical evidence.

## Same identity requires stronger semantics

`SAME_AS` should be rare and strict.

Use it only when both identifiers are intended to refer to the same durable thing.

Do not use `SAME_AS` for ordinary architecture relationships.

Bad:

```text
Payment Capture SAME_AS payments-api
payments-api SAME_AS Payments::Gateway
```

Better:

```text
Payment Capture SERVES_CAPABILITY <- payments-api
payments-api IMPLEMENTED_BY -> Payments::Gateway
payments-api OBSERVED_AS -> OTEL resource service.name=payments
```

This preserves layer boundaries.

## Temporal identity

Identity resolution must be time/revision-aware.

Example:

```text
revision A..K:
  CodeSymbol Payments::Gateway

revision L:
  renamed to PaymentProvider

Identity link:
  PaymentProvider RENAMED_FROM Payments::Gateway

Both CodeSymbol observations may resolve to the same logical code identity,
while their names remain valid over different revision ranges.
```

The system must be able to answer both:

```text
What is this entity called now?
What was this entity called at revision X?
```

## Split and merge events

Renames are easy compared with splits and merges.

Example split:

```text
legacy Payments service
        |
        +--> PaymentAuthorization
        +--> PaymentCapture
```

This is not a rename and not `SAME_AS`.

The old entity may end its validity interval while two new entities begin. Migration assertions can record lineage:

```text
PaymentAuthorization DERIVED_FROM LegacyPayments
PaymentCapture       DERIVED_FROM LegacyPayments
```

A merge is represented similarly in the opposite direction.

Historical assertions continue to point to the entities that actually existed at that time.

## Resolution states

Identity resolution should expose uncertainty instead of hiding it.

Suggested states:

```text
RESOLVED
PROBABLE
AMBIGUOUS
CONFLICTED
UNRESOLVED
```

A probable mapping can be useful for investigation but must not silently become an authoritative merge.

## Candidate scoring

A resolver may produce candidates using deterministic and probabilistic signals.

Example:

```text
candidate: ENT-SERVICE-PAYMENTS
signals:
  exact stable deployment id       + strong
  Git rename continuity            + strong
  matching OTEL attributes         + medium
  identical display name           + weak
  lexical similarity only          + very weak
```

The exact scoring algorithm is intentionally not frozen yet. The important contract is that the evidence and confidence remain inspectable.

## Conflict example

Suppose architecture declares:

```text
payment-capture -> deployed_as -> payments-v2
```

but runtime telemetry observes:

```text
payment-capture traffic -> payments-legacy
```

The model must not solve this by merging `payments-v2` and `payments-legacy`.

It should preserve both identities and emit a conflict/finding such as:

```text
DECLARED deployment mapping != OBSERVED runtime mapping
```

Identity correctness is a prerequisite for reliable drift detection.

## Identity and assertions

Assertions should reference stable entity IDs. Human-readable names are projections.

```text
Assertion
  subject: ENT-CHECKOUT
  predicate: calls
  object: ENT-PAYMENTS
```

The UI may render current names, historical names, or sensor-native names depending on context, while the assertion identity remains stable.

## Resolution pipeline

```text
raw sensor observation
        |
        v
representation fingerprint
        |
        v
candidate entities
        |
        v
identity evidence
        |
        v
resolver
   /       |       \
resolved probable ambiguous
   |                 |
   v                 v
stable entity     keep separate
   |
   v
versioned identity link
```

## Design invariants

1. Stable entity IDs are independent from mutable names.
2. Equal names are never sufficient proof of equal identity.
3. Different entity layers are not collapsed merely because they describe the same product area.
4. `SAME_AS` is stricter than `REPRESENTS`, `IMPLEMENTED_BY`, or `DEPLOYED_AS`.
5. Identity links have provenance and temporal validity.
6. Resolver uncertainty is represented explicitly.
7. Historical identity mappings are not rewritten when current knowledge changes.
8. Splits and merges create lineage; they are not modeled as simple renames.
9. Human corrections should create/retract evidence-backed mappings rather than mutate history invisibly.
10. Assertions reference stable identities; display names are projections.

## Why this matters to the research roadmap

Identity becomes increasingly important from Lab 13 onward:

- evidence fusion requires different sensors to refer to compatible entities;
- runtime evidence requires mapping code/deployment/runtime representations;
- temporal evidence requires identity continuity across revisions;
- prediction-versus-reality requires predicted and observed consequences to resolve onto the same world-model entities.

Without identity resolution, multi-sensor evidence fusion becomes name matching. That is not a reliable software world model.
