# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg
# Import the InstaGENI library.
import geni.rspec.igext as ig
# Import the Emulab specific extensions.
import geni.rspec.emulab as emulab

# Create a portal object.
pc = portal.Context()

# ---------------------------------------------------------------------------
# Aggregates and Images

agglist = [
    ("urn:publicid:IDN+emulab.net+authority+cm", "emulab.net"),
    ("urn:publicid:IDN+utah.cloudlab.us+authority+cm", "utah.cloudlab.us"),
    ("urn:publicid:IDN+clemson.cloudlab.us+authority+cm", "clemson.cloudlab.us"),
    ("urn:publicid:IDN+wisc.cloudlab.us+authority+cm", "wisc.cloudlab.us"),
    ("urn:publicid:IDN+apt.emulab.net+authority+cm", "apt.emulab.net"),
    ("", "Any")
]

imagelist = [
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU18-64-STD', 'UBUNTU 18.04'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU16-64-STD', 'UBUNTU 16.04'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU20-64-STD', 'UBUNTU 20.04'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//CENTOS7-64-STD', 'CENTOS 7'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//FBSD113-64-STD', 'FreeBSD 11.3')
]

pc.defineParameter(
    "aggregate", "Select Aggregate (Cluster)",
    portal.ParameterType.STRING,
    agglist[0][0], 
    agglist,
    longDescription="Pick which cluster you want to run on."
)

pc.defineParameter(
    "image", "Node Image",
    portal.ParameterType.IMAGE,
    imagelist[0][0],
    imagelist,
    longDescription="Which OS image the RawPC will use."
)

pc.defineParameter(
    "routableIP", "Routable IP",
    portal.ParameterType.BOOLEAN, 
    False,
    longDescription="Add a routable IP to the node."
)

# ---------------------------------------------------------------------------
# Short-Term (Ephemeral) Local Blockstore Parameters

pc.defineParameter(
    "wantShortTermDataset",
    "Create an Ephemeral Local Blockstore?",
    portal.ParameterType.BOOLEAN,
    True,
    longDescription="Select this option to create ephemeral 'scratch' space on the local disk."
)

pc.defineParameter(
    "shortTermDatasetSizeGB",
    "Ephemeral Blockstore Size (GB)",
    portal.ParameterType.INTEGER,
    10,
    longDescription="Size of the local ephemeral blockstore in gigabytes."
)

pc.defineParameter(
    "shortTermDatasetMountPoint",
    "Mount Point for Ephemeral Blockstore",
    portal.ParameterType.STRING,
    "/mydata",
    longDescription="The mount point for the ephemeral local disk on your node."
)

params = pc.bindParameters()

# Validate parameters, if needed.
pc.verifyParameters()

# ---------------------------------------------------------------------------
# Create the RSpec Request
request = pc.makeRequestRSpec()

# Optional: Add a Tour Description
tour = ig.Tour()
tour.Description(ig.Tour.TEXT, "Create a single RawPC node with ephemeral local blockstore.")
request.addTour(tour)

# ---------------------------------------------------------------------------
# Create a RawPC node (not XenVM), so local ephemeral storage is possible
node = request.RawPC("node-0")

# Set the OS image
node.disk_image = params.image

# If you want a routable IP
if params.routableIP:
    node.routable_control_ip = True

# Use aggregator param to pick the cluster
if params.aggregate:
    node.component_manager_id = params.aggregate

# ---------------------------------------------------------------------------
# Ephemeral Local Blockstore (Scratch Disk) if desired
if params.wantShortTermDataset:
    bs = request.Blockstore("bs0", params.shortTermDatasetMountPoint)
    bs.size = "{}GB".format(params.shortTermDatasetSizeGB)
    bs.temporary = True  # ephemeral
    bs.mount = node  # attach to the node

# ---------------------------------------------------------------------------
# Print the RSpec
pc.printRequestRSpec(request)
