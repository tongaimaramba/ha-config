import adbase as ad

class GuestAccessApp(ad.ADBase):
    """Guest Access App Main Class."""

    def initialize(self):
        """Initialize AppDaemon App."""
        self.adbase = self.get_ad_api()
        self.hass = self.get_plugin_api("HASS")
        self.mqtt = self.get_plugin_api("MQTT")

        self.adbase.log("\n\n************\n*\n* Welcome to Guest Access\n*\n************\n") #Launch message


        self.guest_inputs = self.args.get("guest_args")
        action_entity = self.guest_inputs[0]

        self.hass.listen_event(self.manage_guest,event="run_guest_access") 

    def manage_guest(self,event):

        action = self.hass.get_state(self.guest_inputs[0])
        mac = self.hass.get_state(self.guest_inputs[2])
        guest = self.hass.get_state(self.guest_inputs[1])
        rlp = self.hass.get_state(self.guest_inputs[3]) #->add this input_select to the UI
#        rlp="Guest" #use until UI is updated

#        self.adbase.log("action is: {}".format(action))
        
        # Add Guest Access
        if action == "2.0":

           topic = "monitor/setup/ADD STATIC DEVICE"
           payload = f"{mac} {guest}"
            
           self.mqtt.mqtt_publish(topic,payload)
#           self.adbase.log("added guest with mqtt call using topic:={}= and payload:={}=".format(topic,payload))
           self.update_yaml("add",payload,rlp) 
           return
       
        # Remove Guest Access
        if action == "1.0":
            payload = f"{mac} {guest}"
            
            self.mqtt.call_service("monitor/remove_known_device", device=mac,namespace="mqtt")
            self.adbase.log("removed {} with MAC: {}".format(guest,mac))
            self.update_yaml("remove",payload,rlp)
            return
        else:
            self.adbase.log("No action selected, doing nothing {}".format(action))
            return
        
    def update_yaml(self,action,device,rlp):
        
        if rlp == "Guest":
            pass
#            self.adbase.log(f"Update YAML: this is a {rlp} so will {action} device {device} to/from auto_unloc.yaml")
        elif rlp == "Resident":
            pass
#            self.adbase.log(f"Update YAML: this is a {rlp} so will {action} device {device} to/from auto_unloc.yaml AND home_presence")
        else:
            self.adbase.log(f"Update YAML: {rlp} is not known so doing nothing")
        
        
        
        
        
        