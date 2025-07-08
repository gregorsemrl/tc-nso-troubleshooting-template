# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service
import resource_manager.id_allocator as id_allocator

class L3VPNNanoService(ncs.application.NanoService):
    
    @ncs.application.NanoService.create
    def cb_nano_create(self, tctx, root, service, plan, component, state, proplist, component_proplist):
        self.log.debug("NanoService create ", state)

        vlan_id = id_allocator.id_read(tctx.username, root, 'l3vpn-vlan', service.vpn_name)
        self.log.info(f'VLAN ID read: {vlan_id}')

        vars = ncs.template.Variables()
        vars.add("vlan-id", vlan_id)
        template = ncs.template.Template(service)
        template.apply('l3vpn-template', vars)

class VLANAllocationNanoService(ncs.application.NanoService):
    
    @ncs.application.NanoService.create
    def cb_nano_create(self, tctx, root, service, plan, component, state, proplist, component_proplist):
        self.log.debug("NanoService create ", state)

        self.log.info(f'VLAN ID requested for {service.vpn_name}, XPATH {service._path}')
        service_path = f"/l3vpn:l3vpn[l3vpn:vpn-name='{service.vpn_name}']"

        id_allocator.id_request(service, service_path, tctx.username, 'l3vpn-vlan', service.vpn_name, False)

        vlan_id = id_allocator.id_read(tctx.username, root, 'l3vpn-vlan', service.vpn_name)

        if not vlan_id:
            self.log.info(f'VLAN ID not allocated yet for {service.vpn_name}')
            plan.component[component].state[state].status='not-reached'
            return
        
        self.log.info(f'VLAN ID allocated for {service.vpn_name} with value {vlan_id}')
        return

# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')
        self.register_nano_service('l3vpn-servicepoint', 'l3vpn:l3vpn', 'l3vpn:l3vpn-configured', L3VPNNanoService)
        self.register_nano_service('l3vpn-servicepoint', 'l3vpn:l3vpn', 'l3vpn:vlan-allocated', VLANAllocationNanoService)

    def teardown(self):
        self.log.info('Main FINISHED')
