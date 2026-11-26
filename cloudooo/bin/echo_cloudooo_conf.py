import importlib.resources
from os import fspath


def main():
  cloudooo_conf_path = fspath(
    importlib.resources.files("cloudooo").joinpath(
      "sample", "cloudooo.conf.in"))

  print(open(cloudooo_conf_path).read())
