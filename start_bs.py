#!/opt/conda_envs/lsdc_dev3/bin/ipython -i
import asyncio
#from ophyd import setup_ophyd
from ophyd import *
setup_ophyd()

# Subscribe metadatastore to documents.
# If this is removed, data is not saved to metadatastore.
import metadatastore.commands
from bluesky.global_state import gs
gs.RE.subscribe_lossless('all', metadatastore.commands.insert)
from bluesky.callbacks.broker import post_run
# At the end of every run, verify that files were saved and
# print a confirmation message.
from bluesky.callbacks.broker import verify_files_saved
gs.RE.subscribe('stop', post_run(verify_files_saved))

# Import matplotlib and put it in interactive mode.
import matplotlib.pyplot as plt
plt.ion()

# Make plots update live while scans run.
from bluesky.utils import install_qt_kicker
install_qt_kicker()

# Optional: set any metadata that rarely changes.
# RE.md['beamline_id'] = 'YOUR_BEAMLINE_HERE'

# convenience imports
from ophyd.commands import *
from bluesky.callbacks import *
from bluesky.spec_api import *
from bluesky.global_state import gs, abort, stop, resume
from databroker import (DataBroker as db, get_events, get_images,
                                                get_table, get_fields, restream, process)
from time import sleep
import numpy as np
from mercury import *

RE = gs.RE  # convenience alias
#rest is hugo
abort = RE.abort
resume = RE.resume
stop = RE.stop

RE.md['group'] = 'amx'
RE.md['beamline_id'] = 'AMX'
#RE.ignore_callback_exceptions = False

loop = asyncio.get_event_loop()
loop.set_debug(False)



from ophyd import (SingleTrigger, TIFFPlugin, ProsilicaDetector,
                   ImagePlugin, StatsPlugin, ROIPlugin, DetectorBase, HDF5Plugin,
                   AreaDetector)

import ophyd.areadetector.cam as cam

from ophyd.areadetector.filestore_mixins import (FileStoreTIFFIterativeWrite,
                                                 FileStoreHDF5IterativeWrite)

from ophyd import Component as Cpt

class StandardProsilica(SingleTrigger, ProsilicaDetector):
    #tiff = Cpt(TIFFPluginWithFileStore,
    #           suffix='TIFF1:',
    #           write_path_template='/XF16ID/data/')
    image = Cpt(ImagePlugin, 'image1:')
    roi1 = Cpt(ROIPlugin, 'ROI1:')
#    roi2 = Cpt(ROIPlugin, 'ROI2:')
#    roi3 = Cpt(ROIPlugin, 'ROI3:')
#    roi4 = Cpt(ROIPlugin, 'ROI4:')
    stats1 = Cpt(StatsPlugin, 'Stats1:')
#    stats2 = Cpt(StatsPlugin, 'Stats2:')
#    stats3 = Cpt(StatsPlugin, 'Stats3:')
#    stats4 = Cpt(StatsPlugin, 'Stats4:')
    stats5 = Cpt(StatsPlugin, 'Stats5:')

def filter_camera_data(camera):
    camera.read_attrs = ['stats1', 'stats5']
    #camera.tiff.read_attrs = []  # leaving just the 'image'
    camera.stats1.read_attrs = ['total', 'centroid']
    #camera.stats2.read_attrs = ['total', 'centroid']
    #camera.stats3.read_attrs = ['total', 'centroid']
    #camera.stats4.read_attrs = ['total', 'centroid']
    camera.stats5.read_attrs = ['total', 'centroid']


cam_7 = StandardProsilica('XF:17IDC-ES:FMX{Cam:7}', name='cam_7')
filter_camera_data(cam_7)

omega = EpicsMotor("XF:17IDC-ES:FMX{Gon:1-Ax:O}Mtr",name="omega")
#gs.DETS=[cam_7,mercury]
gs.DETS=[mercury]
mercury.count_time.set(1.0)
#mercury.count_time = 1
#gs.PLOT_Y=cam_7.stats1.total.name
#gs.PLOT_Y=mercury.mca.spectrum.value.sum

