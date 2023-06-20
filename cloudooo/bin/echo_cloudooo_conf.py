from os import path
import pkg_resources


def main():
  cloudooo_conf_path = pkg_resources.resource_filename("cloudooo",
                                    path.join("sample", "cloudooo.conf.in"))

  print(open(cloudooo_conf_path).read())
