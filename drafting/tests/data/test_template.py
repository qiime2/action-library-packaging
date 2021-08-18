# ----------------------------------------------------------------------------
# Copyright (c) 2016-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

# Testing the validate_params function
class TestValidateParams(unittest.TestCase):
    def test_qiime2_filepath_not_provided(self):
        pass

    def test_conda_filepath_not_provided(self):
        pass

    def test_conda_recipe_file_exists(self):
        pass

    def test_all_recipe_args_provided(self):
        pass

# Testing the _yaml_parsing function
class TestYamlParsing(unittest.TestCase):
    pass

# Testing the write_recipe function
class TestWriteRecipe(unittest.TestCase):
    def test_empty_qiime2_recipe(self):
        pass

    def test_qiime2_reqs_only(self):
        pass

    def test_all_reqs(self):
        pass

    def test_no_reqs(self):
        pass

    def test_imports_only(self):
        pass

    def test_imports_and_commands(self):
        pass

    def test_full_qiime2_recipe(self):
        pass
