# lspdb



 Connects to IOS XE router, grabs the LSPDB from IS-IS.
 Can be used to tell you abut a router in the topology.
 Can (in a very basic manner) create head end tunnel config for SR TE paths and tell you the SID list from a list of routers you want in the path.
 Mostly used for massing about in a lab and creating ad-hoc SR-TE paths.
 
 Looks a bit like:
 
>  ----------------------------------
>  
>  $ python lspdb.py
> Enter seed router: 10.10.20.100
> Enter username: test
> Your password:
> 
> 
> Loading LSPDB.....
> 
> 
> 
> 
> Checking for duplicate SIDs.....
> 
> 
> No duplicate node SIDs
> 
> 
> 
> 
> Checking for consistent SRGB.....
> 
> 
> SRGB is consistent......it doesn't have to be....your choice
> 
>  
>  What do you want to do?
>  1. Describe Node
>  2. Path calc
>  3. Quit
> Enter choice: 1
> Enter node:p23
> 
> 
> Attempting to find info on node p23 ..............
> 
> 
> Matching node found......
> 
> 
> 
> p23 router information:
> 
> area: 49.0001
> msd: 10
> nsid: 16023
> rid: 23.23.23.23
> router: p23
> srgb_end: 23999
> srgb_start: 16000
> srlb_end: 15999
> srlb_start: 15000
> 
> 
> 
> p23 core circuits:
> 
> neighbor      metric    te_metric  local_ip      local_adj_sid  neighbor_ip      neighbor_adj_sid
> ----------  --------  -----------  ----------  ---------------  -------------  ------------------
> p2.00             10           10  10.0.0.17             24000  10.0.0.16                   24001
> p22.00            10           10  10.0.0.13             24002  10.0.0.12                   24003
> pe31.00           10           10  10.0.0.20             24004  10.0.0.21                   24005
> 
> 
> 
> 
> 
> What do you want to do?
>  1. Describe Node
>  2. Path calc
>  3. Quit
>  Enter choice: 2
> Enter comma seperated list of routers (pe1,p1,p2,pe30): pe11,p1,p2,p23,pe31
> want this to be strict (try) path or loose? [strict|loose]: strict
> Head end type? [xe|xr]: xe
> Name of explicit path?: TEST_PATH
> Numeric tunnel index: 100
> 
> 
> Attempting to generate path and tunnel config
> 
> 
> 
> !
> ip explicit-path name TEST_PATH
>  index 10 next-address 10.0.0.1
>  index 20 next-address 10.0.0.9
>  index 30 next-address 10.0.0.17
>  index 40 next-address 10.0.0.21
> !
> int tunnel100
>  ip unnumbered Loopback0
>  mpls traffic-eng tunnels
>  tunnel mode mpls traffic-eng
>  tunnel destination 31.31.31.31
>  tunnel mpls traffic-eng autoroute announce
>  tunnel mpls traffic-eng path-option 10 explicit name TEST_PATH segment-routing
>  tunnel mpls traffic-eng fast-reroute
> 
> 
> 
> 
> Current SID list is:
> [19, 19, 23, 24005]
> 
> 
> 
> 
> 
> What do you want to do?
>  1. Describe Node
>  2. Path calc
>  3. Quit
