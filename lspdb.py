import napalm
import re
import yaml
import os
import getpass
from napalm import get_network_driver
from tabulate import tabulate


def duplicate_sid_check(router_dict):
  # Looking fro duplicate Node SIDs
  seq=[]
  for router, router_info in router_dict.items():
    seq.append(router_info['nsid'])
    
  not_duplicates=[] 
  duplicates=[]  
  for x in seq:
    if not x in not_duplicates:
      not_duplicates.append(x)
    else:
      duplicates.append(x)
  
  if duplicates:
    print("Duplicate node SID.....whoops")
    for x in duplicates:
      print("Duplicate SID ",x)
      print("Routers:")
      for router, router_info in router_dict.items():
        if router_info['nsid'] == x:
          print(router)
           
           
  else:
    print("No duplicate node SIDs\n\n")
    

def duplicate_srgb(router_dict,start,end):
  # Checking we have consistent SRGB
  none_to_report=0
  for router, router_info in router_dict.items():
    if router_info['srgb_start'] != start:
      print("\n"+router + " has incorrect start of SRGB range\n")
      print (router_info['srgb_start'])
      none_to_report+=1
    if router_info['srgb_end'] != end:
      print("\n"+router + " has incorrect end of SRGB range\n")
      print (router_info['srgb_end'])
      none_to_report+=1
  if none_to_report==0:
    print("SRGB is consistent......it doesn't have to be....your choice")

      
# FUnction to describe a router.
# WHat's connected to, metrics etc and adj sid to reach neighbor

def describe_node(router_dict,node):
  # Get rid of previous crap to make it easier on the eye.
  screen_clear()
  match=0
  print("\n\n\nAttempting to find info on node "+node+" ..............\n\n")
  for router, router_info in router_dict.items():
    if router_info['router'] == node:
      print("Matching node found......\n\n\n")
      match=1
      circuits=router_info['circuits']
      
      router_info2=router_info.copy()
      router_info2.pop('circuits')
      format_dict= yaml.safe_dump(router_info2)
      
      # I'm lazy so just dump the dict with the circuits removed for general node info.
      # Can't say the order will make much sense but meh.
      print(node+" router information:\n")
      print(format_dict)
      print("\n\n"+node+" core circuits:\n")
      # print the actual circuits in a more pleasant table.
      print (tabulate(circuits, headers="keys"))
  print ("\n\n\n\n")

      
  if match==0:
    print("ERROR - Node not found")
  
def screen_clear():
  if os.name == 'posix':
    _ = os.system('clear')
  else:
    # for windows platfrom
    _ = os.system('cls')   

def path_calc(nodes,router_dict,mode,he_type,path_name,tunnel_id):
  screen_clear()

  # SO nodes should contain the start of the tunnel and any explicit paths.
  # Now!....if you put a router as a next hop that is directly connected this
  # will it's interface IP and adj SID label
  # No support yet for picking up a link of of multiple to exist between two nodes. I might change that, who knows.
  # If the next node is not directly connected we will return the node SID. OK?
  
  node_list=nodes.split(",")
  node_index=0
  path_index=10
  node_list2=node_list.copy()
  sid_list=[]
  print("\n\nAttempting to generate path and tunnel config\n\n\n")
  if he_type=="xr":
    print ("!\nexplicit-path name "+path_name)
  elif he_type=="xe":
    print ("!\nip explicit-path name "+path_name)
  for z in node_list:
    #print("ZZZZZZZ "+z)
    #in_node=node_list[node_index]
    encoded_string = z.encode("ascii", "ignore")
    in_node=encoded_string.decode()
    #print("IN NODE "+in_node)
    if mode=='strict':    
      circuits=get_circuits(router_dict,in_node)    
      
      #in_node=z
      
      # get the next node and make sure there actually is one.
      
      del node_list2[0]
      if len(node_list2)==0:
        #print ("No more nodes to process")
        break
      
      else:
      
        next_node=node_list2[0]
        #print("next node is "+next_node)
        
        
      
        node_index+=1
        #print(node_index)      
        
      
      #print("nodes----- "+in_node+next_node)
      # Am I connected to the next hop in the path or is it loose
      circuit_match=0
      for x in circuits:
        neigh = x['neighbor']
        neigh_split=neigh.split('.')
        
        neigh_concise=neigh_split[0]
        if next_node==neigh_concise and circuit_match==0:
          
          next_ip_hop=x['neighbor_ip']
          next_asid_hop=x['neighbor_adj_sid']
          if he_type=="xr":
            print (" index "+str(path_index)+" next-address strict ipv4 unicast "+next_ip_hop)
            sid_list.append(next_asid_hop)
          elif he_type=="xe":
            print (" index "+str(path_index)+" next-address "+next_ip_hop)
            sid_list.append(next_asid_hop)
          path_index+=10
          circuit_match=1
          
      if circuit_match==0:
        expanded_node=next_node+".00-00"
        next_hop_detail=router_dict.get(expanded_node)
        next_ip_hop=next_hop_detail['rid']
        next_asid_hop=next_hop_detail['nsid']
        if he_type=="xr":
          print (" index "+str(path_index)+" next-address strict ipv4 unicast "+next_ip_hop)
          sid_list.append(next_asid_hop)
        elif he_type=="xe":
          print (" index "+str(path_index)+" next-address "+next_ip_hop)
          sid_list.append(next_asid_hop)
        path_index+=10
      
      #next_node= None
      circuits= None
    
    elif mode=='loose':
      del node_list2[0]
      if len(node_list2)==0:
        #print ("No more nodes to process")
        break
      
      else:
      
        next_node=node_list2[0]
        #print("next node is "+next_node)
        
        
      
        node_index+=1
        #print(node_index)      
      
      expanded_node=next_node+".00-00"
      next_hop_detail=router_dict.get(expanded_node)
      next_ip_hop=next_hop_detail['rid']
      next_asid_hop=next_hop_detail['nsid']
      if he_type=="xr":
        print ("index "+str(path_index)+" next-address strict ipv4 unicast "+next_ip_hop)
        sid_list.append(next_asid_hop)
      elif he_type=="xe":
        print ("index "+str(path_index)+" next-address "+next_ip_hop)
        sid_list.append(next_asid_hop)
      path_index+=10
    
  print("!")
  tunnel_dst = node_list.pop()
  expanded_tunnel_dst=tunnel_dst+".00-00"
  tunnel_dst_detail=router_dict.get(expanded_tunnel_dst)
  tunnel_ip_dst=tunnel_dst_detail['rid']
  
  if he_type=="xr":
    print ("explicit-path name "+path_name)
  elif he_type=="xe":
    print ("int tunnel"+str(tunnel_id))
    print (" ip unnumbered Loopback0")
    print (" mpls traffic-eng tunnels")
    print (" tunnel mode mpls traffic-eng")
    print (" tunnel destination "+ tunnel_ip_dst)
    print (" tunnel mpls traffic-eng autoroute announce")
    print (" tunnel mpls traffic-eng path-option 10 explicit name "+path_name+" segment-routing")
    print (" tunnel mpls traffic-eng fast-reroute\n\n\n\n")
    print ("Current SID list is: ")
    print (sid_list)
    print ("\n\n\n\n")
      
    
  
  
  # We need to get the circuits of a node.
  # I feel this could happen more than once so let's call another function to do it.

