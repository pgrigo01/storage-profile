#!/usr/bin/env python3

import geni.portal as portal
import geni.rspec.pg as pg
import geni.rspec.emulab as emulab

pc = portal.Context()
request = pc.makeRequestRSpec()

# Create a node
node = request.RawPC("node1")
node.disk_image = "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU20-64-STD"

# Create a blockstore for local persistent storage
bs = node.Blockstore("bs0", "/mnt/storage")
# Give the dataset a unique name (alphanumeric, underscores, etc.)
bs.dataset = "myPersistentDataset"
bs.readonly = False
bs.persistent = True

pc.printRequestRSpec(request)
