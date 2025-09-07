include .env
export

.PHONY: validate api e2e smoke alerts

validate: smoke api e2e
	@echo "✅ ALL CHECKS PASSED"

smoke: scripts/check_dynamo_readings.sh scripts/check_s3_ndvi.sh
	@bash scripts/check_dynamo_readings.sh
	@bash scripts/check_s3_ndvi.sh

api:
	@bash scripts/get_summary.sh
	@bash scripts/get_readings_since.sh
	@bash scripts/post_ops_event.sh
	@bash scripts/get_ops_list.sh
	@npx newman run postman/gsg-farm-api.postman_collection.json -e postman/gsg-env.postman_environment.json --bail

e2e:
	cd e2e && npm ci && npx playwright install --with-deps && npm test

alerts:
	@bash scripts/trigger_ndvi_drop_event.sh