def get_circuits(router_dict,node):
  match=0
  for router, routers in router_dict.items():
    if routers['router'] == node:
      match=1
      circuits=routers['circuits']
      return circuits
  
  if match==0:
    print("ERROR - Node not found")
  

    
################################

seed_router=input("Enter seed router: ")
seed_user=input("Enter username: ")
seed_pass = getpass.getpass(prompt='Your password: ')
#seed_router="10.10.20.100"
#seed_user="test"
#seed_pass = "cisco"
driver = get_network_driver('ios')


device = driver(seed_router, seed_user,seed_pass)
device.open()
commands = ['show isis database']
cli_output=device.cli(commands)

database=list(cli_output.values())[0]



entries=database.split('\n')

#WHen we see the header line in the loop we now the data we want comes next so set this to 1 
header = 0

# Store the router IDs in here
lspid=[]

for line in entries:
  # If the headers line, we now real data comes next so set header to 1 and got to next iteration
  if line.startswith('LSPID                 LSP Seq Num'):
    header=1
    continue
  # If not seen the headers yet, skip the line as I don't (currently) care what's there.
  if header==0:
    continue
  # and here we have lines that begin with the LSP IDs. So split on space and push the LSP ID into the empty list.
  if header==1:
    #print(line)
    x=line.split()
    #print(x[0])
    lspid.append(x[0])

# Now we have all the LSP IDs in lspid list.
# Now we can star prasing the verbose database out per LSP ID.


# We'll shove all the crap in this dict
lspid_dict={}

int_start=0

