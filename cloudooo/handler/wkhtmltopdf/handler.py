##############################################################################
#
# Copyright (c) 2016 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is free software: you can Use, Study, Modify and Redistribute
# it under the terms of the GNU General Public License version 3, or (at your
# option) any later version, as published by the Free Software Foundation.
#
# You can also Link and Combine this program with other software covered by
# the terms of any of the Free Software licenses or any of the Open Source
# Initiative approved licenses and Convey the resulting work. Corresponding
# source of such a combination shall include the source code for all other
# software used.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See COPYING file for full licensing terms.
# See https://www.nexedi.com/licensing for rationale and options.
#
##############################################################################

from zope.interface import implements
from cloudooo.interfaces.handler import IHandler
from cloudooo.file import File
from cloudooo.util import logger
from subprocess import Popen, PIPE
from tempfile import mktemp, mkdtemp
from os.path import basename
from base64 import b64decode

def keyNameToOption(key_name, prefix=""):
  return "--" + prefix + key_name.replace("_", "-")

class Handler(object):
  """ImageMagic Handler is used to handler images."""

  implements(IHandler)

  def __init__(self, base_folder_url, data, source_format, **kw):
    """ Load pdf document """
    self.base_folder_url = base_folder_url
    self.file = File(base_folder_url, data, source_format)
    self.environment = kw.get("env", {})

  def makeTempFile(self, destination_format=None):
    path = mktemp(
      suffix='.%s' % destination_format,
      dir=self.file.directory_name,
    )
    return path

  def makeTempDir(self, *args, **kw):
    return mkdtemp(*args, dir=self.file.directory_name, **kw)

  def convertPathToUrl(self, path):
    if path.startswith("/"):
      return "file://" + path
    raise ValueError("path %r is not absolute" % path)

  def convert(self, destination_format=None, **kw):
    """Convert a image"""
    logger.debug("wkhtmltopdf convert: %s > %s" % (self.file.source_format, destination_format))
    output_path = self.makeTempFile(destination_format)
    command = self.makeWkhtmltopdfCommandList(
      self.convertPathToUrl(self.file.getUrl()),
      output_path,
      conversion_kw=kw,
    )
    stdout, stderr = Popen(
      command,
      stdout=PIPE,
      stderr=PIPE,
      close_fds=True,
      env=self.environment,
      cwd=self.file.directory_name,
    ).communicate()
    self.file.reload(output_path)
    try:
      return self.file.getContent()
    finally:
      self.file.trash()

  def getMetadata(self, base_document=False):
    """Returns a dictionary with all metadata of document.
    along with the metadata.
    """
    return NotImplementedError

  def setMetadata(self, metadata={}):
    """Returns image with new metadata.
    Keyword arguments:
    metadata -- expected an dictionary with metadata.
    """
    raise NotImplementedError

  @staticmethod
  def getAllowedConversionFormatList(source_mimetype):
    """Returns a list content_type and their titles which are supported
    by enabled handlers.

    [('application/pdf', 'PDF - Portable Document Format'),
     ...
    ]
    """
    return [("application/pdf", "PDF - Portable Document Format")]

  def makeSwitchOptionList(self, allowed_option_list, option_dict):
    """
      A switch option is enable if it exists.

      Ex: for         : --grayscale
          option_dict : {"grayscale": True}
          result      : ["--grayscale"]
    """
    option_list = []
    for option_name in allowed_option_list:
      value = option_dict.get(option_name)
      if value:
        option_list.append(keyNameToOption(option_name))
    return option_list

  def makeNoPrefixedOptionList(self, allowed_option_list, option_dict):
    """
      A "no" prefixed option is an option that if disable contains a
      "no" prefix.

      Ex: for         : --images (and --no-images)
          option_dict : {"images": False}
          result      : ["--no-images"]
    """
    option_list = []
    for option_name in allowed_option_list:
      value = option_dict.get(option_name)
      if value is not None:
        option_list.append(keyNameToOption(option_name, prefix="" if value else "no-"))
    return option_list

  def makeEnablePrefixedOptionList(self, allowed_option_list, option_dict):
    """
      An "enable" prefixed option is an option that if enable contains a
      "enable" prefix else contains a "disable" prefix.

      Ex: for         : --enable-external-links (and --disable-external-links)
          option_dict : {"enable_external_links": False}
          result      : ["--disable-external-links"]
    """
    option_list = []
    for option_name in allowed_option_list:
      value = option_dict.get(option_name)
      if value is not None:
        if value:
          option_list.append(keyNameToOption(option_name))
        else:
          option_list.append(keyNameToOption(option_name[7:], prefix="disable-"))
    return option_list

  def makeIncludeInPrefixedOptionList(self, allowed_option_list, option_dict):
    """
      An "include-in" prefixed option is an option that if enable contains a
      "include-in" prefix else contains a "exclude-from" prefix.

      Ex: for         : --include-in-outline (and --exclude-from-outline)
          option_dict : {"include_in_outline": False}
          result      : ["--exclude-from-outline"]
    """
    option_list = []
    for option_name in allowed_option_list:
      value = option_dict.get(option_name)
      if value is not None:
        if value:
          option_list.append(keyNameToOption(option_name))
        else:
          option_list.append(keyNameToOption(option_name[11:], prefix="exclude-from-"))
    return option_list

  def makeOneStringArgumentOptionList(self, allowed_option_list, option_dict):
    """
      A one-string-argument option is a option that require an argument
      which is a string.

      Ex: for         : --title <text>
          option_dict : {"title": "Hello World!"}
          result      : ["--title", "Hello World!"]
    """
    option_list = []
    for option_name in allowed_option_list:
      value = option_dict.get(option_name)
      if value is not None:
        option_list += [keyNameToOption(option_name), str(value)]
    return option_list

  def makeRepeatableOneStringArgumentOptionList(self, allowed_option_list, option_dict):
    """
      A repeatable one-string-argument option is a option that require one
      string argument, this option can be set several times.

      Ex: for         : --allow <path>
          option_dict : {"allow_list": ["a", "b"]}
          result      : ["--allow", "a", "--allow", "b"]
    """
    option_list = []
    for option_name in allowed_option_list:
      value_list = option_dict.get(option_name)
      if value_list:
        for value in value_list:
          option_list += [keyNameToOption(option_name[:-5]), str(value)]
    return option_list

  def makeRepeatableTwoStringArgumentOptionList(self, allowed_option_list, option_dict):
    """
      A repeatable two-string-argument option is a option that require two
      string arguments, this option can be set several times.

      Ex: for         : --cookie <name> <value>
          option_dict : {"cookie_list": [("a", "b"), ("c", "d")]}
          result      : ["--cookie", "a", "b", "--cookie", "c", "d"]
    """
    option_list = []
    for option_name in allowed_option_list:
      tuple_list = option_dict.get(option_name)
      if tuple_list:
        for name, value in tuple_list:
          option_list += [keyNameToOption(option_name[:-5]), str(name), str(value)]
    return option_list

  def makeDataUrlArgumentOptionList(self, allowed_option_list, option_dict,
                                    url_type="url", destination_format=None,
                                    use_switch=True):
    """
      A data-file-argument option is a option that require an url argument.

      Here, we don't want option value to be an url but data, so that
      we can put the data to a temp file an use it's url as option value.

      Ex: for         : --user-style-sheet <url> (and url_type="url")
          option_dict : {"user_style_sheet_data": b64encode("body { background-color: black; }")}
          result      : ["--user-style-sheet", "file:///tmp/tmp.XYZ.css"]

      Ex: for         : --checkbox-svg <path> (and url_type="path")
          option_dict : {"checkbox_svg_data": b64encode("<svg>....</svg>")}
          result      : ["--checkbox-svg", "/tmp/tmp.XYZ.svg"]

      Ex: for         : --xsl-style-sheet <file> (and url_type="file")
          option_dict : {"xsl_style_sheet_data": b64encode("table { border: none; }")}
          result      : ["--xsl-style-sheet", "tmp.XYZ.css"]
    """
    option_list = []
    for option_name in allowed_option_list:
      value = option_dict.get(option_name)
      if value is not None:
        # creates a tmp file in the directory which will be trashed
        path = self.makeTempFile(destination_format=destination_format)
        open(path, "wb").write(b64decode(value))
        if url_type == "url":
          path = self.convertPathToUrl(path)
        elif url_type == "file":
          path = basename(path)
        if use_switch:
          option_list += [keyNameToOption(option_name[:-5]), path]
        else:
          option_list.append(path)
    return option_list

  def makeDataPathArgumentOptionList(self, *args, **kw):
    return self.makeDataUrlArgumentOptionList(*args, url_type="path", **kw)

  def makeDataFileArgumentOptionList(self, *args, **kw):
    return self.makeDataUrlArgumentOptionList(*args, url_type="file", **kw)

  def makeRepeatableDataUrlArgumentOptionList(self, allowed_option_list,
                                              option_dict, **kw):
    option_list = []
    for option_name in allowed_option_list:
      data_list = option_dict.get(option_name)
      if data_list:
        for data in data_list:
          option_name = option_name[:-5]
          option_list += self.makeDataUrlArgumentOptionList([
            option_name,
          ], {option_name: data}, **kw)
    return option_list

  def makeWkhtmltopdfCommandList(self, *args, **kw):
    # http://wkhtmltopdf.org/usage/wkhtmltopdf.txt
    conversion_kw = kw.get("conversion_kw", {})
    command = ["wkhtmltopdf"]

    # Global Options
    command += self.makeNoPrefixedOptionList(["collate"], conversion_kw)
    command += self.makeSwitchOptionList([
      #"extended-help",
      "grayscale",
      #"help",
      #"htmldoc",
      #"licence",
      "lowquality",
      #"manpage",
      "no_pdf_compression",
      #"quiet",  # we decide
      #"read_args_from_stdin",  # only for several command line at a time
      #"readme",
      #"version",
    ], conversion_kw)
    command += self.makeOneStringArgumentOptionList([
      #"cookie_jar",  # no cookie jar
      "copies",
      "dpi",
      "image_dpi",
      "image_quality",
      "margin_bottom",
      "margin_left",
      "margin_right",
      "margin_top",
      "orientation",
      "page_height",
      "page_size",
      "page_width",
      "title",
    ], conversion_kw)

    # Outline Options
    command += self.makeNoPrefixedOptionList(["outline"], conversion_kw)
    #"dump_default_toc_xsl",
    command += self.makeOneStringArgumentOptionList([
      #"dump_outline",
      "outline_depth",
    ], conversion_kw)

    # Page Options
    command += self.makeNoPrefixedOptionList([
      "background",
      "custom_header_propagation",
      "images",
      "print_media_type",
      #"debug_javascript",  # we decide
      #"stop_slow_scripts",  # we decide
    ], conversion_kw)
    command += self.makeEnablePrefixedOptionList([
      "enable_external_links",
      "enable_forms",
      "enable_internal_links",
      "enable_javascript",
      #"enable_local_file_access",  # we decide
      #"enable_plugins",
      "enable_smart_shrinking",
      "enable_toc_back_links",
    ], conversion_kw)
    command += ["--disable-local-file-access"]
    command += self.makeIncludeInPrefixedOptionList([
      "include_in_outline",
    ], conversion_kw)
    command += self.makeSwitchOptionList(["default_header"], conversion_kw)
    # put cache in the temp dir - to disable cache
    command += ["--cache-dir", self.makeTempDir(prefix="cache")]
    command += self.makeOneStringArgumentOptionList([
      #"cache_dir",  # we decide
      "encoding",
      "javascript_delay",
      "load_error_handling",
      "load_media_error_handling",
      "minimum_font_size",
      "page_offset",
      #"password",  # too dangerous
      #"proxy",  # we decide
      #"username",  # too dangerous
      "viewport_size",
      "window_status",
      "zoom",
    ], conversion_kw)
    #"allow",  # we decide
    command += self.makeDataPathArgumentOptionList([
      # <option_name>_data
      "checkbox_checked_svg_data",
      "checkbox_svg_data",
      "radiobutton_checked_svg_data",
      "radiobutton_svg_data",
    ], conversion_kw, destination_format="svg")
    command += self.makeDataUrlArgumentOptionList([
      "user_style_sheet_data",
    ], conversion_kw, destination_format="css")
    #"run_script_list",  # too dangerous, fills --run-script
    command += self.makeRepeatableTwoStringArgumentOptionList([
      # <option_name>_list
      "cookie_list",
      "custom_header_list",
      #"post_list",
      #"post_file_list",
    ], conversion_kw)

    # Headers and Footer Options
    command += self.makeNoPrefixedOptionList([
      "footer_line",
      "header_line",
    ], conversion_kw)
    command += self.makeOneStringArgumentOptionList([
      "footer_center",
      "footer_font_name",
      "footer_font_size",
      "footer_left",
      "footer_right",
      "footer_spacing",
      "header_center",
      "header_font_name",
      "header_font_size",
      "header_left",
      "header_right",  # there's a --top option (not documented)
                       # may be we can do header_right_top option
      "header_spacing",
    ], conversion_kw)
    command += self.makeDataUrlArgumentOptionList([
      # <option_name>_data
      "footer_html_data",
      "header_html_data",
    ], conversion_kw, destination_format="html")
    command += self.makeRepeatableTwoStringArgumentOptionList([
      "replace",
    ], conversion_kw)

    # Custom Options
    command += self.makeRepeatableDataUrlArgumentOptionList([
      "before_toc_data_list",
    ], conversion_kw, destination_format="html", use_switch=False)

    # TOC Options
    value = conversion_kw.get("toc")
    if value:
      command += ["toc"]
      command += self.makeEnablePrefixedOptionList([
        "enable_dotted_lines",
        "enable_toc_links",
      ], conversion_kw)
      command += self.makeOneStringArgumentOptionList([
        "toc_header_text",
        "toc_level_indentation",
        "toc_text_size_shrink",
      ], conversion_kw)
      command += self.makeDataFileArgumentOptionList([
        "xsl_style_sheet_data",
      ], conversion_kw, destination_format="xsl")

    # Custom Options
    command += self.makeRepeatableDataUrlArgumentOptionList([
      "after_toc_data_list",
      "before_body_data_list",
    ], conversion_kw, destination_format="html", use_switch=False)
    command += args[:-1]  # input_url
    command += self.makeRepeatableDataUrlArgumentOptionList([
      "after_body_data_list",
    ], conversion_kw, destination_format="html", use_switch=False)
    command += args[-1:]  # output_path

    return command
