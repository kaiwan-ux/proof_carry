from __future__ import annotations
ALLOWED_ACTIONS={
"inventory_callback_fulfillment":["resolve_callback_then_fulfill","replay_hold_then_fulfill","reject"],
"multi_effect_order_dispatch":["dispatch_without_replaying","replay_effects_then_dispatch","reject"],
"quorum_parallel_2of3":["cancel_remainder_then_join","run_third_worker_then_join","reject"],
"race_first_success_cancel":["cancel_losers_then_finish","run_all_branches","reject"],
"nested_loop_branch_retry_v2":["retry_fast_then_review_3","switch_to_slow","restart_loop","reject"],
"human_edit_publish":["resolve_approval_then_publish_edited","publish_without_approval","reject"],
"saga_dual_compensation":["release_stock_then_refund","replay_forward_effects","reject"],
"lease_renewal_handoff":["renew_then_enter_critical","reacquire_then_enter","reject"],
"mixed_idempotency_effects":["verify_without_replaying_charge","replay_all_effects","reject"],
"map_reduce_threshold":["cancel_remainder_then_reduce","run_fourth_shard_then_reduce","reject"],
}
EXPECTED={k:v[0] for k,v in ALLOWED_ACTIONS.items()}
