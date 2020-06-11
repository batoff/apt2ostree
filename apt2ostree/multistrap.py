from collections import namedtuple
from configparser import NoOptionError, SafeConfigParser

from .apt import AptSource


MultistrapConfig = namedtuple(
    "MultistrapConfig", "apt_sources packages")


def read_multistrap_config(ninja, config_file):
    p = SafeConfigParser()
    with ninja.open(config_file) as f:
        p.readfp(f)

    def get(section, field, default=None):
        try:
            return p.get(section, field)
        except NoOptionError:
            return default

    apt_sources = []
    packages = []
    for section in p.get("General", "aptsources").split():
        apt_sources.append(AptSource(
            architecture=get("General", "arch") or "amd64",
            distribution=get(section, "suite"),
            archive_url=get(section, "source"),
            components=get(section, "components"),
            keyring=get_keyring(get(section, "source"), get(section, "suite"))))
        packages += get(section, "packages", "").split()

    return MultistrapConfig(apt_sources, packages)


def get_keyring(archive_url, distribution):
    if 'ubuntu' in archive_url:
        return "$apt2ostreedir/xenial-keyring.gpg"


def multistrap(config_file, ninja, apt, unpack_only=False):
    cfg = read_multistrap_config(ninja, config_file)
    return apt.build_image("%s.lock" % config_file,
                           packages=cfg.packages,
                           apt_sources=cfg.apt_sources,
                           unpack_only=unpack_only)
