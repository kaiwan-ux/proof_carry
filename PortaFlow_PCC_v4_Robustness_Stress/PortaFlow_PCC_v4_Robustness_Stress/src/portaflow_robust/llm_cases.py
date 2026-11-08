from __future__ import annotations
from .benchmark import BASE_WORKFLOWS,split_case
ALLOWED_ACTIONS={
'escrow_callback_release':['callback_then_release','replay_hold_then_release','reject'],
'two_phase_reservation_commit':['verify_without_replay','replay_commit_then_verify','reject'],
'quorum_write_cancel':['cancel_then_quorum','run_third_then_quorum','reject'],
'race_cleanup_notify':['cleanup_then_notify','run_losers_then_notify','reject'],
'nested_review_retry_publish':['retry_then_review3_then_approve','restart_review','reject'],
'dual_approval_release':['resolve_two_approvals_then_release','release_now','reject'],
'saga_shipping_refund':['release_stock_then_refund','replay_forward_effects','reject'],
'batch_reduce_invoice':['cancel_then_reduce_without_reinvoice','run_fourth_then_reinvoice','reject'],
}
EXPECTED={k:v[0] for k,v in ALLOWED_ACTIONS.items()}
def actions_for(case):return ALLOWED_ACTIONS[split_case(case)[0]]
def expected_for(case):return EXPECTED[split_case(case)[0]]