int_index=0
print("\n\nLoading LSPDB.....\n\n")
for router in lspid:
  circuit_list=[]
  circuit_dict={}
  router_dict={}
  commands = ["show isis database " + router + " verbose"]
  cli_output=device.cli(commands)
  rtrdb=list(cli_output.values())[0]
  lsp_lines=rtrdb.split('\n')
  # SO now we have the LSP for this router and we can start pulling things out from them.
  
  for line in lsp_lines:
    # Get area ID
    if line.startswith('Area Address',2):
      x=line.split(':')
      area=x[1]
      area=area.replace(" ","")
      area=float(area)
      continue
    
    # Get area ID
    if line.startswith('Router ID',2):
      x=line.split(':')
      rid=x[1]
      rid=rid.replace(" ","")
      continue
      
    # Get configured SRGB
    if line.startswith('Segment Routing:',4):
      x=line.split()
      srgb_start=x[6]
      srgb_range=x[8]
      srgb_start=srgb_start.replace(" ","")
      srgb_start=int(srgb_start)
      srgb_range=srgb_range.replace(" ","")
      srgb_range=int(srgb_range)
      srgb_end=srgb_start + srgb_range - 1
      continue

      
     # Get configured SRLB
    if line.startswith('Segment Routing Local',4):
      x=line.split()
      srlb_start=x[6]
      srlb_range=x[8]
      srlb_start=srlb_start.replace(" ","")
      srlb_start=int(srlb_start)
      srlb_range=srlb_range.replace(" ","")
      srlb_range=int(srlb_range)
      srlb_end=srlb_start + srlb_range - 1
      continue

 
    # Hostname
    if line.startswith('Hostname',2):
      x=line.split(':')
      hostname=x[1]
      hostname=hostname.replace(" ","")
      continue
      
    # Look for the start of a link block
    if line.startswith('Metric',2) and re.search("IS-Extended",line):
      int_index=1
      int_start=1
      x=line.split()
      metric=x[1]
      neighbor=x[3]
      metric=metric.replace(" ","")
      metric=int(metric)
      #neighbor=neighbor.replace(" ","")

    # Max depth
    if line.startswith('MSD',6):
      x=line.split(':')
      msd=x[1]
      msd=msd.replace(" ","")
      msd=int(msd)
      continue
    
    #Figure out the adjacency SIDs    
    if int_start==1:
      if line.startswith('Adjacency SID',4):
        x=line.split()
        adj_sid_local=x[2]
        adj_sid_local=adj_sid_local[6:]
        int_start=2
        adj_sid_local=int(adj_sid_local)
        continue
      
    if int_start==2:
      if line.startswith('Adjacency SID',4):
        x=line.split()
        adj_sid_remote=x[2]
        adj_sid_remote=adj_sid_remote[6:]
        int_start=2
        adj_sid_remote=int(adj_sid_remote)
        continue
    
    # Interface IPs    
    if line.startswith('Interface IP Address',4):
      x=line.split()
      local_ip=x[3]  
      local_ip=local_ip.replace(" ","")   
      continue   

    if line.startswith('Neighbor IP Address',4):
      x=line.split()
      neighbor_ip=x[3]  
      neighbor_ip=neighbor_ip.replace(" ","")
      continue
      
    
    if line.startswith('Admin. Weight',4):
      x=line.split()
      temetric=x[2]
      temetric=temetric.replace(" ","")
      temetric=int(temetric)

      
    if line.startswith('Physical BW',4):
      x=line.split()
      link_bw=x[2]  
      link_bw=link_bw.replace(" ","")
      #print (link_bw)
      #put circuit into a dict then
      circuit_dict={'neighbor':neighbor,'metric':metric,'te_metric':temetric,'local_ip':local_ip,'local_adj_sid':adj_sid_local,'neighbor_ip':neighbor_ip,'neighbor_adj_sid':adj_sid_remote}
      #print (circuit_dict)     
      circuit_list.append(circuit_dict)      
      index_start=0    
    
    if line.startswith('Prefix-SID Index',4):
      x=line.split()
      nsid=x[2]  
      nsid=nsid.replace(" ","")   
      nsid=nsid.replace(",","")
      nsid=int(nsid)
      nsid=nsid + srgb_start 
      #nsid=str(nsid)      
    
  #print(router)
  #print(circuit_list)
  
  
  #Build the dict for the router
  router_dict={'router':hostname,'rid':rid,'nsid':nsid,'area':area,'srgb_start':srgb_start,'srgb_end':srgb_end,'srlb_start':srlb_start,'srlb_end':srlb_end,'msd':msd,'circuits':circuit_list}
  
  #Push the router dict to the overall LSPDB dict
  lspid_dict[router]=router_dict

print("\n\nChecking for duplicate SIDs.....\n\n")

duplicate_sid_check(lspid_dict)

# Add thes as options at some point when I can be arsed
srgb_standard_start = 16000
srgb_standard_end = 23999

print("\n\nChecking for consistent SRGB.....\n\n")
duplicate_srgb(lspid_dict,srgb_standard_start,srgb_standard_end)

#lookup_node="p2"
w_control=0

while w_control<3:

  next_action=input("What do you want to do?\n 1. Describe Node\n 2. Path calc\n 3. Quit\nEnter choice: ")

  #int(next_action)
  try:
    control=int(next_action)
    
  except ValueError:
    print("Not a number, try again")

  if control==3:
    w_control=3
    break
  
  if control==1:
    node_describe=input("Enter node:")
    
    describe_node(lspid_dict,node_describe)
  
  if control==2:
    pathlist=input("Enter comma seperated list of routers (pe1,p1,p2,pe30): ")
    #pathlist="pe11,p22,p1,pe12,p23,p2,pe31"
    
    # Loose or strict
    #pathtype="strict"
    pathtype=input("want this to be strict (try) path or loose? [strict|loose]: ")
    
    # Head end type xe / xr maybe add Junos at some point
    
    #he_type="xe"
    he_type=input("Head end type? [xe|xr]: ")
    #path_name="STUPID_PATH"
    path_name=input("Name of explicit path?: ")
    #tunnel_id=10
    tunnel_id=input("Numeric tunnel index: ")
    path_calc(pathlist,lspid_dict,pathtype,he_type,path_name,tunnel_id)
  
  
  
  # Dump out as yaml
pretty_format = yaml.safe_dump(lspid_dict)
print(pretty_format)

  
