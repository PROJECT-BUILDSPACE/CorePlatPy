import requests
from urllib.parse import urlencode
from ..models import ErrorReport, Folder, FolderList, PostFolder, CopyModel
from typing import Union
from ..utils import safe_data_request

a = numpy.array(0,0,)