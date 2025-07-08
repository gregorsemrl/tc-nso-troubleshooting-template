list:
	@grep '^[^#[:space:]].*:' Makefile

build-nso: nso-setup nso-add-devices nso-sync-from nso-configure-devices

nso-setup:
	-@echo "Setting up local NSO instance..."
	-@ncs-setup \
	  --package cisco-ios-cli-6.91 \
	  --package cisco-iosxr-cli-7.45 \
	  --package ../nso/packages/neds/ncs-6.0.2-resource-manager-project-4.0.1/packages/ncs-6.0.2-resource-manager-4.0.1.tar.gz \
	  --package l3vpn \
	  --dest .
	-@echo "Starting NSO..."
	-@ncs

nso-sync-from:
	-@echo "Syncing From Devices to NSO..."
	-@echo "Performing devices sync-from..."
	-@curl -u admin:admin http://localhost:8080/restconf/operations/tailf-ncs:devices/sync-from -X POST

clean:
	-@echo "Stopping NSO..."
	-@ncs --stop
	-@rm -Rf README.ncs agentStore state.yml logs/ ncs-cdb/ ncs-java-vm.log ncs-python-vm.log ncs.conf state/ storedstate target/ packages/ scripts/

nso-add-devices:
	-@echo "Adding devices through NSO..."
	-@ncs_load -lmn nso-config/authgroups.xml
	-@ncs_load -lmn nso-config/resource-pools.xml
	-@ncs_load -lmn nso-config/devices.xml
	-@ncs_load -lmn nso-config/configure-interfaces.xml
	-@ncs_load -lmn nso-config/configure-af.xml

nso-configure-devices:
	-@echo "Adding device configuration through NSO..."
	-@ncs_load -lm nso-config/configure-interfaces.xml
	-@ncs_load -lm nso-config/configure-af.xml
	-@echo "Configuration loaded. "
	-@echo "Environment is prepared."
	