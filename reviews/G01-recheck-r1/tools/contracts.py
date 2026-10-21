"""Frozen preparation contracts; constants only, NOT a gameplay implementation."""
CAMPAIGN_IDS=tuple(f'L{i:02}' for i in range(1,21))
LEGAL_ORDER=('UNKNOWN_OR_REMOVED','MANIFEST_MISMATCH','ARROW_COLLISION','WALL_COLLISION','CLOSED_GATE')
COMMIT_ORDER=('validate complete sweep in pre-state','remove arrow','XOR each listed gate once',
              'advance manifest cursor if nonempty','evaluate win then deadlock','persist logical state','animate')
RULE_FACT_FIELDS=('kind','level_id','arrow_id','from_mask','to_mask','gate_changes','manifest_cursor','won','deadlocked')
FORBIDDEN_RULE_FIELDS=('eventId','sessionId','firstClear','stampCount','completed')
MAX_REVISION=9007199254740991
TUTORIAL_IDS=('base','relay','manifest','combined')
SESSION_CONTRACT=dict(
    rule_return='Accepted(nextAttempt, ruleFacts) or Reject; never publishes events',
    rule_fact_fields=list(RULE_FACT_FIELDS),forbidden_rule_fields=list(FORBIDDEN_RULE_FIELDS),
    publisher='SessionBus.publish, called only by SessionCoordinator',
    event_id='boot-local sessionId + colon + strictly increasing positive sequence; allocated only by SessionCoordinator',
    completion_owner='SessionCoordinator; firstClear computed from pre-action Progress.completed; stampCount from post-union completed set',
    save_owner='SessionCoordinator emits one SaveRequested per accepted revision; SaveCoordinator only persists and returns result',
    save_ack='SessionCoordinator publishes deduplicated SaveSucceeded/SaveFailed; acknowledgement never increments revision or triggers save',
    undo_policy='Undo retains completed; completing again emits firstClear=false with unchanged stampCount; no REDO command exists',
    interrupt_policy='Animation interruption never resubmits rule command or already queued snapshot; visibility flush deduplicates revision',
    rejection_policy='Rejected action does not change revision/completed or request save',
    tasks=dict(rule_facts='T04',session_state_machine_bus='T06',save_transport='T07',campaign_progress_integration='T08'))
