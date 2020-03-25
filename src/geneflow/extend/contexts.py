"""This module contains the GeneFlow data and exec context mappings."""


class Contexts:
    """
    A class that contains GeneFlow context mappings.
    """

    # is data context option initialized by workflow class?
    mapping = {
        'local': {
            'exec': True,
            'data': True,
            'data_scheme': 'local'
        },
        'agave': {
            'exec': True,
            'data': True,
            'data_scheme': 'agave'
        },
        'gridengine': {
            'exec': True,
            'data': False,
            'data_scheme': 'local'
        },
        'tapis': {
            'alias': 'agave'
        }
    }

    @classmethod
    def is_exec_context(cls, context):
        """
        Determine if a context is an execution context.

        Args:
            cls: class object
            context: context to check

        Returns:
            True: context is in mapping dict and 'exec' is True.
            False: context is not in mapping dict, or 'exec' is False.

        """
        if context in cls.mapping:
            if 'alias' in cls.mapping[context]:
                return cls.is_exec_context(cls.mapping[context]['alias'])
            else:
                return cls.mapping[context]['exec']
        else:
            return False


    @classmethod
    def is_data_context(cls, context):
        """
        Determine if a context is a data context.

        Args:
            cls: class object
            context: context to check

        Returns:
            True: context is in mapping dict and 'data' is True.
            False: context is not in mapping dict, or 'data' is False.

        """
        if context in cls.mapping:
            if 'alias' in cls.mapping[context]:
                return cls.is_data_context(cls.mapping[context]['alias'])
            else:
                return cls.mapping[context]['data']
        else:
            return False


    @classmethod
    def get_data_scheme_of_exec_context(cls, context):
        """
        Return the data scheme for a execution context.

        Args:
            cls: class object
            context: context to check

        Returns:
            data scheme: if context is a valid execution context.
            False: context is not in mapping dict, or not an execution context.

        """
        if context in cls.mapping:
            if 'alias' in cls.mapping[context]:
                return cls.get_data_scheme_of_exec_context(cls.mapping[context]['alias'])
            else:
                if cls.mapping[context]['exec']:
                    return cls.mapping[context]['data_scheme']
                else:
                    return False
        else:
            return False
