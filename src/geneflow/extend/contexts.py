"""This module contains the GeneFlow data and exec context mappings."""


class Contexts:
    """
    A class that contains GeneFlow context mappings.
    """

    # is data context option initialized by workflow class?
    mapping = {
        'local': {
            'alias': False,
            'exec': True,
            'data': True,
            'data_scheme': 'local'
        },
        'agave': {
            'alias': False,
            'exec': True,
            'data': True,
            'data_scheme': 'agave'
        },
        'gridengine': {
            'alias': False,
            'exec': True,
            'data': False,
            'data_scheme': 'local'
        },
        'http': {
            'alias': False,
            'exec': False,
            'data': True
        },
        'https': {
            'alias': 'http'
        },
        'tapis': {
            'alias': 'agave'
        }
    }
