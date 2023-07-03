nni = [0,1,2,3]
uni = [4,5,6,7]
agg_groups = [0,3]
west_or_east = "west"
nni_kbps = 10000000000
uni_kbps = 1000000000
vlan = 130
total_nni_kbps = len(nni) * nni_kbps
total_uni_kbps = len(uni) * uni_kbps
nni_range = range(0,21)
uni_range = range(0,21)
nni_inactive = set(nni).intersection(nni_range)
uni_inactive = set(uni).intersection(uni_range)
nni_comma_list = ",".join([str(port) for port in nni])
uni_comma_list = ",".join([str(port) for port in uni])
hostname = 'wwww.yourmom.com'
#- if agg groups are in use for NNI ports, set mode to advanced
for port in agg_groups:
    print(f"traffic-profiling set port {port} mode advanced")
print("!")
print("traffic-profiling enable")
print("!")
#- disable all ports that are not in use to help prevent loops
#  - set all NNI ports to 9216, set all UNI ports to 9200.
# Any port can be used as an NNI or UNI (10G or 1G)
#  Be careful not to disable a port being used for comm
# The below text disables all ports
for port in nni_inactive:
    print(f"port disable port {port}")
    print(f"port set port {port} max-frame-size 9216")
for port in uni_inactive:
    print(f"port disable port {port}")
    print(f"port set port {port} max-frame-size 9200")
print("!")
#only use shaper if there’s a subrate circuit between the switches (like a MW radio or telco circuit) – in kbps
subrate_circuit = False
if subrate_circuit:
    port=0
    sr=0
    print(f"traffic-services queuing egress-port set port {port} shaper-rate {sr}")
    print("!")
print("flow cpu-rate-limit enable")
for port in nni:
    print(f"flow cpu-rate-limit set port {port} eoam 10") # - add this to all NNI ports     
print("!")
# -set cir to .1% of total NNI bandwidth (do this for each NNI port – in this example, port 21 and management vlan 130 was used)
print(f"traffic-profiling standard-profile create port {port} profile {port} name v{vlan}_{port} cir {total_nni_kbps * 0.001} eir 0 cbs 96 ebs 0 vlan {vlan}")    
print("!")
for port in nni:
    print(f"traffic-profiling enable port {port}") # (for all NNI ports)
print("!")
# - use NNI filter for 10G ports and UNI filter for 1G ports

print("broadcast-containment create filter NNI kbps 200000 containment-classification bcast,unknown-l2-mcast,unknown-ip-mcast,unknown-ucast")    
print("broadcast-containment create filter UNI kbps 100000 containment-classification bcast,unknown-l2-mcast,unknown-ip-mcast,unknown-ucast")
print("!")
print(f"broadcast-containment add filter NNI port {nni_comma_list}")
print(f"broadcast-containment add filter UNI port {uni_comma_list}")
print("!")
for port in uni:
    print(f"lldp  set port {port} mode disable") # set this on all UNI ports
    
for port in nni:
    print(f"lldp  set port {port} notification on") # set this on all NNI ports
print("!")
print("eoam enable")
for port in nni:
    print(f"eoam enable port {port}") # set the below eoam settings on all NNI ports
    print(f"eoam set port {port} errd-frame-ev-notify on")
    print(f"eoam set port {port} errd-frame-secs-summary on")
    print(f"eoam set port {port} dying-gasp on")
    print(f"eoam set port {port} critical-event on")
print("!")
print("telnet server disable")# log off of your telnet session and login using ssh before issuing the command
print("!")
print("user create user trans-eng access-level super echoless-password") # see https://passwordvault
print("user delete user su")
print("user delete user gss")
print("user delete user user")
print("user delete user admin")
print("!")
location = "TEST"
print(f"snmp set location {location}") # use the Location Mnemonic code found in the location database

if west_or_east == "west":
    ip_1 = "10.120.99.72"
    ip_2 = "10.92.99.76"
if west_or_east == "east":
    ip_1 = "10.92.99.72"
    ip_2 = "10.120.99.76"

print(f"snmp create target telenium_Server-1 addr {ip_1}/32 param-name v2c_public transport-domain snmp-udp") #–use 10.120.99.72 for the West and 10.92.99.72 for the East
print(f"snmp create target telenium_Server-2 addr {ip_2}/32 param-name v2c_public transport-domain snmp-udp") #–use 10.92.99.76 for the West and 10.120.99.76 for the East
print("!")
print(f"file cp /flash0/config/startup-config /flash0/config/{hostname}") # -use the hostname of the switch for hostname
print(f"config set default-save-filename {hostname} default-load-filename {hostname}")
print("!")
#(see IP Addressing.xlsx for next available loopback address)
next_avail_loopback = "10.241.x.x"
print(f"interface create loopback lb0 ip {next_avail_loopback}") 
print("!")
print(f"vlan create vlan xx1,xx2") # create a vlan for every NNI port (for every point to point between switches)
# (see IP Addressing.xlsx for next available vlans)
print(f"vlan add vlan xx1 port 21") # (Add the vlan for each point to point to the appropriate NNI port)
print(f"vlan add vlan xx2 port 22") # (Add th e vlan for each point to point to the appropriate NNI port)
print(f"vlan remove vlan 1 port {nni_comma_list}") #– remove vlan 1 from all of the NNI ports
#(see IP Addressing.xlsx for next available point to point address
# must be in the same /30 network as the remote switch interface)
print(f"interface create ip-interface ipif-21 ip 10.241.x.x/30 ip-forwarding on mtu 9190 vlan xx1") 
#(see IP Addressing.xlsx for next available point to point address
# must be in the same /30 network as the remote switch interface)
print(f"interface create ip-interface ipif-22 ip 10.241.x.x/30 ip-forwarding on mtu 9190 vlan xx2")
print("!")
print(f"rstp disable port {nni_comma_list}") # disable rstp on the NNI ports
print("!")
print("config save")