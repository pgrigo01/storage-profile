#!/usr/bin/env python3
"""
Persistent Storage Profile Example

This profile creates a persistent local dataset and attaches it to a node.
The dataset is mounted at /mnt/storage on the node and is marked as persistent,
so that its contents can be reused in future experiments.
"""

import geni.portal as portal
import geni.rspec.pg as pg

# Create a portal object.
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()

# Create a persistent local dataset.
# The "local" type indicates that the storage is on the local disk.
# Setting persistent to True makes the dataset persistent across experiments.
ds = request.addDataset("persistentStorage", "local", "/mnt/storage")
ds.persistent = True  # Mark the dataset as persistent

# Create a node.
node = request.addResource(pg.Node("node1"))
node.disk_image = "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU20-64-STD"

# Attach the dataset to the node.
node.addDataset(ds)

# Optionally, add a startup service to automatically mount the dataset.
# (In many cases, CloudLab will auto-mount it, but you can also ensure it via a script.)
startupService = node.addService(pg.Execute(shell="bash", command="sudo mount /mnt/storage"))
 
# Print the RSpec to the enclosing portal.
pc.printRequestRSpec(request)
