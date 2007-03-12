import os, imp

from pida.core.interfaces import IService
from pida.core.plugins import Registry


class ServiceLoader(object):

    def get_all_services(self, service_dirs):
        for service_path in self._find_all_service_paths(service_dirs):
            module = self._load_service_module(service_path)
            if module is not None:
                service_class = self._load_service_class(module)
                if service_class is not None:
                    service_class.servicename = module.servicename
                    service_class.servicefile_path = module.servicefile_path
                    yield service_class

    def load_all_services(self, service_dirs, boss):
        for service_class in self.get_all_services(service_dirs):
            yield service_class(boss)

    def _find_service_paths(self, service_dir):
        for f in os.listdir(service_dir):
            service_path = os.path.join(service_dir, f)
            if self._has_servicefile(service_path):
                yield service_path

    def _find_all_service_paths(self, service_dirs):
        for service_dir in service_dirs:
            if os.path.isdir(service_dir):
                for service_path in self._find_service_paths(service_dir):
                    yield service_path

    def _get_servicefile_path(self, service_path, servicefile_name='service.pida'):
        return os.path.join(service_path, servicefile_name)

    def _has_servicefile(self, service_path):
        return os.path.exists(self._get_servicefile_path(service_path))

    def _load_service_module(self, service_path):
        name = os.path.basename(service_path)
        try:
            fp, pathname, description = imp.find_module(name, [service_path])
        except ImportError:
            return None
        module = imp.load_module(name, fp, pathname, description)
        module.servicename = name
        module.servicefile_path = self._get_servicefile_path(service_path)
        return module

    def _load_service_class(self, module):
        try:
            service = module.Service
        except AttributeError, e:
            return None
        service.servicemodule = module
        return service


class ServiceManager(object):

    def __init__(self, boss):
        self._boss = boss
        self._loader = ServiceLoader()
        self._reg = Registry()

    def load_services(self):
        for svc in self._loader.load_all_services(
                self._boss.get_service_dirs(), self._boss):
            self.register_service(svc)

    def register_service(self, service):
        self._reg.register_plugin(
            instance=service,
            singletons=(
                service.servicename,
            ),
            features=(
                IService,
            )
        )

    def get_service(self, name):
        return self._reg.get_singleton(name)

    def get_services(self):
        return self._reg.get_features(IService)

    



# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
