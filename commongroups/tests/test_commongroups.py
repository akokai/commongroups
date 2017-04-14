# -*- coding: utf-8 -*-

"""
Test suite for commongroups program architecture.

For tests of database query logic, stay tuned...

Depends:
    Home environment is configured; structure-searchable database exists and
    PostgreSQL is running; Google Sheets access is configured.

Side-effects:
    Creates directories and log files.
"""

# pylint: disable=invalid-name,missing-docstring

from itertools import islice
import json
import os
from os.path import exists, join as pjoin
from pkg_resources import resource_filename, resource_string

from pandas import DataFrame
import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.sql import Select

from commongroups.cmgroup import CMGroup
from commongroups.env import CommonEnv
from commongroups.errors import MissingParamError, NoCredentialsError
from commongroups.hypertext import directory
from commongroups.googlesheet import SheetManager
from commongroups.ops import (batch_process,
                              cmgs_from_file,
                              cmgs_from_googlesheet,
                              collect_to_json)
from commongroups.query import QueryMethod, get_query_results

PARAMS_JSON = resource_filename(__name__, 'params.json')
LOCAL_PARAMS = json.loads(resource_string(__name__, 'params.json').decode())
PAR_FAIL_QM = {'cmg_id': 'x666666', 'name': 'Incomplete parameters'}
TEST_LIMIT = 5

# Instantiate a few objects to run multiple tests on:
env = CommonEnv('test', google_worksheet='test')
env.connect_database()
blank_env = CommonEnv(env_path=env.results_path)


# Define a few generic helper functions for the tests.
def check_params(params):
    """
    Verify that group parameters read from file or Google Sheet are OK.

    The argument should be a params data structure for creating a single group,
    not a list of parameters for many group.
    """
    assert isinstance(params, dict)
    assert 'params' in params.keys()
    assert 'info' in params.keys()
    assert 'notes' in params['info'].keys()


def check_cmg(cmg):
    assert isinstance(cmg, CMGroup)
    assert isinstance(cmg.cmg_id, str)
    assert isinstance(cmg.params, dict)
    assert isinstance(cmg.info, dict)
    assert 'notes' in cmg.info
    cmg.add_info({'Added info': 'Success!'})
    assert 'Added info' in cmg.info


# Tests:
def test_env_config():
    assert env.config['google_worksheet'] == 'test'
    assert len(blank_env.config) == 0

    with pytest.raises(MissingParamError):
        blank_env.connect_database()
    with pytest.raises(MissingParamError):
        gen = cmgs_from_googlesheet(blank_env)


def test_env_db():
    env.connect_database()
    assert isinstance(env.database, Engine)


def test_cmgs_IO():
    for params in LOCAL_PARAMS:
        check_params(params)
    cmg_gen_json = cmgs_from_file(env, PARAMS_JSON)
    cmgs = list(islice(cmg_gen_json, None))
    assert len(cmgs) > 2
    for cmg in cmgs:
        check_cmg(cmg)
    coll_json_path = pjoin(env.results_path, 'cmgroups.json')
    collect_to_json(cmgs, env)
    assert exists(coll_json_path)
    html_dir_path = pjoin(env.results_path, 'html', 'index.html')
    directory(cmgs, env)
    assert exists(html_dir_path)


def test_googlesheet():
    with pytest.raises(NoCredentialsError):
        gsm = SheetManager('Untitled', 'Sheet 1', 'KEYFILE.DNE')

    sheet = SheetManager(env.config['google_sheet_title'],
                         env.config['google_worksheet'],
                         env.config['google_key_file'])
    google_params = list(islice(sheet.get_params(), None))
    for params in google_params:
        check_params(params)

    cmg_gen = cmgs_from_googlesheet(env)
    cmgs = list(islice(cmg_gen, None))
    assert len(cmgs) > 2
    for cmg in cmgs:
        check_cmg(cmg)

    path = pjoin(env.results_path, 'google_params.json')
    sheet.params_to_json(path)
    assert exists(path)


def test_querymethod():
    for params in [PAR_FAIL_QM, ]:
        with pytest.raises(MissingParamError):
            bad_qmd = QueryMethod(params)

    qmd = QueryMethod(LOCAL_PARAMS[0]['params'])
    assert isinstance(qmd.get_literal(), str)
    assert isinstance(qmd.expression, Select)
    qmd.expression = qmd.expression.limit(TEST_LIMIT)
    res = get_query_results(qmd.expression, env.database)
    assert isinstance(res, DataFrame)
    assert len(res) == TEST_LIMIT


def test_cmg_process():
    cmg = CMGroup(env, LOCAL_PARAMS[0]['params'], LOCAL_PARAMS[0]['info'])
    cmg.create_query()
    assert isinstance(cmg.query, QueryMethod)
    assert isinstance(cmg.query.get_literal(), str)
    assert isinstance(cmg.query.expression, Select)
    # Use the process() method
    cmg.process(env.database)
    assert isinstance(cmg.compounds, DataFrame)
    assert isinstance(cmg.info, dict)
    assert 'about' in cmg.info
    assert isinstance(cmg.info['count'], int)
    assert cmg.info['sql'] == cmg.query.get_literal()
    cmg.to_json()
    cmg.to_html(formats=['json'])


def test_batch_process():
    cmg_gen = cmgs_from_file(env, PARAMS_JSON)
    cmgs_done = batch_process(cmg_gen, env)
    for cmg in cmgs_done:
        check_cmg(cmg)
        assert exists(
            pjoin(cmg.results_path, '{}.json'.format(cmg.cmg_id))
        )
        assert exists(
            pjoin(cmg.results_path, '{}.xlsx'.format(cmg.cmg_id))
        )
        assert exists(
            pjoin(cmg.results_path, 'html', '{}.html'.format(cmg.cmg_id))
        )
    assert exists(pjoin(env.results_path, 'html', 'index.html'))
