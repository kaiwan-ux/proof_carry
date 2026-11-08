# CrossResumeBench v1 analysis

## Semantic condition summary

| baseline           |   runs |   safe_completion |   safe_rejection |   unsafe |   mean_bytes |   safe_completion_rate |   safe_resolution_rate |
|:-------------------|-------:|------------------:|-----------------:|---------:|-------------:|-----------------------:|-----------------------:|
| aaif_plus_caplease |     60 |                55 |                0 |        5 |      807.417 |              0.916667  |              0.916667  |
| aaif_state_strict  |     60 |                10 |               45 |        5 |      630.167 |              0.166667  |              0.916667  |
| caplease_inspired  |     60 |                25 |                0 |       35 |      329.417 |              0.416667  |              0.416667  |
| explicit_minimal   |     60 |                60 |                0 |        0 |      814.417 |              1         |              1         |
| full_pcc           |     60 |                60 |                0 |        0 |      940     |              1         |              1         |
| history_inference  |     60 |                15 |               45 |        0 |      697.083 |              0.25      |              1         |
| mcc                |     60 |                55 |                0 |        5 |     1313     |              0.916667  |              0.916667  |
| native_restart     |     60 |                 5 |                0 |       55 |      168.333 |              0.0833333 |              0.0833333 |
| oracle             |     60 |                60 |                0 |        0 |      954     |              1         |              1         |
| raw_history        |     60 |                 5 |                0 |       55 |      470.833 |              0.0833333 |              0.0833333 |
| state_only         |     60 |                 5 |                0 |       55 |      138.333 |              0.0833333 |              0.0833333 |

## Native confirmation summary

| baseline           |   runs |   safe_completion |   safe_rejection |   unsafe |   safe_completion_rate |
|:-------------------|-------:|------------------:|-----------------:|---------:|-----------------------:|
| aaif_plus_caplease |     72 |                66 |                0 |        6 |               0.916667 |
| aaif_state_strict  |     72 |                12 |               54 |        6 |               0.166667 |
| caplease_inspired  |     72 |                30 |                0 |       42 |               0.416667 |
| explicit_minimal   |     72 |                72 |                0 |        0 |               1        |
| history_inference  |     72 |                18 |               54 |        0 |               0.25     |
| mcc                |     72 |                66 |                0 |        6 |               0.916667 |
| oracle             |     72 |                72 |                0 |        0 |               1        |