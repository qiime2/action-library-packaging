from setuptools import setup, find_packages


setup(
    name='q2-nothing-to-see-here',
    version='0.0.0',
    packages=find_packages(),
    author='q2d2',
    author_email='q2d2.noreply@gmail.com',
    url='https://qiime2.org',
    license='BSD-3-Clause',
    description='GitHub Action Workflow Testing',
    entry_points={
        'qiime2.plugins':
        ['q2-nothing-to-see-here=q2_nothing_to_see_here:plugin'],
    },
    package_data={},
    zip_safe=False,
)
