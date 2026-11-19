# Distributed Transactions

A **distributed transaction** groups work at multiple transactional participants into one logical transaction. Each participant manages its own recoverable state; an **atomic commit protocol** coordinates whether all participants commit or all abort. A participant might be a database, a transactional message broker, or a shard inside one distributed database—not necessarily a separate application service.

## Transaction Boundaries and Partial Failure

[Local atomicity](01%20Transactions.md#Atomicity) protects changes inside one transaction manager's recovery boundary. Running a local transaction in database A and another in database B does not combine those boundaries: committing A and then B leaves A committed if B aborts. Sending both commit requests concurrently does not remove that failure window.

Distribution introduces uncertainty because communication and execution fail independently:

- **Partial failure:** One participant or network path fails while others continue operating.
- **Ambiguous outcome:** A lost reply leaves the caller unable to distinguish a request that never arrived from one that completed before its response was lost. A commit timeout is therefore not proof of abort.
- **Independent recovery:** A process restarts without its volatile state, while another process has already acted on its earlier messages.

Atomic commit replaces independent final decisions with a shared decision that survives the assumed failures. This requires more than request delivery:

- **Transaction identity:** A global transaction identifier associates votes, decisions, retries, and recovery inquiries with the same transaction. Where one resource executes several branches, branch identifiers distinguish them within that global transaction.
- **Participant membership:** The coordinator must know which participants must prepare; a missing participant cannot simply be omitted from the commit condition.
- **Durable state:** Participants preserve their promises and recoverable changes; the decision authority preserves enough information to reconstruct the outcome after restart.
- **Repeatable completion:** Retransmitted protocol messages must not create a new transaction or reverse an existing decision. Recovery completes the original transaction rather than replaying application work as a new operation.

These protocols assume transactional resources and the stated storage/failure model. A resource that loses its supposedly durable state, behaves arbitrarily, or exposes an irreversible nontransactional side effect falls outside the basic crash-recovery guarantee.

## Atomicity, Isolation, and Progress

Atomic commit establishes **one outcome**, not simultaneous physical application at every machine. Participants learn and apply a durable decision at different moments. Read and concurrency rules must prevent those intermediate implementation states from producing observations forbidden by the transaction's guarantees.

- **Atomicity:** Participants do not reach conflicting final outcomes: one must not commit while another aborts.
- **[Isolation](02%20Transaction%20Isolation.md):** Concurrent transactions have controlled visibility and interference. Agreement to commit does not itself establish serializability or a coherent cross-shard snapshot.
- **[Strict serializability and read freshness](03%20Read%20Consistency.md):** Real-time order and the recency of reads impose requirements beyond an all-or-nothing outcome.

[Distributed isolation and timestamps](07%20Distributed%20Transaction%20Isolation.md) compose concurrency control, version visibility, and ordering across participants with atomic commit. Two-phase commit does not select an isolation level.

Two different correctness questions matter during failure:

- **Safety:** No conflicting final outcomes, no reversal of a final decision, and no commit without every required participant's willingness to commit.
- **Liveness:** Participants eventually learn and complete an outcome under the protocol's progress assumptions.

A safe protocol is not necessarily available during a failure. Waiting for missing information preserves safety at the expense of liveness; a timeout is evidence of missing communication, not knowledge of the remote state.

## One-Phase Commit

**One-phase commit (1PC)** asks a resource to finish without a separate durable prepare agreement. With one transactional resource, that resource's local commit machinery decides the outcome; an external coordinator need not gather independent votes.

With several independent resources, a naive single round of commit requests is insufficient: one resource can commit before another rejects the transaction. The missing mechanism is a promise that each resource will remain able to follow a later common decision.

> [!example] Single-participant optimization
> Microsoft's DTC protocol delegates the outcome decision when a transaction manager has exactly one phase-one subordinate. A lost response still leaves an ambiguous outcome; removing a prepare exchange does not remove communication uncertainty. A subordinate transaction manager may itself coordinate further resources, so one subordinate does not necessarily mean one physical database. [DTC single-phase commit](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-dtco/006b07c2-c66d-46b0-91c6-65b42bc5ac98).

## Two-Phase Commit

**Two-phase commit (2PC)** separates willingness to commit from the irreversible decision. A **coordinator**, or transaction manager, gathers votes and records the decision. Each **participant**, or resource manager, controls its local changes and recovery.

### Participant States

- **Active:** Work is provisional. The participant has not promised to commit and is still free to abort locally.
- **Prepared:** The participant has durably voted **YES**. It has preserved the changes and recovery information needed to obey either final decision, and it no longer decides independently to abort.
- **Committed:** The global commit decision has been accepted and local recovery must preserve its effects.
- **Aborted:** The global work is rejected and local recovery discards its effects.

The prepared state is an **in-doubt** state, not a partially successful commit. A YES vote means “I promise I can commit if instructed,” not “I have committed.” Resources needed to honor that promise remain reserved according to the participant's concurrency-control implementation.

### Normal Message Sequence

After application work has executed provisionally:

1. **Prepare request:** The coordinator fixes the required participant set and asks each participant to prepare.
2. **Durable vote:** Each participant checks whether its work is acceptable. Before returning YES, it forces its prepared state and necessary recovery information to durable storage. A participant unable or unwilling to prepare votes NO and aborts its branch.
3. **Durable decision:** The coordinator chooses COMMIT only after receiving YES from every required participant. A NO vote, or a timeout before a commit decision, permits the coordinator to choose ABORT—not a prepared participant to abort independently. In the basic logged protocol, the coordinator force-writes its final decision before notifying participants.
4. **Decision delivery:** The coordinator sends COMMIT or ABORT. Each participant durably completes the corresponding local outcome and releases the resources no longer needed.
5. **Acknowledgment and cleanup:** Participants acknowledge completion. The coordinator retains the information needed to resend the decision until the protocol's acknowledgment and forgetting rules make cleanup safe.

**Force-writing** means the required record survives a crash before the dependent message is sent. A record merely placed in a volatile buffer does not meet this requirement. Physical log layouts and acknowledgment rules vary; optimizations must preserve the same recovery obligations.

### Why a YES-Voter Cannot Timeout-Abort

Suppose A and B both vote YES. The coordinator records COMMIT, sends it to A, and becomes unreachable before B receives it. A commits. From B's perspective, this execution is indistinguishable from one in which the coordinator has not yet decided.

If B aborts on its timeout, the first execution ends with A committed and B aborted. Therefore **a prepared participant cannot use timeout alone to abort**. It must obtain an authoritative decision, recover information that establishes a safe outcome, or remain prepared. Even learning that every reachable participant is prepared is insufficient: an unreachable participant might already have received COMMIT.

This is the blocking property of 2PC: uncertainty can prevent a healthy participant from completing until the decision becomes available. Blocking is how the protocol avoids violating atomicity, not an exception allowing a local rollback. The state-machine and failure arguments are formalized in [Gray and Lamport, *Consensus on Transaction Commit*](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/tr-2003-96.pdf).

### Crash and Partition Recovery

Recovery uses durable protocol state, not the fact that a connection disappeared:

- **Participant fails before durable preparation:** It has made no durable YES promise and recovers by discarding unfinished work. The coordinator cannot commit without its YES vote.
- **Participant fails after preparation:** It restores the prepared branch and seeks the final decision. Restart does not grant permission to abort it independently.
- **Coordinator fails before a durable decision:** In the basic protocol, recovery can choose ABORT. Prepared participants must wait until that outcome is established; they cannot infer the absence of a decision from silence.
- **Coordinator fails after a durable decision:** Recovery retransmits that same decision, including to participants that never received the original notification.
- **Network partition:** Participants that lack decision evidence remain in doubt. Communication with a participant that knows the authoritative outcome can help, but if all reachable participants are only prepared, uncertainty remains.

The coordinator's disk is consequently part of the recovery mechanism. Replacing a failed coordinator with an empty process is not equivalent to recovering its durable identity and decision records.

> [!example] PostgreSQL prepared transactions
> `PREPARE TRANSACTION` detaches the transaction from its session and preserves its state for subsequent `COMMIT PREPARED` or `ROLLBACK PREPARED`. It is intended for an external transaction manager, not as an application-level substitute for ordinary commit. Prepared transactions retain locks and interfere with storage reclamation when left unresolved. PostgreSQL supplies the participant mechanism; it does not discover the correct global outcome by itself. [Prepared transactions](https://www.postgresql.org/docs/current/sql-prepare-transaction.html), [two-phase transaction state](https://www.postgresql.org/docs/current/two-phase.html).

### Two-Phase Commit Versus Two-Phase Locking

The shared phrase “two-phase” names different mechanisms:

- **2PC:** Prepare/vote, then decide/complete; coordinates transaction outcomes across resources.
- **2PL:** Acquire locks during a growing phase, then release them during a shrinking phase without acquiring new locks; controls concurrent access.

They compose rather than substitute for each other. In a locking implementation, prepared transactions retain the locks required by its isolation and recovery rules. An unavailable commit decision then prolongs lock retention, extending a protocol failure into contention for unrelated transactions that need those resources.

## XA and Resource-Manager Coordination

**XA** standardizes the interface between a transaction manager (**TM**) and resource managers (**RMs**). It exposes transaction branches and prepare/completion/recovery operations; it is not a separate isolation level and does not turn arbitrary network services into transactional participants.

- **TM responsibility:** Enlist branches, associate them with a global transaction, collect prepare results, preserve the decision, and drive completion and recovery.
- **RM responsibility:** Execute recoverable branch work, preserve prepared promises, and commit or roll back according to the protocol.
- **Recovery interface:** Enumerate unresolved prepared branches and relevant heuristic outcomes so the TM reconciles them with its own durable records.

> [!example] XA through Jakarta transaction integration
> Jakarta exposes `XAResource` for coordination and recovery. The TM uses `recover` to discover prepared or heuristically completed transactions and must identify the branches it owns. Recreating a client connection is not sufficient: recovery must reconnect protocol state to the durable global decision. [Jakarta transaction recovery](https://jakarta.ee/specifications/transactions/2.0/jakarta-transactions-spec-2.0.html), [Jakarta Connectors transaction contract](https://jakarta.ee/specifications/connectors/2.0/connectors-spec-2.0).

A **heuristic decision** is a resource's unilateral completion without the normal global instruction, for example an administrative action to free an indefinitely prepared branch. Such intervention risks a mixed outcome and requires explicit reporting and reconciliation. It is not the safe timeout-abort rule that ordinary 2PC deliberately forbids.

## Presumed Abort and Presumed Commit

Logging and acknowledgment costs depend partly on which outcomes must remain explicitly recorded. **Presumed abort** and **presumed commit** encode a defined interpretation of missing transaction information into the recovery protocol:

- **Presumed abort:** The recovery authority interprets absence of the relevant transaction record as ABORT. The protocol retains commit evidence until safe completion, while reducing logging and acknowledgment work for aborts.
- **Presumed commit:** The recovery authority interprets absence according to a commit presumption. Establishing that default safely requires additional durable information during earlier processing; otherwise a never-prepared transaction could be mistaken for a committed one. It shifts costs toward earlier stages to reduce completion costs for commits.

These are protocol-wide rules for durable records and safe forgetting, not guesses made by a disconnected participant. A prepared participant still cannot treat an unanswered inquiry as proof that the authority has no record. They optimize 2PC without eliminating its blocking condition. [Mohan, Lindsay, and Obermarck, *Transaction Management in the R\* Distributed Database Management System*](https://pages.cs.wisc.edu/~remzi/Classes/739/Papers/p378-mohan-2pc.pdf).

## Three-Phase Commit and Timing Assumptions

**Three-phase commit (3PC)** introduces an intermediate **precommit** state between voting and final commit. The extra state separates uncertainty about whether everyone is ready from the stage at which commitment is imminent, giving a termination protocol more information after coordinator failure.

The simplified successful sequence is:

1. **Can commit:** Collect willingness to commit.
2. **Precommit:** Tell participants that all agreed and collect acknowledgments of the intermediate state.
3. **Commit:** Issue the final decision.

Its nonblocking claim depends on the failure and timing model: synchronous or bounded-delay communication, appropriate failure detection, and no network partition separating groups that independently continue the termination protocol. Under those assumptions, surviving processes use their states and timeouts to finish without waiting for a failed coordinator to recover.

Under arbitrary delay or partitions, timeout-driven termination cannot safely assume that unreachable processes share the same knowledge. Adding a phase does not provide nonblocking atomic commit for an unrestricted asynchronous network. The extra communication and restrictive assumptions are part of the trade-off, not incidental implementation details. [Skeen, *Nonblocking Commit Protocols*](https://www.cs.cornell.edu/courses/cs614/2004sp/papers/Ske81.pdf).

## Consensus, Replication, and Atomic Commit

Consensus makes a group agree on a value or ordered log; atomic commit additionally constrains a transaction's outcome by the willingness of **every required participant**. A majority of transaction participants voting YES cannot authorize commit over another participant's NO.

- **Replicated participant:** Consensus preserves one shard's state across replicas. Its replica quorum is not a vote to omit other shards from a transaction.
- **Replicated coordinator:** Consensus preserves the coordinator's decision and allows another leader to continue from it. This removes dependence on one coordinator process, provided the decision group can make progress.
- **Cross-participant commit:** A protocol still establishes that all distinct resources are prepared and that they follow one outcome. Replicating each resource separately does not supply that relationship.

Raft, for example, manages a replicated log; it is not by itself a protocol for atomically committing work across independent logs. [Raft paper](https://raft.github.io/raft.pdf).

### Paxos Commit

**Paxos Commit** distributes decision knowledge through consensus instances for individual participants' prepared/aborted outcomes. The global transaction commits only if every participant's instance chooses Prepared; an Aborted outcome prevents commit. A replica majority decides each instance—it does not replace the requirement that all transaction participants be ready.

Paxos Commit uses **2F + 1 coordinator/acceptor replicas**, where **F** is the number of those replica failures tolerated. A quorum of **F + 1** supports consensus progress under the required stable-leader and communication assumptions. Replicating these outcomes avoids waiting for one particular coordinator's recovery, at the cost of additional messages and replicated durable state.

That fault tolerance does not make unavailable participants execute their work or promise to commit. If a participant fails before Prepared is chosen for its instance, a higher-ballot leader can propose Aborted subject to Paxos's rules for preserving previously accepted values; the crash itself does not establish an Aborted outcome. A chosen outcome must be preserved. Quorum loss or sustained communication failure still prevents progress. Safety does not require bounded message delays, while liveness requires sufficient reachable processes and sufficiently stable communication. [Paxos Commit specification and comparison with 2PC](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/tr-2003-96.pdf).

> [!example] Replication composed with transaction commit
> The Spanner design uses Paxos replication within groups and 2PC across participating groups, with transaction-manager state replicated through Paxos. Replication and cross-group commitment solve different parts of the transaction. [Spanner OSDI paper](https://web.mit.edu/6.033/2014/wwwdocs/papers/spanner-osdi2012.pdf).
>
> CockroachDB uses its Parallel Commits atomic commit protocol with transaction records and provisional write intents; the intents are replicated through Raft. Its asynchronous intent cleanup follows a logically committed outcome rather than defining a new independent decision for each write. [CockroachDB transaction layer](https://www.cockroachlabs.com/docs/stable/architecture/transaction-layer).

## Operational Costs and Transaction Choice

Distributed atomicity moves failure handling into a protocol, but does not remove its cost:

- **Commit latency:** Network exchanges and durable writes lie on the commit path. Distant participants and slow storage increase coordination time.
- **Contention:** Locks, provisional versions, and recovery metadata remain live while a transaction is unresolved. A slow decision extends their lifetime.
- **Availability coupling:** Every required participant must be ready to permit commit; decision availability also depends on coordinator recovery or the relevant consensus quorum.
- **Recovery operations:** Durable identities, participant discovery, decision retention, retries, and prepared-transaction monitoring must survive process replacement and operational intervention.

Prefer a local transaction when the invariant fits one transactional boundary. Distributed atomic commit is appropriate when an operation genuinely requires one all-or-nothing outcome across resources that support participation, and the system accepts its coordination and recovery obligations.

[Sagas and transactional-outbox workflows](../../Backend%20Engineering/Concurrency/04%20Distributed%20Concurrency.md) instead compose local commits with messages, retries, and, where appropriate, compensating actions. They expose intermediate committed states and do not provide the same global rollback boundary. An external action that cannot prepare or roll back must be handled through such application-level semantics rather than assumed to participate in atomic commit.
