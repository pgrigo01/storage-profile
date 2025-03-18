# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg
# Import the InstaGENI library.
import geni.rspec.igext as ig
# Import the Emulab specific extensions.
import geni.rspec.emulab as emulab

# Create a portal object,
pc = portal.Context()

agglist = [
    ("urn:publicid:IDN+emulab.net+authority+cm", "emulab.net"),
    ("urn:publicid:IDN+utah.cloudlab.us+authority+cm", "utah.cloudlab.us"),
    ("urn:publicid:IDN+clemson.cloudlab.us+authority+cm", "clemson.cloudlab.us"),
    ("urn:publicid:IDN+wisc.cloudlab.us+authority+cm", "wisc.cloudlab.us"),
    ("urn:publicid:IDN+apt.emulab.net+authority+cm", "apt.emulab.net"),
    ("", "Any")
]

imagelist = [
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU20-64-STD', 'UBUNTU 20.04'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU22-64-STD', 'UBUNTU 22.04'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU24-64-STD', 'UBUNTU 24.04'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//CENTOS7-64-STD', 'CENTOS 7'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//FBSD113-64-STD', 'FreeBSD 11.3')
]

pc.defineParameter(
    "aggregate", "Specific Aggregate",
    portal.ParameterType.STRING,
    agglist[0][0], agglist)
pc.defineParameter(
    "image", "Node Image",
    portal.ParameterType.IMAGE,
    imagelist[0][0],
    imagelist,
    longDescription="The image your node will run.")
pc.defineParameter(
    "routableIP", "Routable IP",
    portal.ParameterType.BOOLEAN, False,
    longDescription="Add a routable IP to the VM.")
# Add parameter for persistent storage
pc.defineParameter(
    "persistent_storage", "Persistent Storage Size (GB)",
    portal.ParameterType.INTEGER, 0,
    longDescription="The size of persistent storage to mount at /mydata. 0 means no persistent storage.")
pc.defineStructParameter(
    "sharedVlans", "Add Shared VLAN", [],
    multiValue=True, itemDefaultValue={}, min=0, max=None,
    members=[
        portal.Parameter(
            "createSharedVlan", "Create Shared VLAN",
            portal.ParameterType.BOOLEAN, False,
            longDescription="Create a new shared VLAN with the name above, and connect the first node to it."),
        portal.Parameter(
            "connectSharedVlan", "Connect to Shared VLAN",
            portal.ParameterType.BOOLEAN, False,
            longDescription="Connect an existing shared VLAN with the name below to the first node."),
        portal.Parameter(
            "name", "Shared VLAN Name",
            portal.ParameterType.STRING, "",
            longDescription="A shared VLAN name (functions as a private key allowing other experiments to connect to this node/VLAN), used when the 'Create Shared VLAN' or 'Connect to Shared VLAN' options above are selected.  Must be fewer than 32 alphanumeric characters."),
        portal.Parameter(
            "ip_address", "Shared VLAN IP Address",
            portal.ParameterType.STRING, "10.254.254.1",
            longDescription="Set the IP address for the shared VLAN interface.  Make sure to use an unused address within the subnet of an existing shared vlan!"),
        portal.Parameter(
            "subnet_mask", "Shared VLAN Netmask",
            portal.ParameterType.STRING, "255.255.255.0",
            longDescription="Set the subnet mask for the shared VLAN interface, as a dotted quad.")])

params = pc.bindParameters()

i = 0
for x in params.sharedVlans:
    n = 0
    if x.createSharedVlan:
        n += 1
    if x.connectSharedVlan:
        n += 1
    if n > 1:
        err = portal.ParameterError(
            "Must choose only a single shared vlan operation (create, connect)",
            ['sharedVlans[%d].createSharedVlan' % (i,),
             'sharedVlans[%d].connectSharedVlan' % (i,)])
        pc.reportError(err)
    if n == 0:
        err = portal.ParameterError(
            "Must choose one of the shared vlan operations: create, connect",
            ['sharedVlans[%d].createSharedVlan' % (i,),
             'sharedVlans[%d].connectSharedVlan' % (i,)])
        pc.reportError(err)
    i += 1

pc.verifyParameters()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()

tour = ig.Tour()
tour.Description(ig.Tour.TEXT, "Create a single shared-mode VM and host or connect to shared vlan(s).")
request.addTour(tour)

sharedvlans = []

node = ig.XenVM("node-0")
node.disk_image = params.image
node.exclusive = False

# Add persistent storage if requested
if params.persistent_storage > 0:
    bs = node.Blockstore("bs", "/mydata")
    bs.size = str(params.persistent_storage) + "GB"
    bs.placement = "any"

if params.routableIP:
    node.routable_control_ip = True
if params.aggregate:
    node.component_manager_id = params.aggregate
if params.image:
    node.disk_image = params.image
k = 0
for x in params.sharedVlans:
    iface = node.addInterface("ifSharedVlan%d" % (k,))
    if x.ip_address:
        iface.addAddress(
            pg.IPv4Address(x.ip_address, x.subnet_mask))
    sharedvlan = pg.Link('shared-vlan-%d' % (k,))
    sharedvlan.addInterface(iface)
    if x.createSharedVlan:
        sharedvlan.createSharedVlan(x.name)
    else:
        sharedvlan.connectSharedVlan(x.name)
    sharedvlan.link_multiplexing = True
    sharedvlan.best_effort = True
    sharedvlans.append(sharedvlan)
    k += 1

request.addResource(node)
for sv in sharedvlans:
    request.addResource(sv)

pc.printRequestRSpec(request)