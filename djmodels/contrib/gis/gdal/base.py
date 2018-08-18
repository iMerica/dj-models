from djmodels.contrib.gis.gdal.error import GDALException
from djmodels.contrib.gis.ptr import CPointerBase


class GDALBase(CPointerBase):
    null_ptr_exception_class = GDALException
