FROZEN_CONDITIONS = [
    {"name":"state_only","components":[],"inference_mode":"explicit"},
    {"name":"history_inference","components":["history"],"inference_mode":"hybrid"},
    {"name":"hybrid_minimal","components":["history","receipts"],"inference_mode":"hybrid"},
    {"name":"explicit_minimal","components":["frontier","obligations","receipts","contract"],"inference_mode":"explicit"},
    {"name":"full_pcc","components":["progress","history","frontier","obligations","receipts","contract"],"inference_mode":"hybrid"},
]
