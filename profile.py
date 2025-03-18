#!/usr/bin/env python3

import geni.portal as portal
import geni.rspec.pg as pg

pc = portal.Context()
request = pc.makeRequestRSpec()

# Create a node
node = request.RawPC("node1")
node.disk_image = "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU20-64-STD"

# Create a blockstore (like a disk) on this node, mounted at /mnt/storage
bs = node.Blockstore("bs0", "/mnt/storage")

# 1) Use a simple alphanumeric name for a new dataset (no spaces).
bs.dataset = "myPersistentDataset"

# 2) Provide a size so that CloudLab knows to create a new dataset.
bs.size = "10GB"

# 3) Optional: let CloudLab place it on any available disk.
#    (If you omit this, CloudLab picks a default. "any" is often used.)
bs.placement = "any"

# 4) Make the dataset persistent across experiment restarts.
bs.persistent = True

# 5) Set read-only to False so you can write to it.
bs.readonly = False

pc.printRequestRSpec(request)
