# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2017, 2018.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Utilities for reading credentials from environment variables."""

import os
from collections import OrderedDict

from .credentials import Credentials

# Dictionary that maps `ENV_VARIABLE_NAME` to credential parameter.
VARIABLES_MAP = {
    'QE_TOKEN': 'token',
    'QE_URL': 'url',
    'QE_WEBSOCKET_URL': 'websocket_url',
    'QE_HUB': 'hub',
    'QE_GROUP': 'group',
    'QE_PROJECT': 'project'
}


def read_credentials_from_environ():
    """Read the environment variables and return its credentials.

    Returns:
        dict: dictionary with the credentials, in the form::

            {credentials_unique_id: Credentials}
    """
    # The token is the only required parameter.
    if not (os.getenv('QE_TOKEN') and os.getenv('QE_URL')):
        return OrderedDict()

    # Build the credentials based on environment variables.
    credentials = {}
    for envar_name, credential_key in VARIABLES_MAP.items():
        if os.getenv(envar_name):
            credentials[credential_key] = os.getenv(envar_name)

    credentials = Credentials(**credentials)
    return OrderedDict({credentials.unique_id(): credentials})
