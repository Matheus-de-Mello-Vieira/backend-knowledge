# Relational Schema Normalization

**Normalization** organizes a relational schema around its data dependencies to reduce redundant facts and the inconsistencies that redundancy permits. It decomposes relations when their attributes combine facts with different determinants, while preserving the information needed to reconstruct valid data.

Normalization concerns logical design, not physical storage layout or a guarantee of faster queries. The definitions below use the classical relational model, without SQL `NULL` semantics.

## Functional Dependencies and Keys

A **functional dependency** `X → Y` means that, in every valid instance of a relation, any two tuples that agree on all attributes in `X` also agree on all attributes in `Y`. Here, `X` and `Y` are sets of attributes; `X` is the **determinant**. The dependency expresses a rule of the modeled data, not just a pattern observed in the current rows.

For example, `course_id → course_title` states that a course identifier determines one course title. Several courses may share a title; the reverse dependency does not follow.

- **Superkey:** An attribute set that functionally determines every attribute of the relation.
- **[Candidate key](04%20Relational%20Model.md#Keys%20and%20Referential%20Integrity):** A minimal superkey: removing any attribute makes it cease to be a superkey. Any candidate key is eligible to be selected as the primary key; normalization considers all candidate keys, not only the selected one.
- **Prime attribute:** An attribute belonging to at least one candidate key. A **non-prime attribute** belongs to none.
- **Trivial dependency:** A dependency whose right-hand attributes are already contained in its left-hand set, such as `{student_id, course_id} → course_id`. It adds no constraint beyond agreement on the determinant itself.
- **Extraneous determinant attribute:** An attribute in the left-hand side of a dependency that can be removed without changing the dependencies implied by the full set. For `X → A`, an attribute `b ∈ X` is extraneous when replacing that dependency with `(X − {b}) → A` leaves the set equivalent.
    - **Candidate-key connection:** Let `R` be all attributes of the relation. An attribute of a superkey `K` is extraneous in `K → R` exactly when removing it leaves a superkey. Thus `K` is a candidate key exactly when `K → R` has no extraneous determinant attribute.
- **Minimal cover:** A set of dependencies equivalent to the original set—both imply the same dependencies—in which each right-hand side is a single attribute, no dependency can be removed without changing the implied dependencies, and no determinant attribute is extraneous.
    - **Single-attribute right-hand sides:** `X → {A, B}` is equivalent to `X → A` and `X → B`. Splitting it preserves the constraints while letting each determined attribute be tested separately for redundancy.

Adding a surrogate identifier does not remove other dependencies. A new primary key identifies rows, but does not make repeated course titles cease to depend on `course_id`.

## Redundancy and Modification Anomalies

Consider `Enrollment(student_id, course_id, course_title, grade)`. Assume a student has at most one enrollment per course, each course has one title, and an enrollment has one grade:

- `{student_id, course_id} → grade`
- `course_id → course_title`

The candidate key is `{student_id, course_id}`. Because the course title depends only on the course, combining it with each enrollment repeats the same course fact for every enrolled student.

This repetition creates three related design problems:

- **Update anomaly:** Renaming a course requires changing every enrollment row for that course. If only some copies change, the stored titles disagree.
- **Insertion anomaly:** Recording a course before any student enrolls requires an enrollment-shaped row even though no enrollment exists.
- **Deletion anomaly:** Deleting a course's last enrollment also removes the only stored record of its title.

Separating `Course(course_id, course_title)` from `Enrollment(student_id, course_id, grade)` records each course title independently of enrollment. The shared `course_id` relates enrollments to courses without repeating the title. These are schema-design anomalies, not concurrent-transaction isolation anomalies.

## Decomposition Correctness

Splitting a relation is useful only if the resulting schemas preserve the intended data and constraints. Two properties answer different questions:

- **Lossless join:** For every valid original relation, projecting its tuples onto the decomposed schemas and joining those projections reconstructs exactly the original relation. No tuples are lost and no spurious combinations are introduced.
- **Dependency preservation:** Enforcing the functional dependencies within the individual decomposed relations is sufficient to enforce the original functional dependencies. A decomposition without this property requires additional cross-relation checks for dependencies that are no longer locally enforceable.

For a binary decomposition into schemas `R1` and `R2`, the decomposition is lossless with respect to the functional dependencies exactly when the shared attributes functionally determine all attributes of at least one component. Here, `R1` and `R2` together contain all attributes of the original schema.

In the course decomposition, the shared `course_id` determines the entire `Course` tuple, so joining the projections does not invent enrollment combinations. Each original dependency also remains checkable in one relation. Losslessness concerns reconstruction; dependency preservation concerns constraint enforcement. Neither term is a synonym for the other.

## Normal Forms

Normal forms state progressively stronger restrictions on the relation's structure and dependencies. Assess them from the intended rules and all candidate keys, not from a small sample of rows.

For the dependency conditions below:

- **`K`:** Any candidate key.
- **`X`:** A set of attributes.
- **`A`:** One attribute.
- **`X → A`:** `X` functionally determines `A`.
- **`X ⊂ K`:** `X` is a proper subset of `K`.
- **Prime attribute:** An attribute belonging to at least one candidate key.

### First Normal Form

**First normal form (1NF)** represents each attribute occurrence as one value from its domain rather than a repeating group of values treated as multiple occurrences of the attribute. An enrollment relation represents separate enrollments as separate tuples rather than embedding a repeating enrollment group in one student tuple.

Unlike the later forms, 1NF is not a restriction of the form `X → A`; it establishes the structure on which functional-dependency rules operate. The description “atomic values” is relative to the chosen domains and relational model; it does not mean that every domain value must be a universally indivisible scalar. Whether a structured value is appropriate depends on what the model treats as one value and which facts must be represented and constrained independently.

> [!example] Modeling values in 1NF
> - **Repeating group:** If `Student(student_id, enrollments)` treats `enrollments` as a collection of independently recorded `(course_id, grade)` facts, represent each enrollment as a separate `Enrollment(student_id, course_id, grade)` tuple instead.
> - **Single domain value:** An address treated as one value need not be split into every constituent part. If the model must represent and constrain `city` independently, make `city` a separate attribute.

### Second Normal Form

**Second normal form (2NF)** requires 1NF and rules out `X → A` when `X ⊂ K` for a candidate key `K` and `A` is non-prime. Such a **partial dependency** means that part of a composite key already determines an attribute that belongs to no candidate key.

The combined enrollment relation violates 2NF: `course_id → course_title`, `course_id ⊂ {student_id, course_id}`, and `course_title` is non-prime. Separating course facts removes that partial dependency.

### Third Normal Form

**Third normal form (3NF)** requires 1NF and, for every nontrivial dependency `X → A` where `A ∉ X`, at least one of these conditions:

- `X` is a superkey.
- `A` is a prime attribute.

> [!note] 3NF implies 2NF
> A 2NF violation has `X → A` with `X ⊂ K` for a candidate key `K` and `A` non-prime. Because `K` is minimal, `X` is not a superkey; because `A` is non-prime, neither condition in the 3NF rule holds. Thus every relation in 3NF is also in 2NF.

Here, `A` is a single attribute; a dependency with several right-hand attributes is checked one attribute at a time. The prime-attribute exception matters when candidate keys overlap, so “every non-key attribute depends only on the primary key” is not a complete definition.

> [!example] Prime-attribute exception
> Suppose `Assignment(student_id, course_id, instructor_id)` has `{student_id, course_id} → instructor_id` and `instructor_id → course_id`: a student has one instructor per course, and each instructor teaches one course. Its candidate keys are `{student_id, course_id}` and `{student_id, instructor_id}`. Although `instructor_id` is not a superkey, `course_id` is prime because it belongs to a candidate key. Thus `instructor_id → course_id` satisfies 3NF's prime-attribute exception but violates BCNF.

For example, assume `Employee(employee_id, department_id, department_name)` has only `employee_id` as a candidate key, with `employee_id → department_id` and `department_id → department_name`. The latter dependency violates 3NF: `department_id` is not a superkey, and `department_name` is non-prime. Separating department facts removes the repeated department name.

#### Lossless, Dependency-Preserving 3NF Decomposition

For any relation schema `R` and finite set of functional dependencies `F`, there is a decomposition into 3NF relations that is both lossless and dependency preserving. The claim is about the existence of a suitable decomposition, not every possible decomposition.

> [!note]- Proof via 3NF synthesis
> Construct one as follows:
>
> 1. Find a minimal cover `G` of `F`.
> 2. For each `X → A` in `G`, create a schema `X ∪ {A}`. If none of these schemas contains a candidate key `K` of `R`, add a schema consisting of `K`.
>
> The construction has the required properties:
>
> - **Dependency preservation:** Each dependency `X → A` in `G` is enforceable in its own `X ∪ {A}` relation. Since `G` and `F` imply the same dependencies, enforcing the component dependencies preserves `F`.
> - **3NF components:** In `X ∪ {A}`, `X` is a candidate key: if a proper subset of `X` determined `A`, an attribute of `X` would be extraneous in the minimal cover. For any nontrivial dependency `Y → B` on this component, either `B ∈ X` and is prime, or `B = A`. In the latter case, `Y ⊆ X`; minimality rules out `Y ⊂ X`, so `Y = X` is a superkey. A key-only component `K` has no nontrivial dependency among its attributes with a proper-subset determinant, because that would contradict the minimality of `K` for `R`.
> - **Lossless join:** Let `r` satisfy `F`, and let `t` be a tuple in the join of its component projections. A component containing `K` supplies a tuple `u ∈ r` agreeing with `t` on `K`. Follow the dependency steps that compute the closure of `K` under `G`. Whenever `t` and `u` agree on `X` for `X → A`, the `X ∪ {A}` projection supplies a tuple of `r` agreeing with `t` on both `X` and `A`; the dependency forces `u[A] = t[A]`. Since `K` determines every attribute of `R`, this establishes `t = u`. The join therefore adds no spurious tuple, while every tuple of `r` remains in the join.

### Boyce–Codd Normal Form

**Boyce–Codd normal form (BCNF)** requires 1NF and, for every nontrivial `X → A` where `A ∉ X`, requires `X` to be a superkey. It removes 3NF's prime-attribute exception: even a dependency determining a prime attribute violates BCNF when its determinant is not a superkey. Every BCNF relation is therefore in 3NF, but not every 3NF relation is in BCNF.

A lossless decomposition into BCNF relations also exists, but preserving every functional dependency within the individual relations is not always possible. BCNF therefore imposes a stronger restriction on dependency-based redundancy, while 3NF provides a way to retain local enforcement of every functional dependency. These forms do not address every possible source of redundancy; other kinds of dependencies motivate higher normal forms.

## Normalization and Query Trade-offs

Separating facts reduces the number of places that must change together, but queries combining those facts require joins. Whether a normalized design improves execution time depends on the workload and physical execution choices, not on the normal-form label alone.

**Denormalization** deliberately duplicates or combines facts to serve an access pattern. It trades some reconstruction work for responsibility to keep redundant representations consistent. Make that trade-off explicit: identify which fact is authoritative, which values are derived copies, and how updates keep them aligned rather than treating duplication as free read performance.
