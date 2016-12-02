import sys
import os
import socket
import time

import six

import uuid

import bson

import amostra.client.commands as acc
import conftrak.client.commands as ccc
from analysisstore.client.commands import AnalysisClient

# TODO: get the beamline_id from parameter
BEAMLINE_ID = '17ID1'

sample_ref = None
container_ref = None
request_ref = None
configuration_ref = None
mds_ref = None
analysis_ref = None


services_config = {
    'amostra': {'host': 'localhost', 'port': '7770'},
    'conftrak': {'host': 'localhost', 'port': '7771'},
    'metadataservice': {'host': 'localhost', 'port': '7772'},
    'analysisstore': {'host': 'localhost', 'port': '7773'}
}


def db_connect(params=services_config):
    """
    recommended idiom:
    """
    sample_ref = acc.SampleReference(**params['amostra'])
    container_ref = acc.ContainerReference(**params['amostra']))
    request_ref = acc.RequestReference(**params['amostra']))

    configuration_ref = ccc.ConfigurationReference(**services_config['conftrak']))

    analysis_ref = AnalysisClient(**services_config['analysisstore'])


# should be in config :(
primaryDewarName = 'primaryDewar'


def createBeamline(bl_name, bl_num):
    data = {"key": "beamline", "name": bl_name, "number": bl_num}
    uid = configuration_ref.create(beamline_id=BEAMLINE_ID, **data)
    return uid


