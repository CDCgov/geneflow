"""This module contains the GeneFlow URIParser class."""

# import system modules
import re
# import custom modules
from geneflow.log import Log

class URIParser:
    r"""
    Light-weight URI parser adhering to part of RFC 3986.

    This URI parser is not comprehensive, but implements enough of the
    standard to recognize the following URI pattern:

    scheme://authority/path/to/name/..

    "scheme" and "authority" are optional. It will also extract the folder..
    and name from the path. For the above example, folder="/path/to",..
    and name="name". In addition, the final slash is removed.

    Based on a modified regex for URI parsing (RFC 3986):
    ^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?

    Assumptions
    1. No query strings in URI (indicated w/ ? or # characters)
    2. There is a slash (/) before the path (everything absolute)
    3. Only Unix style paths with forward slash (/)
    Examples:
        agave://system/path/
            scheme: agave
            authority: system
            path: /path/
            folder: /path
            name: path
        agave://system/path
            scheme: agave
            authority: system
            path: /path
            folder: /
            name: path
        local:/path
            scheme: local
            authority:
            path: /path
            folder: /
            name: path
        /path
            scheme: empty, but defaults to "local"
            authority:
            path: /path
            folder: /
            name: path

    """

    # regular expressions for parsing the URI
    uri_regex = "^(([^:/]+):)?(//([^/]*))?(.*?)$"
    path_regex = "^(.*?)(/?)([^/]+)?$"

    @classmethod
    def parse(cls, uri):
        """
        Parse a URI and return components. If the scheme is missing, it..

        defaults to "local".

        Args:
            uri: A generic URI string.

        Returns:
            On success: A dict that contains "uri", "scheme", "authority", and
            "path", etc:
                {
                    "uri": original URI
                    "chopped_uri": normalized URI
                    "scheme":
                    "authority":
                    "path": full path
                    "chopped_path": normalized path
                    "folder": folder part of path (to last slash, not including
                        last slash
                    "name": folder/file name, part of path after last slash
                }

            On failure: False.

        """
        matched = re.match(cls.uri_regex, str(uri))
        if not matched:
            Log.a().debug('invalid uri: %s', uri)
            return False

        # extract scheme, e.g., local, agave, http, etc.
        scheme = matched.group(2)
        if not scheme:
            scheme = 'local'

        # authority can be '' (e.g., server, or storage system)
        authority = matched.group(4) if matched.group(4) else ''
        path = matched.group(5) if matched.group(5) else '/'

        # replace one or more consecutive slashes with single slash
        path = re.sub('/+', '/', path)

        # get folder and name from path
        matched = re.match(cls.path_regex, path)
        if not matched:
            Log.a().debug('invalid path of uri: %s', path)
            return False

        folder = matched.group(1) if matched.group(1) else matched.group(2)
        name = matched.group(3) if matched.group(3) else ''

        # "normalized" path without extra slashes
        chopped_path = (
            folder+name if folder == '/' or folder == '' else folder+'/'+name
        ) if name else folder

        # "normalized" URI without extra slashes and with scheme
        chopped_uri = '{}{}{}'.format(
            '{}:'.format(scheme),
            ('//{}'.format(authority) if authority else ''),
            chopped_path
        )

        return {
            'uri': uri, # original URI
            'chopped_uri': chopped_uri,
            'scheme': scheme,
            'authority': authority,
            'path': path,
            'chopped_path': chopped_path,
            'folder': folder,
            'name': name
        }


    @classmethod
    def switch_context(cls, uri, new_base_uri):
        """
        Change the context of uri to the new_base.

        new_base can have a different scheme and base URL. If uri has no 'name'
        (e.g., ends with /), then the new context URI is identical to the
        normalized new_base_uri.

        Args:
            uri: URI to change context.
            new_base_uri: base URI of the new context.

        Returns:
            On success: parsed URI in new context.
            On failure: False.

        """
        # validate URIs
        parsed_uri = cls.parse(uri)
        if not parsed_uri:
            Log.a().debug('invalid uri: %s', uri)
            return False

        parsed_new_base_uri = cls.parse(new_base_uri)
        if not parsed_new_base_uri:
            Log.a().debug('invalid new base uri: %s', new_base_uri)
            return False

        # construct URI in new context
        new_uri = '{}:{}{}{}'.format(
            parsed_new_base_uri['scheme'],
            (
                '//{}'.format(
                    parsed_new_base_uri['authority']
                ) if parsed_new_base_uri['authority'] else ''
            ),
            parsed_new_base_uri['chopped_path'],
            (
                '{}' if parsed_new_base_uri['chopped_path'] == '/' else '/{}'
            ).format(parsed_uri['name'])
        )

        # parse the new URI to validate
        parsed_new_uri = cls.parse(new_uri)
        if not parsed_new_uri:
            Log.a().debug('invalid new uri: %s', new_uri)
            return False

        return parsed_new_uri
