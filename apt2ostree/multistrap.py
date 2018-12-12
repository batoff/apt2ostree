from collections import namedtuple
from configparser import NoOptionError, SafeConfigParser

from .apt import AptSource


MultistrapConfig = namedtuple(
    "MultistrapConfig", "apt_source packages")


def read_multistrap_config(config_file):
    p = SafeConfigParser()
    p.read(config_file)

    def get(section, field, default=None):
        try:
            return p.get(section, field)
        except NoOptionError:
            return default

    section = p.get("General", "aptsources").split()[0]

    apt_source = AptSource(
        architecture=get("General", "arch"),
        distribution=get(section, "suite"),
        archive_url=get(section, "source"),
        components=get(section, "components"))

    return MultistrapConfig(apt_source, get(section, "packages", "").split())


def multistrap(config_file, ninja, apt):
    cfg = read_multistrap_config(config_file)
    return apt.build_image("%s.lock" % config_file,
                           packages=cfg.packages,
                           apt_source=cfg.apt_source)