def searchBeamline(**kwargs):
    try:
        return list(configuration_ref.find(key="beamline", **kwargs)
    except StopIteration:
        return None


def getBeamlineByNumber(num):
    """eg. 17id1, 17id2, 16id1"""
    try:
        return list(configuration_ref.find(key="beamline", number=num))
    except StopIteration:
        return None


def createContainer(name, capacity, **kwargs):
    """
    container_name:  string, name for the new container, required
    kwargs:          passed to constructor
    """
    if capacity is not None:
        kwargs['content'] = [None]*capacity
    uid = container_ref.create(name=name, **kwargs)
    return uid


def updateContainer(cont_info):
    cont = cont_info['uid']
    q = {'uid': cont_info.pop('uid', '')}
    container_ref.update(q, cont_info)

    return cont


def createSample(sample_name, **kwargs):
    """
    sample_name:  string, name for the new sample, required
    kwargs:       passed to constructor
    """
    # initialize request count to zero
    if 'request_count' not in kwargs:
        kwargs['request_count'] = 0

    uid = sample_ref.create(name=sample_name, **kwargs)
    return uid


def incrementSampleRequestCount(sample_id):
    """
    increment the 'request_count' attribute of the specified sample by 1
    """

    # potential for race here?
    sample_ref.update(query={'uid': sample_id}, update={'$inc': {'request_count': 1}})
    return getSampleRequestCount(sample_id)


def getSampleRequestCount(sample_id):
    """
    get the 'request_count' attribute of the specified sample
    """
    s = list(getSampleByID(sample_id))
    return s[0]['request_count']


def getRequestsBySampleID(sample_id, active_only=True):
    """
    return a list of request dictionaries for the given sample_id
    """
    params = {'sample': sample_id}
    if active_only:
        params['active'] = True
    reqs = list(requests_ref.find(**params)
    return reqs


def getSampleByID(sample_id):
    """
    sample_id:  required, integer
    """
    s = list(sample_ref.find(uid=sample_id))
    return s


def getSampleNamebyID(sample_id):
    """
    sample_id:  required, integer
    """
    s = getSampleByID(sample_id)
    return s['name']


def getContainerIDbyName(container_name):
    c = container_ref.find(name=container_name)
    return [cn['uid'] for cn in c]


def getContainerNameByID(container_id):
    """
    container_id:  required, integer
    """
    c = list(container_ref.find(uid=container_id))
    return c[0]['name']


def createResult(result_type, request_id=None, sample_id=None, result_obj=None, timestamp=None,
                 **kwargs):
    """
    result_type:  string
    request_id:   int
    sample_id:    int
    result_obj:   dict to attach
    timestamp:
    """
    header = analysis_ref.insert_analysis_header(time=timestamp, uid=str(uuid.uuid4()),
                                                sample=sample_id, request=request_id,
                                                provenance={'lsdc':1}, result_obj=result_obj,**kwargs)

    return header


def getResult(result_id):
    """
    result_id:  required, int
    """
    header = list(analysis_ref.find_analysis_header(uid=result_id))
    return header[0]


def getResultsforRequest(request_id):
    """
    Takes an integer request_id  and returns a list of matching results or [].
    """
    headers = list(analysis_ref.find_analysis_header(request=request_id))
    return headers


def getResultsforSample(sample_id):
    """
    Takes a sample_id and returns it's resultsList or [].
    """
    headers = list(analysis_ref.find_analysis_header(sample=sample_id))
    return headers


def getRequestByID(request_id, active_only=True):
    """
    return a list of request dictionaries for the given request_id
    """
    params = {'uid': request_id}
    if active_only:
        params['active'] = True
    reqs = list(requests_ref.find(**params)
    return reqs


def addResultforRequest(result_type, request_id, result_obj=None, timestamp=None,
                        **kwargs):
    """
    like createResult, but also adds it to the resultList of result['sample_id']
    """
    sample = getRequestByID(request_id)['sample'] 
    r = createResult(result_type=result_type, request_id=request_id, sample_id=sample, result_obj=result_obj, timestamp=timestamp, **kwargs)
    return r


def addResulttoSample(result_type, sample_id, result_obj=None, timestamp=None,
                        as_mongo_obj=False, **kwargs):
    """
    like addResulttoRequest, but without a request
    """
    r = createResult(result_type=result_type, request_id=None, sample_id=sample, result_obj=result_obj, timestamp=timestamp, **kwargs)
    return r


def addResulttoBL(result_type, beamline_id, result_obj=None, timestamp=None,
                  **kwargs):
    """
    add result to beamline
    beamline_id: the integer, 'beamline_id' field of the beamline entry

    other fields are as for createRequest
    """
    r = createResult(result_type=result_type, request_id=None, sample_id=None, result_obj=result_obj, timestamp=timestamp, beamline_id=beamline_id, **kwargs)
    return r


def getResultsforBL(id=None, name=None, number=None):
    """
    Retrieve results using either BL id, name, or number (tried in that order)
    Returns a generator of results
    """
    if id is None:
        if name is None:
            key = 'number'
            val = number
        else:
            key = 'name'
            val = name

        query = {key: val}
        b = searchBeamline(**query)
        if b is None
            yield None
            raise StopIteration

        id = b['uid']

        if id is None:
            yield None
            raise StopIteration

    results = list(analysis_ref.find_analysis_header(beamline_id=id))

    for r in results:
        yield r


def addFile(data=None, filename=None):
    """
    Put the file data into the GenericFile collection,
    return the _id for use as an id or ReferenceField.

    If a filename kwarg is given, read data from the file.
    If a data kwarg is given or data is the 1st arg, store the data.
    If both or neither is given, raise an error.
    """
    #TODO: Decide what to do with this method
    raise NotImplemented
    '''
    if filename is not None:
        if data is not None:
            raise ValueError('both filename and data kwargs given.  can only use one.')
        else:
            with open(filename, 'r') as file:  # do we need 'b' for binary?
                data = file.read()  # is this blocking?  might not always get everything at once?!

    elif data is None:
        raise ValueError('neither filename or data kwargs given.  need one.')

    f = GenericFile(data=data)
    f.save()
    f.reload()  # to fetch generated id
    return f.to_dbref()
    '''

def getFile(_id):
    """
    Retrieve the data from the GenericFile collection
    for the given _id or db_ref

    Returns the data in Binary.  If you know it's a txt file and want a string,
    convert with str()

    Maybe this will be automatically deref'd most of the time?
    Only if they're mongoengine ReferenceFields...
    """
    #TODO: Decide what to do with this method
    raise NotImplemented
    '''
    try:
        _id = _id.id

    except AttributeError:
        pass

    f = GenericFile.objects(__raw__={'_id': _id})  # yes it's '_id' here but just 'id' below, gofigure
    return _try0_dict_key(f, 'file', 'id', _id, None,
                           dict_key='data')
    '''

def createRequest(request_type, request_obj=None, timestamp=None, as_mongo_obj=False, **kwargs):
    """
    request_type:  required, name (string) of request type, dbref to it's db entry, or a Type object
    request_obj:  optional, stored as is, could be a dict of collection parameters, or whatever
    timestamp:  datetime.datetime.now() if not provided
    priority:  optional, integer priority level

    anything else (priority, sample_id) can either be embedded in the
    request_object or passed in as keyword args to get saved at the
    top level.
    """
    kwargs['request_type'] = request_type
    kwargs['timestamp'] = timestamp
    kwargs['request_obj'] = request_obj

    uid = request_ref.create(**kwargs)

    return uid 


def addRequesttoSample(sample_id, request_type, request_obj=None, timestamp=None,
                       as_mongo_obj=False, **kwargs):
    """
    sample_id:  required, integer sample id
    request_type:  required, name (string) of request type, dbref to it's db entry, or a Type object
    request_obj:  optional, stored as is, could be a dict of collection parameters, or whatever
    timestamp:  datetime.datetime.now() if not provided

    anything else (priority, sample_id) can either be embedded in the
    request_object or passed in as keyword args to get saved at the
    top level.
    """

    kwargs['sample_id'] = sample_id
    r = createRequest(request_type, request_obj=request_obj, timestamp=timestamp,
                      as_mongo_obj=True, **kwargs)

    return r


def insertIntoContainer(container_name, position, itemID):
    c = getContainerByName(container_name)
    if c is not None:
        cnt = c['content']
        diff = len(cnt) - (position - 1)
        if diff > 0:
            cnt.extend([None]*diff)
        cnt[position - 1] = itemID  # most people don't zero index things
        c['content'] = cnt
        updateContainer(c)
        return True
    else:
        print("bad container name")
        return False


def getContainers(filters=None): 
    """get *all* containers"""
    if filters is not None:
        c = list(container_ref.find(**filters))
    else:
        c = list(container_ref.find())
    return c


def getContainersByType(type_name, group_name): 
    #TODO: group_name was not being used kept for compatibility
    return getContainers(filters={type_name: type_name})

def getAllPucks():
    # find all the types desended from 'puck'?
    # and then we could do this?
    return getContainersByType("puck", "")


def getPrimaryDewar():
    """
    returns the mongo object for a container with a name matching
    the global variable 'primaryDewarName'
    """

    return getContainerByName(primaryDewarName)


def getContainerByName(container_name):
    c = getContainers(filters={'name': container_name})
    return c


def getContainerByID(container_id):
    c = getContainers(filters={'uid': container_id})
    return c


def getQueue():
    """
    returns a list of request dicts for all the samples in the container
    named by the global variable 'primaryDewarName'
    """

    # seems like this would be alot simpler if it weren't for the Nones?

    ret_list = []

    # try to only retrieve what we need...
    # Use .first() instead of [0] here because when the query returns nothing,
    # .first() returns None while [0] generates an IndexError
    # Nah... [0] is faster and catch Exception...
    try:
        items = getPrimaryDewar()['content']
    except IndexError as AttributeError:
        raise ValueError('could not find container: "{0}"!'.format(primaryDewarName))

    items = set(items)
    items.discard(None)  # skip empty positions

    sample_list = []
    contents = [getContainerByID(uid)['content'] for uid in items]
    for samp in contents:
        sil = set(samp)
        sil.discard(None)
        sample_list += sil

    for s in sample_list:
        reqs = getRequestsBySampleID(s, active_only=True)
        for request in reqs:
            yield request


def getCoordsfromSampleID(sample_id):
    """
    returns the container position within the dewar and position in
    that container for a sample with the given id in one of the
    containers in the container named by the global variable
    'primaryDewarName'
    """
    try:
        primary_dewar_item_list = getPrimaryDewar()['content']
    except IndexError as AttributeError:
        raise ValueError('could not find container: "{0}"!'.format(primaryDewarName))
    try:

    # eliminate empty item_list slots
    pdil_set = set(primary_dewar_item_list)
    pdil_set.discard(None)

    # find container in the primary_dewar_item_list (pdil) which has the sample
    filters = {'$and': {'uid': {'$in':pdil_set}, 'content': {'$in':[sample_id]}}}
    c = getContainers(filters=filters)

    # get the index of the found container in the primary dewar
    i = primary_dewar_item_list.index(c['uid'])

    # get the index of the sample in the found container item_list
    j = c.['content'].index(sample_id)

    # get the container_id of the found container
    puck_id = c['uid']

    return (i, j, puck_id)


def popNextRequest():
    """
    this just gives you the next one, it doesn't
    actually pop it off the stack
    """
    # is this more 'getNextRequest'? where's the 'pop'?
    orderedRequests = getOrderedRequestList()
    try:
        if (orderedRequests[0]["priority"] != 99999):
            if orderedRequests[0]["priority"] > 0:
                return orderedRequests[0]
            else: #99999 priority means it's running, try next
                if orderedRequests[1]["priority"] > 0:
                    return orderedRequests[1]
    except IndexError:
        pass

    return {}


def getRequest(reqID):  # need to get this from searching the dewar I guess
    reqID = int(reqID)
    """
    request_id:  required, integer id
    """
    r = getRequestByID(reqID)
    return r

def updateRequest(request_dict):
    """
    This is not recommended once results are recorded for a request!
    Using a new request instead would keep the apparent history
    complete and intuitive.  Although it won't hurt anything if you've
    also recorded the request params used inside the results and query
    against that, making requests basically ephemerally useful objects.
    """

    if 'uid' in request_dict:
        r_uid = request_dict.pop('uid', '')
        r = request_ref.update({'uid':r_uid},request_dict)

        addRequesttoSample(**request_dict)


def deleteRequest(reqObj):
    """
    reqObj should be a dictionary with a 'uid' field
    and optionally a 'sample_uid' field.

    """

    r_id = reqObj['request_id']

    r = getRequestByID(r_id)
    r['active'] = False
    updateRequest(r)


def updateSample(sampleObj):
    if 'uid' in sampleObj:
        s_uid = sampleObj.pop('uid','')
        s = sample_ref.update({'uid': s_uid}, sampleObj)


def deleteSample(sample_uid):
    s = getSampleByID(sample_uid])
    s['active'] = False
    updateSample(s)


def removePuckFromDewar(dewarPos):
    dewar = getPrimaryDewar()
    dewar['content'][dewarPos] = None
    updateContainer(dewar)


def updatePriority(request_id, priority):
    r = getRequest(request_id)
    r['priority'] = priority
    updateRequest(r)


def getPriorityMap():
    """
    returns a dictionary with priorities as keys and lists of requests
    having those priorities as values
    """

    priority_map = {}

    for request in getQueue():
        try:
            priority_map[request['priority']].append(request)

        except KeyError:
            priority_map[request['priority']] = [request]

    return priority_map


def getOrderedRequestList():
    """
    returns a list of requests sorted by priority
    """

    orderedRequestsList = []

    priority_map = getPriorityMap()

    for priority in sorted(six.iterkeys(priority_map), reverse=True):
        orderedRequestsList += priority_map[priority]
        #for request in priority_map[priority]:
        #    yield request
        # or if we want this to be a generator could it be more efficient
        # with itertools.chain?
        # foo=['abc','def','ghi']
        # [a for a in itertools.chain(*foo)]
        # ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
        # or [a for a in itertools.chain.from_iterable(foo)]

    return orderedRequestsList






def createBeamline(bl_name, bl_num):
    data = {"key": "beamline", "name": bl_name, "number": bl_num}
    uid = configuration_ref.create(beamline_id=BEAMLINE_ID, **data)
    return uid








def beamlineInfo(beamline_id, info_name, info_dict=None):
    """
    to write info:  beamlineInfo('x25', 'det', info_dict={'vendor':'adsc','model':'q315r'})
    to fetch info:  info = beamlineInfo('x25', 'det')
    """

    # if it exists it's a query or update
    try:
        bli = list(configuration_ref.find(key='beamline_info', beamline_id=beamline_id, info_name=info_name))[0]

        if info_dict is None:  # this is a query
            return bli['info']

        # else it's an update
        bli_uid = bli.pop('uid', '')
        configuration_ref.update({'uid': bli_uid},{'info':info_dict})

    # else it's a create
    except IndexError:
        # edge case for 1st create in fresh database
        # in which case this as actually a query
        if info_dict is None:
            return {}

        # normal create
        data = {'key': 'beamline_info', 'info_name':info_name, 'info': info_dict}
        uid = configuration_ref.create(**data)


def setBeamlineConfigParams(paramDict, searchParams):
    # get current config
    beamlineConfig = beamlineInfo(**searchParams)

    # update with given param dict and last_modified
    paramDict['last_modified'] = time.time()
    beamlineConfig.update(paramDict)

    # save  
    beamlineInfo(info_dict=beamlineConfig, **searchParams)

def getBeamlineConfigParam(paramName, searchParams):
    beamlineConfig = beamlineInfo(**searchParams)
    return beamlineConfig[paramName]

def getAllBeamlineConfigParams(searchParams):
    beamlineConfig = beamlineInfo(**searchParams)
    return beamlineConfig

