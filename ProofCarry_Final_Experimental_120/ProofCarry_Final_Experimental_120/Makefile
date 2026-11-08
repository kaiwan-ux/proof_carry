.PHONY: test audit reproduce smoke native

test:
	python -m unittest discover -s tests -v

audit:
	python scripts/audit_cases.py --root .
	python scripts/verify_legacy.py

reproduce:
	python reproduce_all.py --native-status

smoke:
	python reproduce_all.py --performance-reps 2 --performance-warmups 1 --performance-max-cases 4 --native-status

native:
	python native/run_native_validation.py --root . --out results/native/native_validation.csv
